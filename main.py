import json
import logging
import urlparse

import webapp2

from webapp2_extras import auth, sessions

from simpleauth import SimpleAuthHandler

from providers import NAME_FIELD_NAME, SCOPES, OPENID_IDENTITY_URLS

from config_NOCOMMIT import ROOT_DOMAIN, AUTH_DOMAIN, DEFAULT_REDIRECT, \
    PROVIDER_CONFIG, SECRET_KEY, OPENID_ENABLED


APP_CONFIG = {
  "webapp2_extras.sessions": {
    "cookie_name": "_auth_session",
    "secret_key": SECRET_KEY,
    "cookie_args": {
      "max_age": None,
      "domain": ".%s" % ROOT_DOMAIN,
      "path": "/",
      "secure": True,
      "httponly": True,
    },
  },
  "webapp2_extras.auth": {
    "cookie_name": "auth",
  },
}

def enable_cors(handler):
  if 'Origin' in handler.request.headers:
    origin = handler.request.headers['Origin']
    _, netloc, _, _, _, _ = urlparse.urlparse(origin)
    safe = False
    for root in set((ROOT_DOMAIN, "mayone.us", "mayday.us")):
      if netloc == root or netloc.endswith("." + root):
        safe = True
        break
    if not safe:
      logging.warning('Invalid origin: ' + origin)
      handler.error(403)
      return

    handler.response.headers.add_header("Access-Control-Allow-Origin", origin)
    handler.response.headers.add_header("Access-Control-Allow-Methods", "POST")
    handler.response.headers.add_header("Access-Control-Allow-Headers",
                                        "content-type, origin")
    handler.response.headers.add_header("Access-Control-Allow-Credentials",
                                        "true")

class SessionHandler(webapp2.RequestHandler):

  def dispatch(self):
    self.session_store = sessions.get_store(request=self.request)
    try:
      webapp2.RequestHandler.dispatch(self)
    except Exception:
      logging.exception("failed dispatching request")
      return self.redirect(self.safe_return_to() or DEFAULT_REDIRECT)
    finally:
      self.session_store.save_sessions(self.response)

  @webapp2.cached_property
  def session(self):
    return self.session_store.get_session()

  @webapp2.cached_property
  def auth(self):
      return auth.get_auth()

  @webapp2.cached_property
  def current_user(self):
    user_dict = self.auth.get_user_by_session()
    if user_dict is None:
      return None
    return self.auth.store.user_model.get_by_id(user_dict['user_id'])

  @property
  def logged_in(self):
    return self.current_user is not None

  def safe_return_to(self):
    return_to = self.request.get("return_to", "").encode("ascii")
    if not return_to:
      return None
    p = urlparse.urlparse(return_to)
    if p.netloc != ROOT_DOMAIN and not p.netloc.endswith(".%s" % ROOT_DOMAIN):
      return None
    if p.scheme != "https":
      return None
    return return_to


class AuthHandler(SessionHandler, SimpleAuthHandler):

  OAUTH2_CSRF_STATE = True

  def head(self, *args):
    # for twitter. twitter requires HEAD
    pass

  def _callback_uri_for(self, provider):
    return self.uri_for("auth_callback", provider=provider, _scheme="https",
                        _netloc=AUTH_DOMAIN)

  def _get_consumer_info_for(self, provider):
    key, secret = PROVIDER_CONFIG[provider]
    if provider in SCOPES:
      return key, secret, SCOPES[provider]
    return key, secret

  def _on_signin(self, data, auth_info, provider):
    target_loc = (self.session.pop("return_to") or "").encode("ascii")
    if not target_loc:
      target_loc = DEFAULT_REDIRECT
    if self.logged_in:
      # TODO: oh, we already have a user model logged in. hmm, we should
      # probably join these users. for now we're just going to ignore this log
      # in attempt
      self.redirect(target_loc)
      return

    auth_id = "%s:%s" % (provider, data["id"])

    # TODO: get more user data from each provider
    user_data = {"name": data[NAME_FIELD_NAME[provider]],
                 "provider": provider}

    user = self.auth.store.user_model.get_by_auth_id(auth_id)

    if user:
      user.populate(**user_data)
      user.put()
      self.auth.set_session(self.auth.store.user_to_dict(user))
      self.redirect(target_loc)
      return

    okay, user = self.auth.store.user_model.create_user(auth_id, **user_data)
    if not okay:
      # TODO: handle this error
      self.redirect(target_loc)
      return

    self.auth.set_session(self.auth.store.user_to_dict(user))
    self.redirect(target_loc)

  def _simple_auth(self, *args, **kwargs):
    if self.logged_in:
      self.redirect(self.safe_return_to() or DEFAULT_REDIRECT)
      return
    self.session["return_to"] = self.safe_return_to()
    return SimpleAuthHandler._simple_auth(self, *args, **kwargs)


class CurrentUserHandler(SessionHandler):
  def get(self):
    enable_cors(self)
    self.response.headers["Content-Type"] = "application/json"
    user = self.current_user
    if user is not None:
      self.response.write(json.dumps({
        "logged_in": True,
        "user": {
          "user_id": user.key.urlsafe(),
          "name": user.name,
          "provider": user.provider,
        }
      }))
    else:
      links, qargs = {}, {}
      return_to = self.safe_return_to()
      if return_to:
        qargs["return_to"] = return_to
      for provider in PROVIDER_CONFIG.keys():
        links[provider] = self.uri_for("auth_login", provider=provider,
                                       _scheme="https", _netloc=AUTH_DOMAIN,
                                       **qargs)
      if OPENID_ENABLED:
        for provider, url in OPENID_IDENTITY_URLS.iteritems():
          qargs_copy = qargs.copy()
          qargs_copy["identity_url"] = url
          links[provider] = self.uri_for("auth_login", provider="openid",
                                         _scheme="https", _netloc=AUTH_DOMAIN,
                                         **qargs_copy)
      self.response.write(json.dumps({
        "logged_in": False,
        "login_links": links,
      }))

  def options(self):
    enable_cors(self)


class LogoutHandler(SessionHandler):
  def get(self):
    self.auth.unset_session()
    self.redirect(self.safe_return_to() or DEFAULT_REDIRECT)


class RedirectHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect(DEFAULT_REDIRECT)


app = webapp2.WSGIApplication([
  webapp2.Route('/v1/current_user', handler=CurrentUserHandler,
                name='current_user'),
  webapp2.Route('/v1/logout', handler=LogoutHandler, name='logout'),
  webapp2.Route('/v1/auth/<provider>', handler=AuthHandler,
                handler_method='_simple_auth', name='auth_login'),
  webapp2.Route('/v1/_cb/<provider>', handler=AuthHandler,
                handler_method='_auth_callback', name='auth_callback'),
  webapp2.Route('/', handler=RedirectHandler),
], config=APP_CONFIG, debug=False)

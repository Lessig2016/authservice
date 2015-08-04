# provider specific information (along with what's in config_NOCOMMIT.py) goes
# here

NAME_FIELD_NAME = {
  "facebook": "name",
  "google": "name",
  "windows_live": "name",
  "twitter": "screen_name",
  "linkedin": "first-name",
  "linkedin2": "first-name",
  "foursquare": "firstName",
  "openid": "nickname",
}

SCOPES = {
  # if a SCOPE isn't provided, oauth1 behavior is assumed
  "google": "https://www.googleapis.com/auth/userinfo.profile",
  "linkedin2": "r_basicprofile",
  "facebook": "public_profile",
  "windows_live": "wl.signin",
  "foursquare": "authorization_code",
}

OPENID_IDENTITY_URLS = {
  "yahoo": "me.yahoo.com",
}

# authservice

Please see https://github.com/MayOneUS/wiki/wiki/My-SuperPAC-design-doc

## tl;dr

* **Applicable skills** TBD
* **Slack** [#gh-authservice](https://teamlessigtech.slack.com/messages/gh-authservice/)
* **Project lead** TBD

## Getting started

First, make sure the service is configured. You'll need to run

    cp config_NOCOMMIT_README config_NOCOMMIT.py

and then edit `config_NOCOMMIT.py` to contain some API keys and secrets.

This service must run over HTTPS on something that your computer's hostname
resolution thinks is `auth.mayday.us`. This is because we are using secure
cookies, which your browser requires pass over HTTPS for subdomains of
`mayday.us`.

The easiest way to get an HTTPS server running is to run

    docker pull jtolds/mayone-gae
    docker run -t -i -v /path/to/your/checkout:/develop jtolds/mayone-gae /start.sh /develop

(`start.sh` runs `dev_appserver.py` for you and sets up stunnel to wrap HTTPS
 traffic)

Run `docker ps` to find the container id of your running instance, then find
its IP address by running

    docker inspect -f "{{.NetworkSettings.IPAddress}}" container_id

Finally, add the container's IP and `auth.mayday.us` to your `/etc/hosts` file.

Another sample app that uses `auth.mayday.us` is checked in under the
`example/` subdir. Setting it up to use HTTPS is similar.

When testing, you can remove app auth here: https://www.facebook.com/settings?tab=applications

## Code of Conduct

The Lessig Equal Citizens Exploratory Committee is committed to fostering an open and inclusive community where engaged, dedicated volunteers can build the strategy and tools necessary to fix our country's democracy. All members of the community are expected to behave with civility, speak honestly and treat one another respectfully.

This project adheres to the [Open Code of Conduct](http://todogroup.org/opencodeofconduct/#Lessig2016/conduct@lessigforpresident.com). 
By participating, you are expected to honor this code.

This reference as well as the included copy of the [Code of Conduct](https://github.com/Lessig2016/authservice/blob/master/CONDUCT.md)
shall be included in all forks and distributions of this repository.

## Legal

The Lessig campaign is not responsible for the content posted to this repository, or for actions taken or liabilities incurred by one or more group members. 

You may not post content to the repository that you do not own, and by posting content you consent to its use by others, including the campaign. 

You are responsible for your compliance with federal campaign finance laws. You may not, for example, volunteer for the campaign if you are being paid by someone else to do so, or volunteer while at work unless it is limited to a few hours per month and your volunteering doesn’t create additional costs for your employer.

The campaign may remove any offensive, abusive, attacking, or discriminatory content, as well as any content that may otherwise violate our [Terms of Service](https://lessig2016.us/terms-of-service/). 

## Copyright and License

Copyright 2015 Lessig Equal Citizens Exploratory Committee. This 
project is released under [GNU Affero General Public License, version 3](https://github.com/Lessig2016/authservice/blob/master/LICENSE).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

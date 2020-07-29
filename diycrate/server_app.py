#!/usr/bin/env python3
import argparse
import configparser
import json
import logging
import os

import bottle
from bottle import ServerAdapter
from cheroot.wsgi import Server
from cheroot.ssl.builtin import BuiltinSSLAdapter

from diycrate.cache_utils import r_c
from diycrate.oauth_utils import setup_oauth, store_tokens_callback
from diycrate.log_utils import setup_logger


setup_logger()

crate_logger = logging.getLogger(__name__)


cloud_provider_name = 'Box'

bottle_app = bottle.Bottle()


# The watch manager stores the watches and provides operations on watches

# keep the lint-ing & introspection from complaining that these attributes don't exist before run-time.


@bottle_app.route('/auth_url')
def auth_url():
    """

    :return:
    """
    bottle_app.oauth = setup_oauth(r_c, conf_obj, store_tokens_callback)
    return json.dumps(bottle_app.oauth.get_authorization_url(redirect_url=bottle.request.query.redirect_url))


@bottle_app.route('/authenticate', method='POST')
def auth_url():
    """

    :return:
    """
    bottle_app.oauth = setup_oauth(r_c, conf_obj, store_tokens_callback)
    auth_code = bottle.request.POST.get('code')
    return json.dumps([el.decode(encoding='utf-8', errors='strict')
                       if isinstance(el, bytes) else el
                       for el in bottle_app.oauth.authenticate(auth_code=auth_code)])


@bottle_app.route('/new_access', method='POST')
def new_access():
    """
    Performs refresh of tokens and returns the result
    :return:
    """
    bottle_app.oauth = setup_oauth(r_c, conf_obj, store_tokens_callback)
    access_token_to_refresh = bottle.request.POST.get('access_token')
    refresh_token = bottle.request.POST.get('refresh_token')
    bottle_app.oauth._access_token = str(access_token_to_refresh)
    bottle_app.oauth._refresh_token = str(refresh_token)
    refresh_response = bottle_app.oauth.refresh(access_token_to_refresh)
    str_response = [el.decode(encoding='utf-8', errors='strict') if isinstance(el, bytes) else el
                    for el in refresh_response]
    return json.dumps(str_response)


# Create our own sub-class of Bottle's ServerAdapter
# so that we can specify SSL. Using just server='cherrypy'
# uses the default cherrypy server, which doesn't use SSL
class SSLCherryPyServer(ServerAdapter):
    """
    Custom server adapter using cherry-py with ssl
    """

    def run(self, server_handler):
        """
        Overrides super to setup Cherry py with ssl and start the server.
        :param server_handler: originating server type
        :type server_handler:
        """
        server = Server((self.host, self.port), server_handler)
        # Uses the following github page's recommendation for setting up the cert:
        # https://github.com/nickbabcock/bottle-ssl
        server.ssl_adapter = BuiltinSSLAdapter(conf_obj['ssl']['cacert_pem_path'],
                                               conf_obj['ssl']['privkey_pem_path'],
                                               conf_obj['ssl'].get('chain_pem_path'))
        try:
            server.start()
        finally:
            server.stop()


conf_obj = configparser.ConfigParser()


def main():
    global conf_obj

    conf_dir = os.path.abspath(os.path.expanduser('~/.config/diycrate_server'))
    if not os.path.isdir(conf_dir):
        os.mkdir(conf_dir)
    cloud_credentials_file_path = os.path.join(conf_dir, 'box.ini')
    if not os.path.isfile(cloud_credentials_file_path):
        open(cloud_credentials_file_path, 'w').write('')
    conf_obj.read(cloud_credentials_file_path)
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--client_id', type=str, help='Client ID provided by {}'.format(cloud_provider_name),
                            default='')
    arg_parser.add_argument('--client_secret', type=str,
                            help='Client Secret provided by {}'.format(cloud_provider_name), default='')
    arg_parser.add_argument('--cacert_pem_path', type=str, help='filepath to where the cacert.pem is located',
                            default='')
    arg_parser.add_argument('--privkey_pem_path', type=str, help='filepath to where the privkey.pem is located',
                            default='')
    arg_parser.add_argument('--chain_pem_path', type=str, help='filepath to where the chain.pem is located',
                            default='')
    args = arg_parser.parse_args()
    try:
        prev_chain_pem_path = conf_obj['ssl']['chain_pem_path']
    except Exception:
        prev_chain_pem_path = None
    had_oauth2 = conf_obj.has_section('oauth2')
    if not had_oauth2:
        conf_obj.add_section('oauth2')
    conf_obj['oauth2'] = {
        'client_id': args.client_id or conf_obj['oauth2']['client_id'],
        'client_secret': args.client_secret or conf_obj['oauth2']['client_secret']
    }
    if 'ssl' not in conf_obj:
        if not args.cacert_pem_path:
            raise ValueError('Need a valid cacert_pem_path')
        if not args.privkey_pem_path:
            raise ValueError('Need a valid privkey_pem_path')
        conf_obj['ssl'] = {
            'cacert_pem_path': os.path.abspath(os.path.expanduser(args.cacert_pem_path)),
            'privkey_pem_path': os.path.abspath(os.path.expanduser(args.privkey_pem_path)),
        }
        if args.chain_pem_path:
            conf_obj['ssl']['chain_pem_path'] = os.path.abspath(os.path.expanduser(args.chain_pem_path))

    conf_obj['ssl'] = {
        'cacert_pem_path': os.path.abspath(os.path.expanduser(args.cacert_pem_path)) if args.cacert_pem_path else
        conf_obj['ssl']['cacert_pem_path'],
        'privkey_pem_path': os.path.abspath(os.path.expanduser(args.privkey_pem_path)) if args.privkey_pem_path else
        conf_obj['ssl']['privkey_pem_path'],
    }
    if args.chain_pem_path or prev_chain_pem_path:
        conf_obj['ssl']['chain_pem_path'] = prev_chain_pem_path or os.path.abspath(os.path.expanduser(args.chain_pem_path))

    conf_obj.write(open(cloud_credentials_file_path, 'w'))
    bottle_app.run(server=SSLCherryPyServer, port=8081, host='0.0.0.0')


if __name__ == '__main__':
    main()
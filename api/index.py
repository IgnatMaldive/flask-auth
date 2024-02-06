#!/usr/bin/env python3
"""
A Flask app for Google SSO
"""

import json
import os
import requests
from flask import Flask, redirect, request
from oauthlib import oauth2
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

DATA = {
        'response_type':"code", # this tells the auth server that we are invoking authorization workflow
        'redirect_uri':"https://www.flask-auth-seven.vercel.app/login/callback", # redirect URI https://console.developers.google.com/apis/credentials
        'scope': 'https://www.googleapis.com/auth/userinfo.email', # resource we are trying to access through Google API
        'client_id':CLIENT_ID, # client ID from https://console.developers.google.com/apis/credentials
        'prompt':'consent'} # adds a consent screen

URL_DICT = {
        'google_oauth' : 'https://accounts.google.com/o/oauth2/v2/auth', # Google OAuth URI
        'token_gen' : 'https://oauth2.googleapis.com/token', # URI to generate token to access Google API
        'get_user_info' : 'https://www.googleapis.com/oauth2/v3/userinfo' # URI to get the user info
        }

# Create a Sign in URI
CLIENT = oauth2.WebApplicationClient(CLIENT_ID)
REQ_URI = CLIENT.prepare_request_uri(
    uri=URL_DICT['google_oauth'],
    redirect_uri=DATA['redirect_uri'],
    scope=DATA['scope'],
    prompt=DATA['prompt'])

app = Flask(__name__)

@app.route('/manola')
def manola():
    return 'manola'
        
@app.route('/')
def login():
    "Home"
    # redirect to the newly created Sign-In URI
    return redirect(REQ_URI)

@app.route('/home')
def home():
    "Redirect after Google login & consent"

    # Get the code after authenticating from the URL
    code = request.args.get('code')

    # Generate URL to generate token
    token_url, headers, body = CLIENT.prepare_token_request(
            URL_DICT['token_gen'],
            authorisation_response=request.url,
            # request.base_url is same as DATA['redirect_uri']
            redirect_url=request.base_url,
            code=code)

    # Generate token to access Google API
    token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(CLIENT_ID, CLIENT_SECRET))

    # Parse the token response
    CLIENT.parse_request_body_response(json.dumps(token_response.json()))

    # Add token to the  Google endpoint to get the user info
    # oauthlib uses the token parsed in the previous step
    uri, headers, body = CLIENT.add_token(URL_DICT['get_user_info'])

    # Get the user info
    response_user_info = requests.get(uri, headers=headers, data=body)
    info = response_user_info.json()

    return redirect('/user/%s' % info['email'])

@app.route('/user/<email>')
def login_success(email):
    "Landing page after successful login"

    return "Hello %s" % email

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')

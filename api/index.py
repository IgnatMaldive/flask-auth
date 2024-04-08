from flask import Flask, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email'},
    google_redirect_uri = 'http://127.0.0.1:5000/authorize',
)


@app.route('/')
def index():
    user_info = session.get('user_info')
    if user_info:
        # Assuming 'emal' is the key for the user's name in the response.
        # Adjust the key if the structure of user_info is different.
        user_name = user_info.get('email', 'Guest')  # Fallback to 'Guest' if name is not found
        welcome_message = f'Welcome, {user_name}!'
        return welcome_message
    return 'Hello! <a href="/login">Log in with Google</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    # Store the user information in session
    session['user_info'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
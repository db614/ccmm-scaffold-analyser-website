from flask import current_app, redirect, request, url_for, session
from flask_login import login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import hashlib
import os

from ccmmdb.core.db import db
from ccmmdb.blueprints.auth import bp
from ccmmdb.models.models import User


def get_google_provider_cfg():
    r = requests.get(current_app.config['GOOGLE_DISCOVERY_URL'])
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return 'An unexpected error occurred, please inform the administrator', 500


@bp.route('/login', methods=['GET'])
def login():
    # Find out what URL to hit for Google login, then add request parameter to force Raven login page
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"] + '?hd=cam.ac.uk'

    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

    # Generate state parameter and store it in the server-side session
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    session['state'] = state

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        state=state,
        prompt = "select_account consent"
    )
    return redirect(request_uri)


@bp.route('/login/callback')
def callback():
    # Check that the anti-forgery state token response is correct
    if request.args.get('state', '') != session['state']:
        return 'Invalid state parameter. Please contact an admin', 401

    # Get authorization code Google sent back to you
    code = request.args.get("code")

    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have token, find and hit the endpoint
    # from Google that gives you the user's profile information
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Check that the authorisation comes from the right organisation
    # then extract the crsid from the returned data, and a name for if we want to display later
    if userinfo_response.json()["hd"] == 'cam.ac.uk':
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["name"]
        # Check that they have a valid cam.ac.uk email before attempting to get crsid
        # This also acts as a check for current student status
        if users_email.split('@')[1] == 'cam.ac.uk':
            crsid = users_email.split('@')[0]
        else:
            return "You do not have permission to access this website", 400
    else:
        return "You do not have permission to access this website", 400

    # Check to see if the crsid is in the list of allowed crsid's from the config file
    if crsid not in current_app.config['CCMM_MEMBERS']:
        return "You do not have permission to access this website", 400

    # Create a user with the information provided.
    user = User(id=unique_id, crsid=crsid)

    # If the user doesn't exist already then add it to the database.
    if User.query.filter_by(id=unique_id).first() is None:
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for('main.index'))

'''
@bp.route('/revoke-access')
@login_required
def revoke_access():
    logout_user()
    # Delete Flask-Login's session cookies
    [session.pop(key) for key in list(session.keys())]
    session.clear()
    return redirect(url_for('main.index'))

@bp.route('/revoke-access')
'''
@bp.route('/revoke_access', methods=['GET'])
@login_required
def revoke_access():
    # Find out what URL to hit for Google login, then add request parameter to force Raven login page
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"] + '?hd=cam.ac.uk'

    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

    # Generate state parameter and store it in the server-side session
    state = session['state']

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/revoke_callback",
        scope=["openid", "email", "profile"],
        state=state,
    )
    return redirect(request_uri)

@bp.route('/revoke_access/revoke_callback')
def revoke_callback():
    # Check that the anti-forgery state token response is correct
    if request.args.get('state', '') != session['state']:
        return 'Invalid state parameter. Please contact an admin', 401

    # Get authorization code Google sent back to you
    code = request.args.get("code")

    client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have token, find and hit the endpoint
    # from Google that gives you the user's profile information
    revocation_endpoint = google_provider_cfg["revocation_endpoint"]
    revocation_response = requests.post(revocation_endpoint,
                  params={'token': client.token['access_token']},
                  headers={'content-type': 'application/x-www-form-urlencoded'})
    if revocation_response.status_code == requests.codes.ok:
        # Send user back to homepage
        logout_user()
        session.clear()
        [session.pop(key) for key in list(session.keys())]
        return redirect(url_for('main.index'))
    else:
        return "Logout was not possible, please try again or contact an administrator", 500



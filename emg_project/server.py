# oauth_server.py

import os
import urllib.parse
from flask import Flask, request, redirect, jsonify
import requests
from config import EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_RU_NAME, EBAY_SCOPES
from config import OAUTH_RENDER_URL ###### some of these can be altered (getting rid of config)
from ebay_client import save_tokens, load_tokens, is_token_expired  # CHANGE: added is_token_expired import
TOKEN_FILE = "ebay_tokens.json"
EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
EBAY_SCOPES = "https://api.ebay.com/oauth/api_scope/sell.communication"
















flask_app = Flask()

                        #possible change name
@flask_app.route("/start")
def start_oauth():
    redirect_uri = OAUTH_RENDER_URL

    auth_url = {
        "client_id": EBAY_CLIENT_ID,        #convert these to lowercase
        "response_type": "code",            # manual harcode these if possible...
        # authorization code, not token
        "redirect_uri": redirect_uri,
        "scope": EBAY_SCOPES,
    }

    query = ""
    for key, value in auth_url.items():
        query += f"{key}={value}&"

    query = query.rstrip("&")

    auth_url = f"{EBAY_AUTH_URL}?{query}"

    return redirect(auth_url)


@flask_app.route("/callback")
def callback():
    code = request.args.get("code")
    
    if not code:
        return "Missing authorization code", 400
        # api redirect requires subsquent browser get request
        # return values sent in responce to browser...

    redirect_uri = OAUTH_RENDER_URL

    responce = requests.post(                            ###responce progject name change
        EBAY_TOKEN_URL,
        headers = {"Content-Type": "application/x-www-form-urlencoded"},
        # Ebay api does not expect json, but `form` key/value pairs...
        auth = (EBAY_CLIENT_ID, EBAY_CLIENT_SECRET), # Basic/base64...
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
    )

    if responce.status_code != 200:
        return f"Failed to exchange token: {responce.text}", 400 ###change text

    save_tokens(responce.json())
    
    return "Authorization complete! You can close this page."


@flask_app.route("/refresh")
def refresh():

    token_data = load_tokens()

    if token_data is None:
        return "No token data found", 400             ## check these two check arent covered by the load token method
                                                      ## they might not be needed
    if "refresh_token" not in token_data:
        return "No refresh token available", 400

    responce = requests.post(

        EBAY_TOKEN_URL,

        headers={"Content-Type": "application/x-www-form-urlencoded"},

        auth=(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET),

        data={
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"],
            "scope": EBAY_SCOPES
        }
    )

    if responce.status_code != 200:
        return f"Refresh failed: {responce.text}", 400

    new_data = responce.json()

    save_tokens(new_data)

    return jsonify(new_data)
    # http responce object...


@flask_app.route("/health")
def health():
    
    return "OK", 200


# ============================================================
# NEW: /get-token endpoint.
# The desktop app polls this after opening the browser for OAuth.
# Returns {"status": "pending"} (202) while waiting, or
# {"status": "ready", "access_token": ..., ...} (200) once the
# /callback route has saved a valid token.
# ============================================================
@flask_app.route("/get-token")
def get_token():
    token_data = load_tokens()

    if token_data is None:
        return "", 202

    # Accepted bot ready yet, expected by render
    if is_token_expired(token_data):
        return "", 202

    # In the case eligible tokens
    return jsonify({
        "access_token": token_data.get("access_token"),
        "expires_in": token_data.get("expires_in", 0),
        "received_at": token_data.get("received_at", 0)
    })


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    flask_app.run(host = "0.0.0.0", port = port)
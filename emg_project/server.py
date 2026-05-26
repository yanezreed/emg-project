# from config import client_id, client_secret, api_scope, render_ulr
from ebay_client import save_tokens, load_tokens, is_token_expired

from ebay_client import get_conversations

from flask import Flask, request, redirect
from urllib.parse import urlencode
import requests
import os

test_token = {}

client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")
api_scope = os.environ.get("api_scope")
render_ulr = os.environ.get("render_ulr")

flask_app = Flask(__name__)

@flask_app.route("/start")
def start_oauth():

    data = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": render_ulr,
        "scope": api_scope,
    }

    query = ""
    for key, value in data.items():
        query += f"{key}={value}&"

    query = query.rstrip("&")
    # builds str query, redirecting user to OAuth page
    # once complete, code sent via url to callback url
    # ie. the method below...

    created_url = f"{"https://auth.ebay.com/oauth2/authorize"}?{query}"

    return redirect(created_url)


@flask_app.route("/callback")
def callback():
    code = request.args.get("code")
    # flasks object `request.args` allows access to query parameters from incoming uri
    if not code:
        return "Missing authorization code within the url", 400

    code_responce = requests.post(
        url = "https://api.ebay.com/identity/v1/oauth2/token", # parameter must be url
        headers = {"Content-Type": "application/x-www-form-urlencoded"},
        auth = (client_id, client_secret),
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": render_ulr,
        }
    )

    if code_responce.status_code != 200:
        return f"Failed to exchange token: {code_responce.text}", 400

    #save_tokens(code_responce.json())
    # json data saved as pythonic dict

    global test_token
    test_token.update(code_responce.json())
    # `update` adds key and value pairs to my existing dict

    return "<h1>Authorization complete!</h1><p>You can close this page.</p>"


@flask_app.route("/health")
def health():
    return "OK", 200


@flask_app.route("/check-token")
def get_token():
    token_data = load_tokens()

    if token_data is None:
        return "No token data found saved", 202

    if is_token_expired(token_data):
        return "Token saved, is expired", 202
    
    return {
        "access_token": token_data.get("access_token"),
        "expires_in": token_data.get("expires_in", 0),
        "received_at": token_data.get("received_at", 0)
    } # flask automatically converts dict into http responce

@flask_app.route("/conversations")
def conversations():
    access_token = test_token.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    api_response = requests.get(
        url = "https://api.ebay.com/sell/messaging/v1/conversation",
        headers = headers,
        params = {"limit": 75, "sort": "date_desc"},
        timeout = 20
    )
    
    return api_response.json()

@flask_app.route("/check-test-tokenn")
def check_test_token():
    return test_token


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host = "0.0.0.0", port = port)

# render auto sets port when hosting application
# `8080` is a backup default...
# `0.0.0.0` allows server to listen for all avalbale network interfaces...
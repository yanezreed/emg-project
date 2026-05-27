from ebay_client import save_tokens, load_tokens, is_token_expired
from flask import Flask, request, redirect
import requests
import os

client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")
api_scope = os.environ.get("api_scope")
render_ulr = os.environ.get("render_ulr")

# note: my `api_scope` enviromental variable, on render, must be percent encoded
# as the scope itself is a url passed within the users url as a parameter
# meaning colons must be %3A and forward slashes must be %2F...

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

    save_tokens(code_responce.json())
    # json data saved as pythonic dict

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
    } 
    # flask will auto converts dict into https responce


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host = "0.0.0.0", port = port)

# render auto sets port when hosting application
# `8080` is a backup default...
# `0.0.0.0` allows server to listen for all avalbale network interfaces...
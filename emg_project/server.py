from ebay_client import save_tokens, load_tokens, token_expired_check
from flask import Flask, request, redirect
import requests
import os

client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")
api_scope = os.environ.get("api_scope")
render_callback = os.environ.get("render_callback")

# note: my `api_scope` enviromental variable, on render, must be percent encoded
# as the scope itself is a url passed within the users url as a parameter
# meaning colons must be %3A and forward slashes must be %2F...

flask_app = Flask(__name__)

@flask_app.route("/start")
def start_oauth():
    data = {"client_id": client_id, "response_type": "code", "redirect_uri": render_callback, "scope": api_scope}
    
    built_query = ""
    for key, value in data.items():
        built_query += f"{key}={value}&"
    built_query = built_query.rstrip("&")

    # builds string query, redirecting user to OAuth page
    # once complete, code sent via url to callback url
    # ie. the method below...

    created_url = f"{"https://auth.ebay.com/oauth2/authorize"}?{built_query}"

    return redirect(created_url)

@flask_app.route("/callback")
def callback():
    auth_code = request.args.get("code")
    # flasks global object `request.args` allows access to query parameters from incoming url...

    if auth_code == None:
        return "Missing authorization code within the url", 400

    exhanging_token_responce = requests.post(
        url = "https://api.ebay.com/identity/v1/oauth2/token",
        headers = {"Content-Type": "application/x-www-form-urlencoded"},
        auth = (client_id, client_secret),
        data = {"grant_type": "authorization_code", "code": auth_code, "redirect_uri": render_callback}
    )

    if exhanging_token_responce.status_code != 200:
        return f"Failed to exchange token: {exhanging_token_responce.text}", 400

    save_tokens(exhanging_token_responce.json())
    # json data must be encoded as a python dict

    return '<h1>Authorization completed</h1>' + '<h2>You may now close this webpage.</h2>'

@flask_app.route("/check_token")
def get_token():
    token_data =  load_tokens()

    if token_data == None:
        return "No token data found saved", 202

    if token_expired_check(token_data):
        return "Token saved, is expired", 202
    
    return {
        "access_token": token_data["access_token"],
        "expires_in": token_data["expires_in"],
        "received_at": token_data["received_at"]
    }
    # flask auto converts dict into https responce

if __name__ == "__main__":
    os_port = os.environ['PORT']
    port = int(os_port)

    flask_app.run(host = "0.0.0.0", port = port)
# render auto sets port when hosting application
# `0.0.0.0` allows server to listen for all avalbale network interfaces...
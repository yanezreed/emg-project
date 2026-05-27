from time import time
import requests
import json
import os

client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")

def load_tokens():
    try:
        with open("ebay_tokens.json", "r") as file:
            return json.load(file)
            # output `dict object`
    except FileNotFoundError:
        return None

def save_tokens(token_data):
    token_data["received_at"] = int(time())

    with open("ebay_tokens.json", "w") as file:
        json.dump(token_data, file)
        # writes json data to local

        # used on render server via `/callback` saving token data after OAuth
        # being used on the flask server in addition to within my application

def is_token_expired(token_data):
    if not token_data:
        return True
    
    expires_in = token_data.get("expires_in", 0)
    received_at = token_data.get("received_at", 0)
    
    expiry_time = received_at + (expires_in - 30)
    time_now = int(time())

    return time_now > expiry_time


def refresh_access_token():
    token_data = load_tokens()

    if token_data == None or "refresh_token" not in token_data:
        raise RuntimeError("Token data is invalid.")
    
    ebay_api_url = "https://api.ebay.com/identity/v1/oauth2/token"

    content_type = {"Content-Type": "application/x-www-form-urlencoded"}
    # noting that the payload is formatted as a form ie. key/value pairs

    authorization = (client_id, client_secret)
    # `requests` formats the strings to base64
    # `Authorization: Basic <base64string>`

    request_body = {
        "grant_type": "refresh_token", 
        "refresh_token": token_data["refresh_token"],

        "scope": "https://api.ebay.com/oauth/api_scope/commerce.message"
    }

    api_response = requests.post(
        url = ebay_api_url,
        headers = content_type,
        auth = authorization,
        data = request_body,
        timeout = 20
    )

    if api_response.status_code != 200:
        raise RuntimeError("Error when gaining access token.")

    token_data = api_response.json()

    save_tokens(token_data)

    return token_data["access_token"]


def ensure_valid_token():
    token_data = load_tokens()

    if token_data == None:
        return refresh_access_token()

    if is_token_expired(token_data):
        return refresh_access_token()

    return token_data["access_token"]


def get_auth_header():
    access_token = ensure_valid_token()

    if access_token == None:
        raise RuntimeError("Could not obtain an access token.")
    
    return {"Authorization": f"Bearer {access_token}"}
    # formatted header expected by api each request...


def get_conversations():
    url = "https://api.ebay.com/commerce/message/v1/conversation"

    formatted_access_token = get_auth_header()

    conversations_limit = {"limit": 35, "conversation_type": "FROM_MEMBERS"}

    api_response = requests.get(
        url = url,
        headers = formatted_access_token,
        params = conversations_limit,
        timeout = 20
    )

    if api_response.status_code == 200:
        return api_response.json().get("conversations", [])
    
    # conversations is a list of dicts...
    # including; conversationId, conversationStatus, conversationType,
    # createdDate, referenceId, unreadCount, latestMessage

    raise RuntimeError(
        f"Error when getting conversations: {api_response.status_code}/{api_response.text}")


def get_conversation_messages(conversation_id):
    url = f"https://api.ebay.com/commerce/message/v1/conversation/{conversation_id}"
    formatted_access_token = get_auth_header()

    api_response = requests.get(
        url = url,
        headers = formatted_access_token,
        params = {"conversation_type": "FROM_MEMBERS"},
        timeout = 20
    )

    if api_response.status_code == 200:
        return api_response.json().get("messages", [])

    raise RuntimeError(f"Error when getting messages: {api_response.status_code}/{api_response.text}")


def send_message(conversation_id, message_text):
    url = f"https://api.ebay.com/sell/messaging/v1/conversation/{conversation_id}/message"

    json_message = {"messageText": message_text}

    headers = get_auth_header()
    headers["Content-Type"] = "application/json"
    # Adds "Content-Type" key/value pair to access token...

    api_response = requests.post(
        url = url,
        headers = headers,
        json = json_message,
        timeout = 15
    )

    if api_response.status_code == 200 or api_response.status_code == 201:
        return True # covers possible multiple resources sent to api (201)

    raise RuntimeError(
        f"Could not send message(s): {api_response.status_code}/{api_response.text}")
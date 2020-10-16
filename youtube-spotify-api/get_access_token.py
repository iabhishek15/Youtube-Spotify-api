import requests
from key import spotify_app_client_secret_id, spotify_client_id
import base64

def get_user_token():
    endpoint = "https://accounts.spotify.com/api/token"
    client_creds = f"{spotify_client_id}:{spotify_app_client_secret_id}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    token_data = {
        "grant_type": "client_credentials",
    }
    token_headers = {
        "Authorization": f"Basic {client_creds_b64.decode()}"  # <base64 encoded client_id:client_secret>
    }
    response = requests.post(endpoint, data = token_data, headers = token_headers).json()
    user_token = response["access_token"]
    print(response)
    return user_token

my_user_token = get_user_token()
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def getAccessToken():
    # Set up the OAuth2 client
    sp_oauth = SpotifyOAuth(client_id= 'YOUR_CLIENT_ID',
                            client_secret= 'YOUR_CLIENT_SECRET_ID',
                            redirect_uri="REDIRECT_URI",
                            scope=["playlist-modify-private,playlist-modify-public",'user-top-read','user-library-read'])

    # Get the access token
    access_token = spotipy.util.prompt_for_user_token(username="YOUR_USERNAME", 
                                                    oauth_manager=sp_oauth)
    return access_token
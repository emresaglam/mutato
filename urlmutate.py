import tidalapi
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

tidal_access_token=os.getenv('TIDAL_ACCESS_TOKEN')
tidal_session_id=os.getenv('TIDAL_SESSION_ID')
tidal_token_type=os.getenv('TIDAL_TOKEN_TYPE')
spotify_client_id=os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')


def get_tidal_album_id(url):
    o = urlparse(tidal_url)
    if o.netloc != "tidal.com":
        raise Exception("Sorry this domain is not a Tidal domain: {}".format(o.netloc))
    else:
        tidal_album_id = o.path.split("/")[2]

    return tidal_album_id


tidal_url="https://tidal.com/album/35614665"
tidal_album_id=get_tidal_album_id(tidal_url)

#print(tidal_album_id)

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_client_id,
                                                                              client_secret=spotify_client_secret))
session = tidalapi.Session()
session.load_oauth_session(session_id=tidal_session_id, access_token=tidal_access_token, token_type=tidal_token_type)
tidal_album = session.get_album(tidal_album_id)

print("{}, {}, {}, {}".format(tidal_album.artist.name, tidal_album.name, tidal_album.release_date, tidal_url))

results = spotify.search(q='artist:' + tidal_album.artist.name + ' album:'
                         + tidal_album.name , type='artist,album')
#print(json.dumps(results))
print(results["albums"]["items"][0]["artists"][0]["name"],
      results["albums"]["items"][0]["name"], results["albums"]["items"][0]["release_date"],
      results["albums"]["items"][0]["external_urls"]["spotify"])
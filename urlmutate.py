from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
import requests
import tidalapi
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse
import os
from dotenv import load_dotenv


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
                                                                    "\n"
                                                                    "Some commands you can use:\n"
                                                                    "/kitty\n"
                                                                    "/start\n"
                                                                    "Secret command: /oktay\n"
                                                                    "/mutato <ALBUM URL> "
                                                                    "(example: /mutato https://tidal.com/browse/album/131029033)")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def shut_up(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Shut up Oktay")


def grab_a_kitten(update, context):
    catapi_token = "CATAPI_TOKEN"
    CATAPITOKEN = os.getenv(catapi_token)
    if CATAPITOKEN is None:
        print("EEK! Define CATAPITOKEN first. 😹")
    fn = "/tmp/kitty.jpg"
    kittyurl = "https://api.thecatapi.com/v1/images/search?limit=1&page=10&order=random"
    r = requests.get(kittyurl)
    kittypicurl=r.json()[0]["url"]
    headers = {"x-api-key": CATAPITOKEN}
    r = requests.get(kittypicurl, headers=headers)
    f = open(fn, "wb")
    r.raw.decode_content = True
    for chunk in r:
        f.write(chunk)
    f.close()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(fn, 'rb'))
    os.remove(fn)


def get_tidal_album_id(tidal_url):
    o = urlparse(tidal_url)
    if o.netloc != "tidal.com":
        raise Exception("Sorry this domain is not a Tidal domain: {}".format(o.netloc))
    else:
        tidal_album_id = o.path.split("/")[-1]

    return tidal_album_id


def tidal2spotify(update, context):
    load_dotenv()

    tidal_access_token = os.getenv('TIDAL_ACCESS_TOKEN')
    tidal_session_id = os.getenv('TIDAL_SESSION_ID')
    tidal_token_type = os.getenv('TIDAL_TOKEN_TYPE')
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    print(context.args)
    tidal_url = context.args[0]
    album_info = {}
    tidal_album_id = get_tidal_album_id(tidal_url)

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_client_id,
                                                                                  client_secret=spotify_client_secret))
    session = tidalapi.Session()
    session.load_oauth_session(session_id=tidal_session_id, access_token=tidal_access_token, token_type=tidal_token_type)
    tidal_album = session.get_album(tidal_album_id)

    #print("{}, {}, {}, {}".format(tidal_album.artist.name, tidal_album.name, tidal_album.release_date, tidal_url))

    results = spotify.search(q='artist:' + tidal_album.artist.name + ' album:'
                             + tidal_album.name , type='artist,album')
    print("{}, {}, {}, {}".format(results["albums"]["items"][0]["artists"][0]["name"],
          results["albums"]["items"][0]["name"], results["albums"]["items"][0]["release_date"],
          results["albums"]["items"][0]["external_urls"]["spotify"]))

    album_info = {"tidal": {"artist_name": tidal_album.artist.name,
                            "album_name": tidal_album.name,
                            "release_date": "{}".format(tidal_album.release_date.year),
                            "album_url": tidal_url},
                  "spotify": {"artist_name": results["albums"]["items"][0]["artists"][0]["name"],
                            "album_name": results["albums"]["items"][0]["name"],
                            "release_date": results["albums"]["items"][0]["release_date"],
                            "album_url": results["albums"]["items"][0]["external_urls"]["spotify"]}
                  }
    context.bot.send_message(chat_id=update.effective_chat.id, text="{}".format(album_info["spotify"]["album_url"]))
    return album_info

if __name__ == "__main__":
    #tidal_url="https://tidal.com/browse/album/35614665"
    #print(json.dumps(tidal2spotify(tidal_url)))
    load_dotenv()

    api_token = "BOTAPI_TOKEN"
    APITOKEN = os.getenv(api_token)
    if APITOKEN is None:
        exit("EEK! Define APITOKEN first.")
    updater = Updater(token=APITOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    oktay_handler = CommandHandler('oktay', shut_up)
    dispatcher.add_handler(oktay_handler)
    kitty_handler = CommandHandler('kitty', grab_a_kitten)
    dispatcher.add_handler(kitty_handler)
    mutato_handler = CommandHandler('mutato', tidal2spotify)
    dispatcher.add_handler(mutato_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    # TODO: Add a function to iterate through added handlers.

    updater.start_polling()
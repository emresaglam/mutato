import tidalapi
from dotenv import load_dotenv, dotenv_values

'''
This is used to renew the tidal token and recreate the .env file automatically.
IMPORTANT: You need to create a working .env file first! Then use this script to 
renew the TIDAL TOKENS ONLY! It really depends on your original .env file. 
'''
config = dotenv_values(".env")
session = tidalapi.Session()
session.login_oauth_simple()
config["TIDAL_ACCESS_TOKEN"] = session.access_token
config["TIDAL_SESSION_ID"] = session.session_id
f = open(".env", "w")
for key in config:
    f.write("{}=\"{}\"\n".format(key, config[key]))

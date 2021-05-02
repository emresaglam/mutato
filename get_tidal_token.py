import tidalapi
session = tidalapi.Session()
session.login_oauth_simple()
print("TIDAL_ACCESS_TOKEN=\"{}\" \n TIDAL_SESSION_ID=\"{}\"\n".format(session.access_token, session.session_id))
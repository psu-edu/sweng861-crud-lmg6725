import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# okta authentication configuration
OKTA_ISSUER = os.getenv("OKTA_ISSUER")
OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
OKTA_REDIRECT_URL = os.getenv("OKTA_REDIRECT_URL")
OKTA_CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")

# Flask session key
SECRET_KEY = os.getenv("SECRET_KEY")



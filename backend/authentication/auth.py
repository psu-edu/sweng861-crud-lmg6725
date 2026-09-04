from authlib.integrations.starlette_client import OAuth
from config import *

# Configure okta OAuth/OpenID connection
oauth = OAuth()

oauth.register(
    name="okta",
    server_metadata_url=f'{OKTA_ISSUER}/.well-known/openid-configuration',
    client_id=OKTA_CLIENT_ID,
    client_secret=OKTA_CLIENT_SECRET,
    redirect_uri=OKTA_REDIRECT_URL,
    client_kwargs={
        "scope": "openid profile email" # Request the user's identity and basic profile information.
    }
)

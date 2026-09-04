from flask import Flask, jsonify, session, send_from_directory
from flask import request, jsonify, g, redirect
from functools import wraps
from datetime import datetime, timezone
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
import jwt
from authlib.integrations.flask_client import OAuth
from database import engine, SessionLocal
from authentication.config import (
    SECRET_KEY,
    OKTA_CLIENT_ID,
    OKTA_CLIENT_SECRET,
    OKTA_ISSUER,
    OKTA_REDIRECT_URL
)
from models import Base, User

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)

app.secret_key = SECRET_KEY
Base.metadata.create_all(bind=engine)


# Set up logging
logging.basicConfig(filename="security.log", level=logging.INFO)

# Rate limiting setup
limiter = Limiter(
    get_remote_address,
    app = app,
    default_limits=["1000 per hour"]
)

oauth = OAuth(app)

oauth.register( 
    name="okta",
    client_id=OKTA_CLIENT_ID,
    client_secret=OKTA_CLIENT_SECRET,
    server_metadata_url=f"{OKTA_ISSUER}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid profile email"
        }
)

# Authentication Middleware
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid access token is required"
            }), 401

        auth_returned = auth_header.split()

        if len(auth_returned) != 2 or auth_returned[0].lower() != "bearer":
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid authorization header"
            }), 401

        access_token = auth_returned[1]

        """# Verify token matches logged-in session
        if access_token != session.get("access_token"):
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid access token is required"
            }), 401

        g.user_id = session.get("user_id")
        g.email = session.get("email")
        g.name = session.get("name")"""

        try:
            # Decode the token payload to identify the authenticated user.
            payload = jwt.decode(
                access_token,
                options={"verify_signature": False}
            )

            email = payload.get("sub")

            db = SessionLocal()

            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            if not user:
                db.close()

                return jsonify({
                    "error": "Unauthorized",
                    "message": "User not found"
                }), 401

            g.user_id = user.provider_id
            g.email = user.email
            g.name = user.name

            db.close()

        except Exception:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid token"
            }), 401
      

        return f(*args, **kwargs)

    return decorated

# Health check
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Debug session
@app.route("/debug-session")
def debug_session():
    return jsonify(dict(session))

# Protected Endpoint
# To use must pass in bearer token (can not be used without it)
@app.route('/api/hello')
@require_auth
def hello():
    logging.info(f"Accessing protected endpoint")
    return jsonify(
        {
            "message": f"Hello, {g.email}!"
        })

# Home page
@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")

# Login
@app.route("/login")
@limiter.limit("10 per minute") # Limit for this route
def login():
    response = oauth.okta.authorize_redirect(
        redirect_uri=OKTA_REDIRECT_URL
        )
    return response

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Authorization callback
@app.route("/authorize/callback")
def authorize():
    token = oauth.okta.authorize_access_token()
    userinfo = token["userinfo"]
    provider_id = userinfo["sub"]
    email = userinfo.get("email")
    name = userinfo.get("name")
    id_token = token.get("id_token")
    access_token = token.get("access_token")

    db = SessionLocal()

    user = (
    db.query(User)
    .filter(User.provider_id == provider_id)
    .first()
    )
    # Check if user exists, if not add to database
    if not user:
        user = User(
            provider_id=provider_id,
            email=email,
            name=name,
            created_at=datetime.now(timezone.utc),
            last_login=datetime.now(timezone.utc)
        )
        db.add(user) # Add user

    else: # Update existing user
        user.email = email
        user.name = name
        user.last_login = datetime.now(timezone.utc)

    db.commit()
    db.close()

    session["email"] = email
    session["name"] = name
    session["user_id"] = provider_id
    session["access_token"] = access_token

    if id_token and access_token:

        """return jsonify({
            "message": "Log in successful",
            "access_token": access_token})"""
        return redirect("/")
    else:
        return jsonify({
            "message": "Log in not successful"
            })
    #return redirect(url_for("home"))

# Return session information
@app.route("/session-info")
def session_info():
    return jsonify({
        "logged_in": "access_token" in session,
        "access_token": session.get("access_token")
    })

# Return user profile information
@app.route("/profile")
@require_auth
def profile():
    return jsonify({
        "user_id": g.user_id,
        "email": g.email
    })

# Return user information for the authenticated user
@app.route("/users/me")
@require_auth
def get_users():
    db = SessionLocal()
    user = (
        db.query(User)
        .filter(User.provider_id == g.user_id)
        .first()
    )
    if not user:
        db.close()
        return "User not found", 404

    result = {
            "email": user.email, 
            "name": user.name,
            "created_at": user.created_at,
            "last_login": user.last_login}
    
    db.close()
    return jsonify(result)

# Return a greeting and the authenticated user's name 
# A check to verify we are authenticated and returning data
@app.route("/protected")
@require_auth
def protected():
    return jsonify({
        "message": f"Hello, {g.name or 'user'}!",
        "name": g.name
    })

if __name__ == '__main__':
    app.run(debug=False)


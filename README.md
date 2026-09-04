# sweng861-crud-lmg6725

Lauren Gilbert
- Course name: SWENG 861 – Software Construction

A web application developed for SWENG 861: Software Construction at Penn State. The application uses a Flask backend and a lightweight HTML frontend with Okta authentication.

Tech Stack:
- Python3
- HTML
- FLask
- Okta
- OAuth 2.0 / OpenID Connect
- Git
- GitHub

Clone the repository steps
- git clone <repository url>
- cd <repository name>

Authentication

The application uses Okta for authentication. The frontend provides a Login with Okta button that redirects the user to Okta for authentication. After authentication, Okta redirects the user back to the application's callback endpoint.

Running the Application

Open Command Prompt and navigate to the backend folder:

cd backend

Create and activate the virtual environment:

python -m venv venv
venv\Scripts\activate

Install the required packages:

pip install -r requirements.txt

Start the Flask application from the virtual environment:

python main.py

Open the application in a browser:

http://localhost:5000/

# Authentication Strategy

## Option Chosen: C – Enterprise SSO with Okta

This project uses Okta as an external Identity Provider (IdP) while maintaining a local user database within the application. I chose this approach because it combines the security benefits of a trusted identity provider with the flexibility of storing application-specific user information locally.

In a healthcare setting, this architecture is particularly beneficial because sensitive patient and employee data can remain under the organization's control while authentication is securely handled by Okta.

Authentication is implemented using Okta OpenID Connect (OIDC). User identity is extracted from the Okta-issued access token and mapped to local user records.

---

## Authentication Flow

When a user clicks the **Login with Okta** button, they are redirected to Okta for authentication. After a successful login, Okta redirects the user back to the application's callback endpoint with an authorization code. The backend exchanges the authorization code for tokens, retrieves the user's profile information, and checks the local database for an existing user record. If the user does not exist, a new local user record is created. The authenticated user can then access protected resources within the application.

### Flow Sequence

1. Client → Login with Okta button
2. Login button → Okta Identity Provider (IdP)
3. Okta IdP → User authentication
4. Okta → Callback endpoint with authorization code
5. Backend → Exchange authorization code for tokens
6. Backend → Retrieve user profile information
7. Backend → Look up or create local user record
8. Backend → Validate user and establish session
9. User → Access protected API endpoints

### Flow Summary

Client
   ↓
Login Button
   ↓
Okta (IdP)
   ↓
Callback Endpoint
   ↓
Token Exchange
   ↓
Local User Database
   ↓
Protected API

---

# Protected Endpoint Description

The `/api/hello` endpoint is protected using the `requireAuth` middleware. This middleware verifies that a valid bearer token is included in the request before allowing access to the endpoint. If the user is not authenticated, the request is rejected with a **401 Unauthorized** response. When authentication succeeds, the middleware extracts the user's identity and makes it available to the endpoint handler, which returns a personalized greeting.

---

# OWASP API Security Practices Applied

## 1. Broken Object Level Authorization (BOLA)

The API only uses the authenticated user's identity from the token and request context. Users cannot access data belonging to other users.

## 2. Excessive Data Exposure

The protected endpoint returns only the information needed for the response (a greeting message) and does not expose user records, tokens, or sensitive claims.

## 3. Security Misconfiguration

Authentication failures return generic JSON error messages and HTTP 401 responses without exposing stack traces or internal application details. Detailed errors are logged server-side for troubleshooting.

---

# Bonus Features

## Rate Limiting

Implemented Flask-Limiter to restrict login requests to **10 attempts per minute per IP address**. This helps reduce the risk of brute-force attacks against authentication endpoints.

## Security Logging

Added application logging for login attempts and protected endpoint access. Logs include timestamps and can be reviewed to identify suspicious activity, such as repeated failed login attempts or unusual access patterns.
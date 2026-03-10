import sys
import datetime
from datetime import timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from IMDBTraktSyncer import errorHandling as EH
from IMDBTraktSyncer import errorLogger as EL


class TraktAuthenticationError(RuntimeError):
    pass


def _build_expiration_time(expires_in):
    expiration_time = datetime.datetime.now(timezone.utc) + timedelta(
        seconds=expires_in - 120
    )
    return expiration_time.replace(tzinfo=timezone.utc).isoformat()


def _parse_token_response(response):
    if not response or response.status_code not in [200, 201]:
        return None

    json_data = response.json()
    access_token = json_data["access_token"]
    refresh_token = json_data["refresh_token"]
    expires_in = json_data["expires_in"]
    expiration_time = _build_expiration_time(expires_in)
    return access_token, refresh_token, expiration_time


def _prompt_for_authorization_code(auth_url):
    if not sys.stdin or not sys.stdin.isatty():
        raise TraktAuthenticationError(
            "Trakt authentication requires an interactive terminal. "
            "Run the app locally and complete the browser authorization step to refresh credentials."
        )

    print(
        f"\nPlease visit the following URL to authorize this application: \n{auth_url}\n"
    )
    try:
        authorization_code = input("Please enter the authorization code from the URL: ")
    except EOFError as exc:
        raise TraktAuthenticationError(
            "Trakt needs a new authorization code, but no interactive input was available. "
            "Run the app in a local terminal to complete OAuth again."
        ) from exc
    if not authorization_code.strip():
        raise ValueError("Authorization code cannot be empty.")
    return authorization_code.strip()


def authenticate(client_id, client_secret, refresh_token=None):
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

    if refresh_token:
        # If a refresh token is provided, use it to get a new access token
        data = {
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "refresh_token",
        }
        headers = {
            "Content-Type": "application/json",
        }

        # Use make_trakt_request for the POST request
        response = EH.make_trakt_request(
            "https://api.trakt.tv/oauth/token", headers=headers, payload=data
        )

        parsed_tokens = _parse_token_response(response)
        if parsed_tokens:
            return parsed_tokens

        invalid_refresh_token = response is not None and response.status_code in [
            400,
            401,
        ]
        if invalid_refresh_token:
            message = "Saved Trakt refresh token is no longer valid."
            print(f" - {message}")
            EL.logger.warning(message)

        return authenticate(client_id, client_secret)

    else:
        # Set up the authorization endpoint URL
        auth_url = "https://trakt.tv/oauth/authorize"

        # Construct the authorization URL with the necessary parameters
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
        }
        auth_url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])

        authorization_code = _prompt_for_authorization_code(auth_url)

        # Set up the access token request
        data = {
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {
            "Content-Type": "application/json",
        }

        # Use make_trakt_request for the POST request
        response = EH.make_trakt_request(
            "https://api.trakt.tv/oauth/token", headers=headers, payload=data
        )

        parsed_tokens = _parse_token_response(response)
        if parsed_tokens:
            return parsed_tokens

        raise TraktAuthenticationError(
            "Trakt authorization failed. Verify the client ID, client secret, and authorization code, then try again."
        )

    return None

import json
import requests
from jose import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

class Auth0JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            raise exceptions.AuthenticationFailed('Invalid Authorization header')

        token = parts[1]

        try:
            unverified_header = jwt.get_unverified_header(token)
            jwks = requests.get(settings.OIDC_JWKS_URL).json()
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }

            if not rsa_key:
                raise exceptions.AuthenticationFailed('Unable to find appropriate key')

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.OIDC_AUDIENCE,
                issuer=settings.OIDC_ISSUER,
            )

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.JWTClaimsError:
            raise exceptions.AuthenticationFailed('Invalid claims')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Token decode error: {str(e)}')

        # You can customize the user fetching here
        user_id = payload.get('sub')
        if not user_id:
            raise exceptions.AuthenticationFailed('Token missing subject')

        return (None, token)  # Returning None for User if you don’t manage local users

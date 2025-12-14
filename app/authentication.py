"""
Custom JWT Cookie Authentication

This module provides cookie-based JWT authentication instead of
the default header-based Bearer token approach.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HTTP-only cookies.

    This provides better security against XSS attacks by storing
    tokens in HTTP-only cookies that JavaScript cannot access.
    """

    def authenticate(self, request):
        """
        Authenticate the request using JWT from cookies.

        First checks for access token in cookies, falls back to
        Authorization header for API clients that prefer headers.
        """
        # Try to get token from cookie first
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if raw_token is None:
            # Fall back to header-based authentication for API clients
            return super().authenticate(request)

        # Validate the token from cookie
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except TokenError as e:
            raise InvalidToken(e.args[0])

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return f'Bearer realm="{self.www_authenticate_realm}"'

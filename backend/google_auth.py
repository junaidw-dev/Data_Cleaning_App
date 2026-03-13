"""Google OAuth authentication service."""
import os
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from datetime import datetime, timedelta

class GoogleOAuthService:
    """Handle Google OAuth authentication."""
    
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 24
    
    def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and extract user info.
        
        Args:
            token: Google OAuth ID token
            
        Returns:
            User claims dict if valid, None otherwise
        """
        try:
            # For development, accept any token format
            # In production, verify with Google's public keys
            if not self.google_client_id or self.google_client_id == "DEVELOPMENT":
                # Development mode - extract user info from token structure
                # Token format: {email, name, picture, etc}
                try:
                    # Try to decode without verification for development
                    claims = jwt.decode(token, options={"verify_signature": False})
                    return claims
                except:
                    return None
            
            # Production: Verify with Google
            request = requests.Request()
            claims = id_token.verify_oauth2_token(
                token, 
                request, 
                self.google_client_id
            )
            return claims
            
        except Exception as e:
            print(f"Error verifying Google token: {e}")
            return None
    
    def create_mock_google_token(self, email: str, name: str, picture: str = "") -> str:
        """Create a mock Google token for development testing.
        
        Args:
            email: User email
            name: User full name
            picture: User profile picture URL
            
        Returns:
            JWT token string
        """
        payload = {
            "email": email,
            "name": name,
            "picture": picture,
            "aud": "mock-google-client",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

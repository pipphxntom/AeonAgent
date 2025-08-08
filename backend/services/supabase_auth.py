from supabase import create_client, Client
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class SupabaseAuth:
    """Supabase authentication service."""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        self.admin_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data."""
        try:
            response = self.client.auth.get_user(token)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed": response.user.email_confirmed_at is not None,
                    "created_at": response.user.created_at,
                    "user_metadata": response.user.user_metadata,
                    "app_metadata": response.user.app_metadata
                }
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def sign_up(self, email: str, password: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Sign up a new user."""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "email_confirmed": response.user.email_confirmed_at is not None
                    },
                    "session": response.session.access_token if response.session else None
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user"
                }
        except Exception as e:
            logger.error(f"Sign up failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email and password."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.session:
                return {
                    "success": True,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "email_confirmed": response.user.email_confirmed_at is not None
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
        except Exception as e:
            logger.error(f"Sign in failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "success": True,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to refresh token"
                }
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user."""
        try:
            self.client.auth.sign_out(access_token)
            return True
        except Exception as e:
            logger.error(f"Sign out failed: {e}")
            return False
    
    async def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Update user metadata (admin only)."""
        try:
            response = self.admin_client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": metadata}
            )
            return response.user is not None
        except Exception as e:
            logger.error(f"Failed to update user metadata: {e}")
            return False


# Global instance
supabase_auth = SupabaseAuth()

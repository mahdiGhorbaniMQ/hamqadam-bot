# bot/core_api_client.py

import logging
import httpx # Import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CORE_API_BASE_URL = "http://localhost:8080/api/v1"

class CoreAPIClient:
    # Removed self.auth_token from here to make client more stateless per user.
    # Token will be managed in context.user_data by handlers.

    async def login_or_register_telegram_user(
        self, telegram_id: int, telegram_username: Optional[str]
    ) -> Dict[str, Any]:
        """
        Actual call to: POST /api/v1/auth/telegram
        Logs in or registers a user via Telegram details.
        """
        endpoint = f"{CORE_API_BASE_URL}/auth/telegram"
        payload = {
            "telegramId": str(telegram_id), # As per User entity: telegram_id (String)
            "telegramUsername": telegram_username,
            # Add other fields if your Core API expects them for registration,
            # e.g., "registration_method": "telegram" might be set by the backend.
        }
        logger.info(
            f"Calling Core API: POST {endpoint} with payload: {payload}"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status() # Raise an exception for HTTP error codes 4xx/5xx
                api_response_data = response.json()
                logger.info(f"Core API success response: {api_response_data}")
                return api_response_data # This should contain token and user data
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred while calling Core API: {e.response.status_code} - {e.response.text}"
            )
            return {
                "status": "error",
                "message": f"Core API HTTP error: {e.response.status_code}",
                "error_detail": e.response.text,
                "data": None,
            }
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while calling Core API: {e}")
            return {
                "status": "error",
                "message": "Core API request error. Is the Core service running?",
                "error_detail": str(e),
                "data": None,
            }
        except Exception as e:
            logger.exception("An unexpected error occurred during API call:")
            return {
                "status": "error",
                "message": "An unexpected error occurred.",
                "error_detail": str(e),
                "data": None,
            }

        # --- Dummy Response (kept for reference or fallback if needed) ---
        # logger.info(
        #     f"STUB: Simulating login/register for Telegram user: telegram_id={telegram_id}, username={telegram_username}"
        # )
        # if telegram_id == 12345: # Simulate a known user
        #     dummy_response = {
        #         "status": "success",
        #         "message": "User logged in successfully.",
        #         "data": {
        #             "token": "dummy_jwt_token_for_12345",
        #             "user": {
        #                 "user_id": "user_uuid_123",
        #                 "telegram_id": str(telegram_id),
        #                 "telegram_username": telegram_username or "testuser",
        #                 "full_name": {"en": "Test User", "fa": "کاربر تستی"},
        #                 "account_status": "active"
        #             }
        #         }
        #     }
        #     return dummy_response
        # else: # Simulate a new user registration
        #     dummy_response = {
        #         "status": "success",
        #         "message": "User registered and logged in successfully.",
        #         "data": {
        #             "token": f"dummy_jwt_token_for_{telegram_id}",
        #             "user": {
        #                 "user_id": f"user_uuid_{telegram_id}",
        #                 "telegram_id": str(telegram_id),
        #                 "telegram_username": telegram_username,
        #                 "full_name": {"en": f"New User {telegram_id}", "fa": f"کاربر جدید {telegram_id}"},
        #                 "account_status": "pending_verification"
        #             }
        #         }
        #     }
        #     return dummy_response
        # --- End Dummy Response ---

    async def get_my_profile(self, auth_token: str) -> Dict[str, Any]:
        """
        Actual call for: GET /api/v1/users/me
        Fetches the current user's profile using their auth token.
        """
        endpoint = f"{CORE_API_BASE_URL}/users/me"
        logger.info(f"Calling Core API: GET {endpoint}")

        if not auth_token:
            logger.warning("No auth token provided for get_my_profile.")
            return {"status": "error", "message": "Authentication token required.", "data": None}

        headers = {"Authorization": f"Bearer {auth_token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers)
                response.raise_for_status()
                api_response_data = response.json()
                logger.info(f"Core API success response for get_my_profile: {api_response_data}")
                return api_response_data
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred while calling get_my_profile: {e.response.status_code} - {e.response.text}"
            )
            return {
                "status": "error",
                "message": f"Core API HTTP error: {e.response.status_code}",
                "error_detail": e.response.text,
                "data": None,
            }
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while calling get_my_profile: {e}")
            return {
                "status": "error",
                "message": "Core API request error for get_my_profile.",
                "error_detail": str(e),
                "data": None,
            }
        except Exception as e:
            logger.exception("An unexpected error occurred during get_my_profile API call:")
            return {
                "status": "error",
                "message": "An unexpected error occurred.",
                "error_detail": str(e),
                "data": None,
            }

        # --- Dummy Response (kept for reference) ---
        # user_id_from_token = auth_token.split("_for_")[-1] if auth_token and "_for_" in auth_token else "unknown_stub_user"
        # is_known_user = user_id_from_token == "12345"
        # return {
        #     "status": "success",
        #     "message": "Profile fetched successfully.",
        #     "data": {
        #         "user_id": "user_uuid_123" if is_known_user else f"user_uuid_{user_id_from_token}",
        #         "telegram_id": user_id_from_token,
        #         # ... other fields
        #     }
        # }
        # --- End Dummy Response ---

# Global instance for easy access.
# For more complex scenarios, dependency injection or context-managed instances might be better.
api_client = CoreAPIClient()
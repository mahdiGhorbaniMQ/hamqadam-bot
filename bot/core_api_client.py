# bot/core_api_client.py

import logging
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CORE_API_BASE_URL = "http://hamqadam-core:8080/api/v1" # Ensure this is correct

async def log_request_details(request: httpx.Request): # Made async
    logger.info(f"Outgoing HTTPX Request:")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {request.headers}")
    if request.content:
        content_to_log = request.content
        if isinstance(content_to_log, bytes):
            try:
                content_to_log = content_to_log.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                content_to_log = "[binary content]"
        logger.info(f"Body: {content_to_log}")

class CoreAPIClient:
    async def login_or_register_telegram_user(
        self, telegram_id: int, telegram_username: Optional[str]
    ) -> Dict[str, Any]:
        endpoint = f"{CORE_API_BASE_URL}/auth/telegram"
        # Using camelCase for payload keys as requested
        payload = {
            "telegramId": str(telegram_id),
            "telegramUsername": telegram_username,
        }
        try:
            async with httpx.AsyncClient(event_hooks={'request': [log_request_details]}) as client:
                response = await client.post(endpoint, json=payload)
                if response.status_code not in [200, 201]:
                    logger.warning(f"Core API (login) returned {response.status_code}. Response Body: {response.text[:500]} Headers: {response.headers}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error (login): {e.response.status_code} - {e.response.text[:500]}. Req: {e.request.url}")
            return {"_api_error": True, "status_code": e.response.status_code, "message": f"Core API HTTP error: {e.response.status_code}", "error_detail": e.response.text[:500]}
        except httpx.RequestError as e:
            logger.error(f"Request error (login): {e}. Req: {e.request.url if e.request else 'N/A'}")
            return {"_api_error": True, "message": "Core API request error. Is Core service running?", "error_detail": str(e)}
        except Exception as e:
            logger.exception("Unexpected error during API call (login):")
            return {"_api_error": True, "message": "An unexpected error occurred.", "error_detail": str(e)}

    async def get_my_profile(self, auth_token: str) -> Dict[str, Any]:
        endpoint = f"{CORE_API_BASE_URL}/users/me"
        if not auth_token:
            logger.warning("No auth token for get_my_profile.")
            return {"_api_error": True, "message": "Authentication token required."}

        headers = {"Authorization": f"Bearer {auth_token}"}
        try:
            async with httpx.AsyncClient(event_hooks={'request': [log_request_details]}) as client:
                response = await client.get(endpoint, headers=headers)
                if response.status_code != 200:
                     logger.warning(f"Core API (get_profile) returned {response.status_code}. Response Body: {response.text[:500]}. Headers: {response.headers}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error (get_profile): {e.response.status_code} - {e.response.text[:500]}. Req: {e.request.url}")
            return {"_api_error": True, "status_code": e.response.status_code, "message": f"Core API HTTP error: {e.response.status_code}", "error_detail": e.response.text[:500]}
        except httpx.RequestError as e:
            logger.error(f"Request error (get_profile): {e}. Req: {e.request.url if e.request else 'N/A'}")
            return {"_api_error": True, "message": "Core API request error for get_profile.", "error_detail": str(e)}
        except Exception as e:
            logger.exception("Unexpected error during get_my_profile API call:")
            return {"_api_error": True, "message": "An unexpected error occurred.", "error_detail": str(e)}

api_client = CoreAPIClient()
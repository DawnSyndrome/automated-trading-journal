import requests
import time
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import *
from src.logging.logger import Logger
from src.utils.config_vars import HTTP_VALID_RESPONSE_CODES, API_VALID_INTERNAL_RESPONSE_CODES
import aiohttp

logger = Logger()

class RequestHandler:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            missing_data = "api_key" if not api_key else "api_secret"
            raise ValueError(f"Unable to set up RequestHandler. Missing '{missing_data}'")

        self.api_key = api_key
        self.api_secret = api_secret

    def generate_signature(self, params):
        # generates an HMAC signature for the upcoming API request
        sorted_params = "&".join(f"{key}={params[key]}" for key in sorted(params))
        return hmac.new(
            self.api_secret.encode("utf-8"),
            sorted_params.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def build_request_params(self, additional_params: Dict, date='', day_count=1):
        date_dict = {}
        if date:
            # converts the date to the UNIX timestamp range specified by the user
            start_date = datetime.strptime(date, "%Y-%m-%d")
            start_time = int(start_date.timestamp())
            end_time = int((start_date + timedelta(days=day_count)).timestamp())

            date_dict = {
            "startTime": start_time * 1000,
            "endTime": end_time * 1000,
            }

        main_params = {
            "api_key": self.api_key,
            "category": "linear",
            "timestamp": str(int(time.time() * 1000))
        }

        params = main_params | date_dict | additional_params
        params["sign"] = self.generate_signature(params)

        return params

    async def process_request(self, session, url, params):
        async with session.get(url, params=params) as response:
            if response.status not in HTTP_VALID_RESPONSE_CODES:
                response.raise_for_status()
            return await response.json()

    async def get_paginated_response(self, endpoint, additional_params, date, day_count=1, use_async=False):
        if not endpoint:
            raise ValueError("Unable to process response without a valid endpoint")
        if day_count < 1:
            raise ValueError("day_count value must be higher than 0. At least 24 hours of data must be requested")

        full_response = []
        if use_async:
            async with aiohttp.ClientSession() as session:
                while True:
                    request_params = self.build_request_params(additional_params, date, day_count)
                    logger.debug(f"Request params: {request_params}")

                    response_json = await self.process_request(session, endpoint, request_params)
                    if response_json.get("retCode") not in API_VALID_INTERNAL_RESPONSE_CODES:
                        logger.warning(
                            f"Unable to process request: code '{response_json.get('retCode')}',"
                            f" retMsg '{response_json.get('retMsg')}'"
                        )
                        return full_response

                    response_result = response_json.get('result', {})
                    cursor = response_result.get('nextPageCursor', None)

                    full_response += response_result.get('list', [])
                    if not cursor:
                        break
                    additional_params["cursor"] = cursor
                    logger.debug(f"Async Response: {response_json}")
        else:
            while True:
                request_params = self.build_request_params(additional_params, date, day_count)
                logger.debug(f"Request params: {request_params}")
                response = requests.get(endpoint, params=request_params)

                if response.status_code not in HTTP_VALID_RESPONSE_CODES:
                    response.raise_for_status()

                response_json = response.json()
                if response_json.get("retCode") not in API_VALID_INTERNAL_RESPONSE_CODES:
                    logger.warning(f"Unable to process request: code '{response_json.get("retcode")}',"
                                    f" retMsg '{response_json.get("retMsg")}'")
                    return full_response

                response_result = response_json.get('result', {})
                cursor = response_result.get('nextPageCursor', None)

                full_response += response_result.get('list',[])
                if not cursor:
                    break
                additional_params["cursor"] = cursor
                logger.debug(f"Response: {response.status_code}, {response.text}")

        return full_response

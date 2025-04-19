from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from urllib.error import HTTPError
from src.api.request_handler import RequestHandler
from parameterized import parameterized

class TestRequestHandler(IsolatedAsyncioTestCase):

    @parameterized.expand([
        ("valid_test", "api_key", "api_secret", True),
        ("test_missing_api_key", "", "api_secret", False),
        ("test_missing_api_secret", "api_key", "", False),
    ])
    def test_contructor(self, _, api_key, api_secret, is_valid):
        if not is_valid:
            with self.assertRaises(ValueError):
                RequestHandler(api_key, api_secret)
        else:
            handler = RequestHandler(api_key, api_secret)
            self.assertIsNot(handler, None)
            self.assertEqual(handler.api_key, api_key)
            self.assertEqual(handler.api_secret, api_secret)

    def setUp(self):
        self.handler = RequestHandler(api_key="valid_key", api_secret="valid_secret")

    @parameterized.expand([
        ("valid_test", "2025-01-01", 2, {"test": "value"}, True, None),
        ("valid_test_without_date", "", 1, {"test": "value"}, True, None),
        #("failed_test_with_negative_day_count", "", -1, {}, False, ValueError),
    ])
    @patch("src.api.request_handler.time.time", return_value=1672531200)
    def test_build_request_params(self, _, date, day_count, additional_params, is_valid, returned, mock_time):
        if not is_valid:
            with self.assertRaises(returned):
                self.handler.build_request_params(additional_params, date, day_count)
        else:
            params = self.handler.build_request_params(additional_params, date, day_count)

            if date:
                expected_start_time = int(datetime.strptime(date, "%Y-%m-%d").timestamp()) * 1000
                expected_end_time = expected_start_time + (day_count * 86400000)
                self.assertEqual(params["startTime"], expected_start_time)
                self.assertEqual(params["endTime"], expected_end_time)
            [self.assertEqual(params[key], value) for key, value  in additional_params.items()]
            self.assertIn("sign", params)

    @parameterized.expand([
        (
                "async_single_page",
                "https://api-testnet.bybit.com/v5/order/history",
                1,
                [
                    {
                        "retCode": 0,
                        "result": {
                            "list": [{"data": "item1"}],
                            "nextPageCursor": None,
                        },
                    }
                ],
                [{"data": "item1"}],
                True, True,
        ),
        (
                "async_multi_page",
                "https://api-testnet.bybit.com/v5/order/history",
                1,
                [
                    {
                        "retCode": 0,
                        "result": {
                            "list": [{"data": "item1"}],
                            "nextPageCursor": "cursor1",
                        },
                    },
                    {
                        "retCode": 0,
                        "result": {
                            "list": [{"data": "item2"}],
                            "nextPageCursor": None,
                        },
                    },
                ],
                [{"data": "item1"}, {"data": "item2"}],
                True, True,
        ),
        (
                "sync_single_page",
                "https://api-testnet.bybit.com/v5/order/history",
                1,
                [{
                    "status_code": 200,
                    "response": {
                        "retCode": 0,
                        "result": {
                            "list": [{"data": "item1"}],
                            "nextPageCursor": None,
                        },
                    },
                }],
                [{"data": "item1"}],
                False, True,
        ),
        (
                "sync_multi_page",
                "https://api-testnet.bybit.com/v5/order/history",
                1,
                [
                    {
                        "status_code": 200,
                        "response": {
                            "retCode": 0,
                            "result": {
                                "list": [{"data": "item1"}],
                                "nextPageCursor": "cursor1",
                            },
                        },
                    },
                    {
                        "status_code": 200,
                        "response": {
                            "retCode": 0,
                            "result": {
                                "list": [{"data": "item2"}],
                                "nextPageCursor": None,
                            },
                        },
                    },
                ],
                [{"data": "item1"}, {"data": "item2"}],
                False, True,
        ),
        (
                "sync_bad_status_code",
                "https://api-testnet.bybit.com/v5/order/history",
                1,
                [{
                    "status_code": 403,
                    "response": {
                        "retCode": 0,
                        "result": {
                            "list": [{"data": "item1"}],
                            "nextPageCursor": None,
                        },
                    },
                }],
                HTTPError,
                False, False,
        ),
    ])
    # @patch("src.api.request_handler.aiohttp.ClientSession.get")
    @patch("src.api.request_handler.requests.get")
    @patch("src.api.request_handler.RequestHandler.process_request", new_callable=AsyncMock)
    @patch("src.api.request_handler.RequestHandler.generate_signature", return_value="mock_signature")
    @patch("src.api.request_handler.Logger.debug")
    async def test_get_paginated_response(
            self, _, endpoint, day_count, mock_responses, expected_result,
            use_async, is_valid, mock_logger, mock_generate_signature,
            mock_process_request, mock_sync_get,
    ):
        if use_async:
            if not is_valid:
                with self.assertRaises(expected_result):
                    await self.handler.get_paginated_response(endpoint, {}, "2025-01-01", day_count, use_async)
                return

            mock_process_request.side_effect = mock_responses

            response = await self.handler.get_paginated_response(
                endpoint=endpoint, additional_params={}, date="2025-01-01", day_count=day_count, use_async=True
            )
        else:
            def sync_side_effect(*args, **kwargs):
                if isinstance(mock_responses, list):
                    result = mock_responses.pop(0)
                else:
                    result = mock_responses

                mock_object = MagicMock()
                mock_object.status_code = result.get("status_code")
                mock_object.json.return_value = result.get("response")
                if mock_object.status_code != 200:
                    mock_object.raise_for_status.side_effect = HTTPError(
                        code=mock_object.status_code, msg=f"Bad HTTP {mock_object.status_code}", hdrs={}, fp=None,
                        url=endpoint,
                    )
                return mock_object
            mock_sync_get.side_effect = sync_side_effect

            if not is_valid:
                with self.assertRaises(expected_result):
                    await self.handler.get_paginated_response(
                        endpoint=endpoint, additional_params={}, date="2025-01-01", day_count=day_count, use_async=False
                    )
                return
            response = await self.handler.get_paginated_response(
                endpoint=endpoint, additional_params={}, date="2025-01-01", day_count=day_count, use_async=False
            )

        self.assertEqual(response, expected_result)
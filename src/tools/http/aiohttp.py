import asyncio

import orjson
from aiohttp import ClientResponse, ClientSession


class AiohttpClient:
    async def async_init(self) -> None:
        self._session = ClientSession(json_serialize=orjson.dumps)

    async def request_raw(
        self, url: str, method: str = 'GET', data: dict | None = None, **kwargs
    ) -> ClientResponse:
        async with self._session.request(
            method=method, url=url, data=data, **kwargs
        ) as response:
            await response.read()
            return response

    async def request_json(
        self, url: str, method: str = 'GET', data: dict | None = None, **kwargs
    ) -> dict:
        response = await self.request_raw(
            url=url, method=method, data=data, **kwargs
        )
        return await response.json(
            encoding='utf-8', loads=orjson.loads, content_type=None
        )

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def __del__(self) -> None:
        if self._session and not self._session.closed:
            if (
                self._session._connector is not None
                and self._session._connector_owner
            ):
                self._session._connector._close()
            self._session._connector = None

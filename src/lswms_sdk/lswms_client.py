from  __future__ import annotations
import asyncio
import logging
import time 
from typing import Any, Iterable
from datetime import date 
import httpx 
from pydantic import TypeAdapter
import json 
from tenacity import retry, retry_if_exception,stop_after_attempt, wait_exponential
from lswms_sdk.lswms_models import (Adm1, Adm2, Adm3,Waterpoints)
from lswms_sdk.lswms_api_error import WaterpointAPIError
from lswms_sdk.utils import csv
import atexit

logger = logging.getLogger(__name__)

class WaterpointClient:
    """
    Use as an async context manager::
        async with WaterpointClient(client_id="...", client_secret="...") as client:
            countries = await client.get_countries()
    """

    def __init__(self,
                *,
                base_url: str = "https://webapi.waterpointsmonitoring.net",
                timeout: float = 30.0,)->None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http:httpx.AsyncClient | None = None
    async def __aenter__(self)->"WaterpointClient":
        self._http = httpx.AsyncClient(timeout=self._timeout, headers={"Content-Type":"application/json"})
        return self
    async def __aexit__(self, *_:Any) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception(httpx.TransportError),
    reraise=True,
)
    async def get(self, path: str, **params: Any) -> Any:
        assert self._http, "Client not initialized; use 'async with AClimateClient(...)'"
        
        # Filter out None query parameters
        clean_params = {k: v for k, v in params.items() if v is not None}
        
        response = await self._http.get(f"{self.base_url}{path}", params=clean_params)
        
        if response.status_code >= 400:
            raise WaterpointAPIError(response.status_code, response.text[:500])
            
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception((httpx.TransportError)),
        reraise=True,
    )
    async def post(self, path: str, json_body: dict[str, Any]) -> Any:
        assert self._http, "Client not initialized; use 'async with AClimateClient(...)'"
        
        # Filter out None values in top-level JSON body if desired
        clean_body = {k: v for k, v in json_body.items() if v is not None}
        
        response = await self._http.post(f"{self.base_url}{path}", json=clean_body)
        
        if response.status_code >= 400:
            raise WaterpointAPIError(response.status_code, response.text[:500])
            
        return response.json()
        # Adm1 levels or get zone
    async def get_Adm1(self) -> list[Adm1]:
        return TypeAdapter(list[Adm1]).validate_python(await self.get("/adm1"))

    #Adm1 levels or get woredas
    async def get_adm2_by_adm1_ids(self, adm1  : str | int | Iterable[int]) -> list[Adm2]:
        
        return TypeAdapter(list[Adm2]).validate_python(await self.get(f"/adm2/{adm1}"))#, adm1=csv(adm1))


    async def get_waterpoints(self) -> list[Waterpoints]:
        response_data = await self.get("/waterpoints")
        return TypeAdapter(list[Waterpoints]).validate_python(response_data)
        return TypeAdapter(list([Waterpoints]).validate_python(await self.get("/waterpoints")))

_client: WaterpointClient | None = None
_client_lock = asyncio.Lock()
_client_started = False


async def get_client(base_url: str = "https://webapi.waterpointsmonitoring.net/api/v1/",  timeout: float = 30.0) -> WaterpointClient:
    global _client, _client_started
    if _client is not None and _client_started:
        return _client
    async with _client_lock:
        if _client is not None and _client_started:
            return _client
        client = WaterpointClient(base_url=base_url, timeout=timeout)
        await client.__aenter__()
        _client = client
        _client_started = True
        return _client


async def close_client() -> None:
    global _client, _client_started
    if _client is not None and _client_started:
        await _client.__aexit__(None, None, None)
        _client = None
        _client_started = False


def _close_client_at_exit() -> None:
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(close_client())
    except Exception:
        pass


atexit.register(_close_client_at_exit)


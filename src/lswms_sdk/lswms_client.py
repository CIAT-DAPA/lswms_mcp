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
from lswms_sdk.lswms_models import (Adm1, Adm2, Adm3,Advisory,Waterpoints,SeasonalForecast,SubseasonalForecast,Monitored)
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
        assert self._http, "Client not initialized; use 'async with WaterpointClient(...)'"
        
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
        assert self._http, "Client not initialized; use 'async with WaterpointClient(...)'"
        
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
    
    async def get_seasonal_forecast(self, waterpoint_id: str)->SeasonalForecast:
        response_data = await self.get(f"/seasonal_sub_forecast/{waterpoint_id}") 
        response_seasonal = response_data['seasonal']
        # return TypeAdapter(list[SubseasonalForecast]).validate_python([response_seasonal])
        return SeasonalForecast.model_validate(response_seasonal)
    
    async def get_subseasonal_forecast(self, waterpoint_id: str)-> SubseasonalForecast:
        response_data = await self.get(f"/seasonal_sub_forecast/{waterpoint_id}")
        response_subseasonal = response_data["subseasonal"]
        return SubseasonalForecast.model_validate(response_subseasonal)
    
    async def get_daily_observations(self,waterpoint_id:str)-> list[Monitored]:
        response_data = await self.get(f"/monitored/{waterpoint_id}")
        # return TypeAdapter(list[Monitored]).validate_python(response_data)
        return TypeAdapter(list[Monitored]).validate_python(response_data)
    
    async def get_current_observations(self,waterpoint_id:str)-> list[Monitored]:
        response_data = await self.get(f"/lastmonitored/{waterpoint_id}")# response is a list of dicts
        return [Monitored.model_validate(item) for item in response_data]
        # return TypeAdapter(list[Monitored]).validate_python(response_data)

    async def get_waterpoint_status(self, waterpoint_id: str, language: str = "en") -> list[Advisory]:
        payload = {
            "advisories": ["wp_status"], 
            "language": [language], 
            "waterpoints": [waterpoint_id]
        }
        response_data = await self.post("/advisory", payload)
        # if isinstance(response_data, dict) and "advisories" in response_data:
        #     response_data = response_data["advisories"]
        # Use TypeAdapter for consistent validation and better error messages
        return TypeAdapter(list[Advisory]).validate_python(response_data)
    

    async def get_waterpoint_profile(self, waterpoint_id: str, language: str = "en") -> dict:
        response_data = await self.get(f"/waterpointsprofiles/{waterpoint_id}/{language}") 
        
        if isinstance(response_data, list):
            if len(response_data) > 0:
                return Waterpoints.model_validate(response_data[0]) 
            else:
                return []
        # only one dict is retrived here and model_validate is used 
        return TypeAdapter(Monitored.validate_python(response_data))

           

_client: WaterpointClient | None = None
_client_lock = asyncio.Lock()
_client_started = False


async def get_client(base_url: str = "https://webapi.waterpointsmonitoring.net",  timeout: float = 30.0) -> WaterpointClient:
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
from __future__ import annotations

from typing import Any, Awaitable, Callable
from lswms_sdk.utils import parse_name
from lswms_sdk.lswms_client import  WaterpointClient

#CachedGet = Callable[..., Awaitable[Any]]
#GetClient = Callable[..., Awaitable[Any]]

#def register_tools(mcp, cached_get: CachedGet, ctx, get_client: GetClient) -> None:
def register_tools(mcp, client: WaterpointClient) -> None:
    # ═══════════════════════════════════════════════════════════════════════════
    # ADMINISTRATIVE REGIONS AND WATERPOINTS 
    # ═══════════════════════════════════════════════════════════════════════════

    @mcp.tool(name="find_administrative_zone_by_name",
            description="Search for administrative zones level 1 (zones) by name.")
    async def find_administrative_zone_by_name(zone_name: str) -> list[object]:
        adm1_data = await client.get_Adm1()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in adm1_data]
        matched_dicts = parse_name(dict_data,zone_name)
        if not matched_dicts:
            return []
        return matched_dicts


    @mcp.tool(name="find_administrative_districts_by_zone",
            description="Search for administrative district level 2 (district or woreda) by zone name.")
    async def find_administrative_districts_by_zone(zone_name: str) -> list[object]:
        adm1_data = await find_administrative_zone_by_name(zone_name)
            
        if not adm1_data:
            return []
        zone_id =  adm1_data[0]['id']
        districts = await client.get_adm2_by_adm1_ids(zone_id)
        return districts
    #Got to be reviewd 
    # @mcp.tool(name="search_waterpoints_by_district",
    #         description="Get details of a waterpoints available in the database searched by district name use this to search for status of waterpoints in a zone")
    # async def search_waterpoints_by_district(district_name: str) -> list[object]:
    #     wp_data = await client.get_waterpoints() #model list data
    #     dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
    #     matched_dicts = parse_name(dict_data,district_name,district=True)
    #     if not matched_dicts:
    #         return []
    #     # Return structured Pydantic objects 
    #     return matched_dicts 
    
    @mcp.tool(name="search_waterpoints_by_name",
            description="Get a waterpoint available in the database searched by name")
 
    async def search_waterpoints_by_name(waterpoint_name: str) -> list[object]:
        wp_data = await client.get_waterpoints()
        
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        
        matched_dicts = parse_name(dict_data, waterpoint_name)
        if not matched_dicts:
            return []

        return matched_dicts
    
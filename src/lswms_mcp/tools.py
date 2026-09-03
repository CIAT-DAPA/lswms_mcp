from __future__ import annotations

from typing import Any, Awaitable, Callable
from lswms_sdk.utils import parse_name
from lswms_sdk.lswms_client import  WaterpointClient
from lswms_sdk.lswms_models import Waterpoints,Monitored,Adm1,Adm2,SubseasonalForecast
from lswms_sdk.context_builder import ContextBuilder  


#CachedGet = Callable[..., Awaitable[Any]]
#GetClient = Callable[..., Awaitable[Any]]

#def register_tools(mcp, cached_get: CachedGet, ctx, get_client: GetClient) -> None:
def register_tools(mcp, client: WaterpointClient, ctx: ContextBuilder) -> None:
    # ═══════════════════════════════════════════════════════════════════════════
    # ADMINISTRATIVE REGIONS AND WATERPOINTS 
    # ═══════════════════════════════════════════════════════════════════════════

    @mcp.tool(name="find_administrative_zone_by_name",
            description="Search for administrative zones level 1 (zones) by name.")
    async def find_administrative_zone_by_name(zone_name: str) -> dict:
        adm1_data = await client.get_Adm1()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in adm1_data]
        matched_dicts = parse_name(dict_data,zone_name)
        if not matched_dicts:
            return []
        return matched_dicts


    @mcp.tool(name="find_administrative_districts_by_zone",
            description="Search for administrative district level 2 (district or woreda) by zone name.")
    async def find_administrative_districts_by_zone(zone_name: str) -> list[dict]:
        adm1_data = await find_administrative_zone_by_name(zone_name)
            
        if not adm1_data:
            return [{"Not Found": f"a zone named '{zone_name}'"}]
        zone_id =  adm1_data[0]['id']
        districts = await client.get_adm2_by_adm1_ids(zone_id)
        districts_dict = [d.model_dump() if hasattr(d, "model_dump") else d for d in districts]
        return districts_dict
  
    @mcp.tool(name="search_waterpoints_by_district",
            description="Get details of a waterpoints available in the database searched by district name use this to search for status of waterpoints in a zone")
    async def search_waterpoints_by_district(district_name: str) -> list[Waterpoints]:
        wp_data = await client.get_waterpoints() #model list data
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data,district_name,district=True)
        if not matched_dicts:
            return [{"Not Found": f"a district named '{district_name}'"}]
        # Return structured Pydantic objects 
        return [Waterpoints(**d) for d in matched_dicts]
    
    @mcp.tool(name="search_waterpoints_by_name",
            description="Get a waterpoint available in the database searched by name")
 
    async def search_waterpoints_by_name(waterpoint_name: str) -> str:
        wp_data = await client.get_waterpoints()
        
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        
        matched_dicts = parse_name(dict_data, waterpoint_name)
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint= waterpoint_name)
        data =[Waterpoints(**d) for d in matched_dicts]
        return ctx.waterpoint_summary(waterpoint=data)    
    @mcp.tool(name="get_seasonal_forecast",
              description = "Retrieve the seasonal forecast for a specific waterpoint using its name, where forecast probabilities are provided as values ranging from 0 to 1 for Below-Normal, Normal, and Above-Normal conditions.")
    async def get_seasonal_forecast(waterpoint_name:str)->str:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint=waterpoint_name)
        sesonal_fxt = await client.get_seasonal_forecast(matched_dicts[0]['id'])
        waterpoint_name_db = matched_dicts[0]['name']
        data =  [sesonal_fxt.model_dump()]
        return ctx.seasonal_summary(seasonal=data,waterpoint_name=waterpoint_name_db) 

    @mcp.tool(name="get_subseasonal_forecast",
              description = "Retrieve the subseasonal forecast represented from week 1 to week 4 for a specific waterpoint using its name, where forecast probabilities are provided as values ranging from 0 to 1 for Below-Normal, Normal, and Above-Normal conditions.")
    async def get_subseasonal_forecast(waterpoint_name:str)->str:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint=waterpoint_name)
        
        subseasonal_fxt = await client.get_subseasonal_forecast(matched_dicts[0]['id'])
        waterpoint_name_db = matched_dicts[0]['name']
        data = [subseasonal_fxt.model_dump()]
        return ctx.subseasonal_summary(subseasonal=data,waterpoint_name=waterpoint_name_db)

    @mcp.tool(name="get_waterpoint_profile",
              description="get a waterpoint profile from the available dataset using the waterpoint name")
    async def get_waterpoint_profile(waterpoint_name: str) -> list:
        # Get list of all waterpoints to find the ID by name
        wp_data = await client.get_waterpoints()
        
        # Convert models to dicts for the parse_name utility
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint=waterpoint_name)
        #context_builder will handle the agri_contexts
        #profile_contexts = ['Water use and management','Demographic characteristics','Location'] 
        waterpoint_name_db = matched_dicts[0]['name']
        profile = await client.get_waterpoint_profile(matched_dicts[0]["id"])
        
        data = [profile.model_dump()]
        return ctx.profile_summary(data,waterpoint_name=waterpoint_name_db)
    #observation
    @mcp.tool(name="get_daily_observation_series",
              description = "Retrieve the daily sereis of records on waterpoint depth, scaled depth, rainfall and evapotranspiration data for a specific waterpoint using the waterpoint name")
    async def get_daily_observation_series(waterpoint_name:str)->dict:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return [{"Not Found": f"waterpoint named '{waterpoint_name}'"}]
        
        dialy_data = await client.get_daily_observations(matched_dicts[0]['id'])
        #TODO
        #return with details and summary the context_builder will handle this
    
       
        return dialy_data

    @mcp.tool(name="get_current_observations",
              description = "Retrieve the latest monitoring of the waterpoint depth, scaled depth, rainfall and evapotranspiration data for a specific waterpoint using the waterpoint name")
    async def get_current_observations(waterpoint_name:str)->dict:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return [{"Not Found": f"waterpoint named '{waterpoint_name}'"}]
        
        latest_data = await client.get_current_observations(matched_dicts[0]['id'])
        #TODO
        #return with the context builder  
       
        return latest_data
    @mcp.tool(name="get_waterpoint_status",
              description="Retrieves the current status and associated advisory of a waterpoint based on its name")
    async def get_waterpoint_status(waterpoint_name:str,language:str="en",)->dict:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
                
        if not matched_dicts:
            return [{"Not Found": f"waterpoint named '{waterpoint_name}'"}]
        advisory_data = await client.get_waterpoint_status(matched_dicts[0]["id"])

        #TODO return with the context builder with STATUS and ADVISORY contexts 
        
        return advisory_data
from __future__ import annotations

from typing import Any, Awaitable, Callable
from lswms_sdk.utils import parse_name,date_str
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

    @mcp.tool(name="get_zone_with_waterpoints",
            description="returns adminstrative zone where waterpoints are presernt. Search by zone name.")
    async def get_zone_with_waterpoints(zone_name: str) -> dict:
        adm1_data = await client.get_Adm1()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in adm1_data]
        matched_dicts = parse_name(dict_data,zone_name)
        if not matched_dicts:
            return ctx.t("no_zone", zone_name=zone_name)
        # return matched_dicts
        return ctx.zone_summary(matched_dicts[0],zone_name=matched_dicts[0]['name'])


    @mcp.tool(name="get_districts_with_waterpoints", 
            description="Returns a list of districts within a specified zone where waterpoints are present. This tool helps identify the administrative districts that contain one or more recorded waterpoints in the selected zone")
    async def get_districts_with_waterpoints(zone_name: str) -> str: #
        adm1_data = await client.get_Adm1()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in adm1_data]
        matched_dicts = parse_name(dict_data,zone_name)
            
        if not matched_dicts:
            return ctx.t("no_zone", zone_name=zone_name)
        zone_id =  matched_dicts[0]['id']
        districts = await client.get_adm2_by_adm1_ids(zone_id)
        districts_dict = [d.model_dump() if hasattr(d, "model_dump") else dict(d) for d in districts]
        # return districts_dict
        return ctx.districts_summary(districts_dict,zone_name=matched_dicts[0]['name'])  
  
    @mcp.tool(name="get_waterpoints_by_district",
            description="Get details of a waterpoints available in the database searched by district name use this to search for status of waterpoints in a district")
    async def get_waterpoints_by_district(district_name: str) -> str: #list[Waterpoints]
        wp_data = await client.get_waterpoints() #model list data
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data,district_name,district=True)
        if not matched_dicts:
            return [{"Not Found": f"a district named '{district_name}'"}]
        # Return structured Pydantic objects 
        data = [Waterpoints(**d) for d in matched_dicts]
        return ctx.waterpoints_in_district_summary(data,district_name=matched_dicts[0]['adm2'])
    
    @mcp.tool(name="get_waterpoints_by_name",
            description="Get a waterpoint available in the database searched by name")
 
    async def get_waterpoints_by_name(waterpoint_name: str) -> str:
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
              description = "Retrieve daily waterpoint monitoring records for a specified waterpoint, including water depth, scaled depth, rainfall, and evapotranspiration measurements. The query requires the waterpoint name, start year, and end year as inputs and returns all daily observations within the selected date range. To maintain performance and avoid excessive data retrieval, limit requests to a maximum of three years of data whenever possible")
    async def get_daily_observation_series(waterpoint_name:str, start_year:int,end_year:int)->dict:
        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"
        if end_year - start_year > 3:
            return ctx.t("date_range_exceeded", start_year=start_year, end_year=end_year)
        start_date = date_str(start_date)
        end_date = date_str(end_date)
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint=waterpoint_name)        
        daily_data = await client.get_daily_observations(matched_dicts[0]['id'])
        return ctx.daily_row(daily_data,start_date=start_date,end_date=end_date,waterpoint_name=matched_dicts[0]['name'])       

    @mcp.tool(name="get_waterpoint_climatology",
              description = "Retrieve the climatology of waterpoint depth, scaled depth, rainfall and evapotranspiration data for a specific waterpoint using the waterpoint name")
    async def get_waterpoint_climatology(waterpoint_name:str)->dict:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint=waterpoint_name)        
        daily_data = await client.get_daily_observations(matched_dicts[0]['id'])
        #return with details and summary the context_builder will handle this
        return ctx.climatology_summary(daily_data,waterpoint_name=matched_dicts[0]['name'])       
        # return daily_data_dict

    @mcp.tool(name="get_current_observations",
              description = "Retrieve the latest monitoring of the waterpoint depth, scaled depth, rainfall and evapotranspiration data for a specific waterpoint using the waterpoint name")
    async def get_current_observations(waterpoint_name:str)->dict:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        
        if not matched_dicts:
        #     # return [{"Not Found": f"waterpoint named '{waterpoint_name}'"}]
            return ctx.t("no_waterpoint", waterpoint_name)
        
        latest_data = await client.get_current_observations(matched_dicts[0]['id'])
        waterpoint_name_data = matched_dicts[0]['name']
        #return with the context builder  
        return ctx.monitoring_summary(latest_data,waterpoint_name=waterpoint_name_data)
        # return latest_data #returns list originally 
    @mcp.tool(name="get_waterpoint_status",
              description="Retrieves the current waterpoint status and associated advisory of a waterpoint based on its name")
    async def get_waterpoint_status(waterpoint_name:str,language:str="en",)->str:
        wp_data = await client.get_waterpoints()
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
                
        if not matched_dicts:
            return (ctx.t("no_waterpoint", waterpoint=waterpoint_name))
        advisory_data = await client.get_waterpoint_status(matched_dicts[0]["id"])
        waterpoint_name_db = matched_dicts[0]['name']

        #TODO return with the context builder with STATUS and ADVISORY contexts
        # return type(advisory_data)
        return ctx.advisory_summary(advisory=advisory_data,waterpoint_name = waterpoint_name_db) 
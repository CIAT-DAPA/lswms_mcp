from __future__ import annotations

from ast import pattern
from typing import Any, Awaitable, Callable
from lswms_sdk.utils import parse_name,date_str,parse_waterpoint_status,parse_zone_name
from lswms_sdk.lswms_client import  WaterpointClient
from lswms_sdk.lswms_models import Waterpoints,Monitored,Adm1,Adm2,SubseasonalForecast
from lswms_sdk.context_builder import ContextBuilder  
import re
import numpy as np 
from typing import Union, List
import json 
from collections import OrderedDict

#CachedGet = Callable[..., Awaitable[Any]]
#GetClient = Callable[..., Awaitable[Any]]

#def register_tools(mcp, cached_get: CachedGet, ctx, get_client: GetClient) -> None:
def register_tools(mcp, client: WaterpointClient, ctx: ContextBuilder) -> None:
    # ═══════════════════════════════════════════════════════════════════════════
    # ADMINISTRATIVE REGIONS AND WATERPOINTS 
    # ═══════════════════════════════════════════════════════════════════════════
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

    @mcp.tool(name="get_waterpoints_by_zone",
            description="Get details of a waterpoints available in the database searched by zone name use this to search for status of waterpoints in a zone")
    async def get_waterpoints_by_zone(Zone_name: str) -> str: #list[Waterpoints]
        wp_data = await client.get_waterpoints() #model list data
        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_zone_name(dict_data,Zone_name)
        if not matched_dicts:
            return [{"Not Found": f"a Zone named '{Zone_name}'"}]
        # Return structured Pydantic objects 
        data = [Waterpoints(**d) for d in matched_dicts]
        return ctx.waterpoints_in_zone_summary(data,Zone_name=matched_dicts[0]['adm1'])

    @mcp.tool(name="get_waterpoints_by_district",
            description="""Returns all waterpoints within a district regardinless of status.  Use this tool ONLY when a district is specified and the user wants a list or count of waterpoints.
            Examples:
            - List waterpoints in 'XX' District.
            - Show all waterpoints in 'XX' District.
            - How many waterpoints are in 'XX' District
            Do NOT use this tool if the user mentions:dry, watch, alert, good other status condition. 
            In those cases use get_waterpoint_status_in_district."""
            )
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
            description = '''Retrieve the seasonal rainfall forecast or climate outlook for a specific waterpoint using its name. 
                Use this tool when the user asks about seasonal forecasts, rainfall outlooks, precipitation outlooks, 
                climate outlooks, or expected future conditions. Returns the probabilities (0 to 1) of Below-Normal, Normal, and Above-Normal rainfall conditions for the forecast season''')
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
            description = '''Get the subseasonal rainfall forecast for a waterpoint. Use this tool when the user asks for:subseasonal forecast
            subseasonal rainfall forecast, precipitation outlook, weather outlook, weekly forecast,week 1, week 2, week 3, or week 4 forecast, forecast for the next four weeks
            Returns the probabilities of Below-Normal, Normal, and Above-Normal rainfall conditions for weeks 1 through 4 at the specified waterpoint.''')
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
              description='''Retrieve a comprehensive waterpoint profile using the waterpoint name. 
              Use this tool when the user asks about a waterpoint's characteristics, community context, 
              land use, livelihoods, demographics, water use, water management, agriculture, livestock production, or watershed conditions. 
              Returns information on Land Use and Livelihood Dynamics, Demographic Characteristics, Water Use and Management Practices, Agricultural Context, Livestock Systems, and Watershed Description for the specified waterpoint.''')
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
              description = "Retrieve daily waterpoint monitoring records for a specified waterpoint, including water depth, scaled depth, rainfall, and evapotranspiration measurements. " \
              "The query requires the waterpoint name, start year, and end year as inputs and returns all daily observations within the selected date range. " \
              "To maintain performance and avoid excessive data retrieval, limit requests to a maximum of three years of data whenever possible")
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
    @mcp.tool(name="get_waterpoint_status_in_district",
        description=(
                    "Get waterpoints in a district filtered by status. Use this tool"
                    " whenever the user asks about waterpoints with a specific status"
                    " within a district.\nExamples:\n- Which waterpoints are dry in"
                    " Yabello District?\n- Show dry waterpoints in Dire"
                    " District.\n- List functional waterpoints in XX.\n- How many"
                    " DRY waterpoints are in XX District?\nPrefer this tool over"
                    " get_waterpoints_by_district when the query contains status terms"
                    " such as: DRY, GOOD, ALERT, WATCH and SEASONLY DRY."
                ))
    async def get_waterpoint_status_in_district(district_name:str,status: Union[str, List[str]])->str:
        
        if isinstance(status, str):
            status = [status]
        #clean the status call        
        cleaned_status = []
        
        for s in status:
            parsed = parse_waterpoint_status(s)
            if isinstance(parsed, list):
                cleaned_status.extend(parsed)
            else:
                cleaned_status.append(parsed)
                    
            # Normalize cleaned_status items to uppercase for consistent comparison
        cleaned_status = [str(s).upper() for s in cleaned_status]
        

        wp_in_districts = await get_waterpoints_by_district(district_name)
        if not wp_in_districts:
            return json.dumps({"tell_user": f"Could not find a district named '{district_name}' in the database."})
        waterpoints = re.findall(r'Waterpoint Name:\s*([^\n]+)', wp_in_districts)
        kebeles = re.findall(r'Kebel:\s*([^\n]+)', wp_in_districts)

        
        waterpoints = [wp.strip() for wp in waterpoints]
        kebeles = [d.strip() for d in kebeles]
        waterpoint_kebele_map = dict(zip(waterpoints, kebeles))
        
        #tyde the waterpoint 
        wp_status_in_district = []
        available_status = []

        for waterpoint in waterpoints:

            waterpoint_status = await get_waterpoint_status(waterpoint)

            if not waterpoint_status:
                continue

            waterpoint_status = str(waterpoint_status)

            status_match = re.findall(r'Status:\s*([^\n]+)', waterpoint_status,flags=re.IGNORECASE )

            if not status_match:
                continue

            current_status = status_match[0].strip().upper()
            kebele_ = waterpoint_kebele_map.get(waterpoint)
            if current_status in cleaned_status:
                wp_status_in_district.append({"waterpoint": waterpoint, "kebele": kebele_, "status": current_status })
            # else:
            #     available_status.append({"waterpoint": waterpoint, "status": current_status})
        if wp_status_in_district:  
            response_data = {
                "Title": "Waterpoint Status",
                "waterpoints": wp_status_in_district
            }
            return json.dumps(response_data,indent=2)
        else:
            available_status.insert(0,{"tell_user": f"No waterpoints are currently available with the status '{cleaned_status}'" })
            return json.dumps(available_status,indent=2)
    @mcp.tool(name="compare_district_waterpoint_status",
             description=(
                    "use this tool to compare two districts waterpoints in a specific status." 
                    "Status must be one of GOOD, ALERT, WATCH, or DRY. Infer the status from the user's wording:. Use this tool"
                    " GOOD = healthy, normal, adequate water availability"
                    " WATCH = caution, declining conditions, monitor closely"
                    "ALERT = stressed, concerning conditions, low water availability "
                    " NEAR DRY = dry, critical, failed, no water available"
                    " DRY waterpoints are in XX District?\nPrefer this tool over"

                ))
    async def compare_district_waterpoint_status(district_name1:str,district_name2:str,status: Union[str, List[str]])->str:
        district_name1_return = await get_waterpoint_status_in_district(district_name1,status)
        district_name2_return = await get_waterpoint_status_in_district(district_name2,status)
        if district_name1_return and district_name2_return:
            return json.dumps({
                "district_1": { "name": district_name1, "waterpoints": district_name1_return },
                "district_2": { "name": district_name2, "waterpoints": district_name2_return }
            }, indent=2)
        else:
            return json.dumps ({"tell_user": "the districts may not be found in the system"}
            )
    @mcp.tool(name="get_waterpoint_statistics_by_zone",
            description="Retrieves a zone-level statistical summary of waterpoint conditions (counts for GOOD, ALERT, WATCH, and NEAR DRY statuses) for a specified geographic zone. Use this tool when the user asks for a summary of waterpoint conditions in a zone, including counts of waterpoints in each status category. This tool provides an overview of the current state of waterpoints within the selected zone, helping to identify areas with potential water scarcity or stress.")
    async def get_waterpoint_statistics_by_zone(zone_name: str, status: List[str] = ["GOOD","ALERT","WATCH","NEAR DRY"]) -> str:
        # if isinstance(status, str):
        #     status = [status]
        
        # Clean the status call        
        cleaned_status = []
        for s in status:
            parsed = parse_waterpoint_status(s)
            if isinstance(parsed, list):
                cleaned_status.extend(parsed)
            else:
                cleaned_status.append(parsed)
        
        # Normalize cleaned_status items to uppercase
        cleaned_status = [str(s).upper() for s in cleaned_status]

        wp_in_zone = await get_waterpoints_by_zone(zone_name)
        if not wp_in_zone:
            return json.dumps({"tell_user": f"Could not find a Zone named '{zone_name}' in the database. Please check the spelling and try again."})
        
        # Extract waterpoint names and their corresponding districts
        waterpoints = re.findall(r'Waterpoint Name:\s*([^\n]+)', wp_in_zone)
        districts = re.findall(r'District:\s*([^\n]+)', wp_in_zone)
        waterpoints = [wp.strip() for wp in waterpoints]
        districts = [d.strip() for d in districts]
        
        # Create a mapping of waterpoint to district
        waterpoint_district_map = dict(zip(waterpoints, districts))
        
        wp_status_in_district = []
        available_status = []
        
        for waterpoint in waterpoints:
            waterpoint_status = await get_waterpoint_status(waterpoint)
            if not waterpoint_status:
                continue

            waterpoint_status = str(waterpoint_status)
            status_match = re.findall(r'Status:\s*([^\n]+)', waterpoint_status, flags=re.IGNORECASE)

            if not status_match:
                continue

            current_status = status_match[0].strip().upper()
            district = waterpoint_district_map.get(waterpoint, "Unknown")

            if current_status in cleaned_status:
                wp_status_in_district.append({"district": district, "waterpoint": waterpoint, "status": current_status})
            else:
                available_status.append({"district": district, "waterpoint": waterpoint, "status": current_status})
        
        if wp_status_in_district:             
            return json.dumps(wp_status_in_district, indent=2)
        else:
            available_status.insert(0, {"tell_user": f"No waterpoints found with status '{', '.join(cleaned_status)}'. Available statuses shown below."})
            return json.dumps(available_status, indent=2)

    #Spatial & Proximity Queries   
    @mcp.tool(name="get_nearby_waterpoints",
    description = "Find waterpoints near a specified waterpoint. "
        "The search radius is optional and defaults to 40 km when not specified by the user.")
    async def get_nearby_waterpoints(waterpoint_name:str, radius_km: float=40.0) -> str:
        wp_data = await client.get_waterpoints() #model list data

        dict_data = [item.model_dump() if hasattr(item, "model_dump") else item for item in wp_data]
        matched_dicts = parse_name(dict_data, waterpoint_name)
        if not matched_dicts:
            return ctx.t("no_waterpoint", waterpoint= waterpoint_name)
        coords_rad = np.radians([[item["lon"], item["lat"]] for item in dict_data])
        target_rad = np.radians([[item["lon"], item["lat"]] for item in matched_dicts][0])
        matched_waterpoint_name = matched_dicts[0]["name"]
        dlon = coords_rad[:, 0] - target_rad[0]
        dlat = coords_rad[:, 1] - target_rad[1]
        a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(target_rad[1])
        * np.cos(coords_rad[:, 1])
        * np.sin(dlon / 2.0) ** 2
         )
        c = 2 * np.arcsin(np.sqrt(a))

        earth_radius_km = 6371.0
        distances_km = earth_radius_km * c
        nearest_5_indices = np.argsort(distances_km)[:5]
        nearest_5_items = []
        for i in nearest_5_indices:
            item_with_dist = {**dict_data[i], "distance_km": round(float(distances_km[i]), 2)}
            nearest_5_items.append(item_with_dist)
        final_nearby_waterpoints = [item for item in nearest_5_items if item["distance_km"] <= radius_km and item["name"] != matched_waterpoint_name]
        keys_to_keep = {"name","adm3","distance_km"}
        filtered_nearby_waterpoints = []
        for items in final_nearby_waterpoints:
            filtered = {k: items[k]  for k in keys_to_keep if k in items}
            filtered['kebele'] = filtered.pop("adm3")
            filtered_nearby_waterpoints.append(filtered)
        if not filtered_nearby_waterpoints:
            return json.dumps({"tell_user": f"No waterpoints found within {radius_km} km of the specified location."})
        
        return json.dumps(filtered_nearby_waterpoints, indent=2)
    @mcp.tool(
        name="get_nearby_waterpoints_with_status",
        description= "Find waterpoints near a specified waterpoint that match a given status "
        "(GOOD, WATCH, ALERT, or DRY). The search radius is optional and defaults to 40 km when not specified."
    )
    async def get_nearby_waterpoints_with_status(waterpoint_name: str, status:str, radius_km: float=40.0) -> str:
        nearby_waterpoints = await get_nearby_waterpoints(waterpoint_name, radius_km)
        if not nearby_waterpoints:
            return json.dumps({"tell_user": f"No nearby waterpoints found within {radius_km} km of {waterpoint_name}."})
        if isinstance(nearby_waterpoints, str):
            nearby_waterpoints = json.loads(nearby_waterpoints)

        wanted = status.strip().lower()
        matched_waterpoints = []

        for item in nearby_waterpoints:
            name = item.get("name")
            if not name:
                continue
            raw_status = str(await get_waterpoint_status(name))
            pattern = rf'{re.escape(name)}\s+Status:\s*([^\r\n]+)'
            status_match = re.search(pattern, raw_status, flags=re.IGNORECASE)
            if not status_match:
                continue
            current = status_match.group(1).strip()
            if current.lower() == wanted:
                item["status"] = current.upper()
                matched_waterpoints.append(item)

        if not matched_waterpoints:
            return json.dumps({
                "tell_user": f"Couldn't find waterpoints with status '{status}' within {radius_km} km of {waterpoint_name}."
            }, indent=2)

        summary = {"tell_user": f"Waterpoints matching status '{status.upper()}' found: {len(matched_waterpoints)}"}
        return json.dumps([summary] + matched_waterpoints, indent=2)
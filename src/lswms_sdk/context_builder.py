"""
Waterpoint SDK contextBuilder.
transform API resoposes into LLM-readable narrative context.
The builder supports multiple output languages through lighweight templates.

"""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Literal

from lswms_sdk.lswms_models import (
    Adm2,Adm3,Advisory,Monitored,Waterpoints,SubseasonalForecast,SeasonalForecast
)

SupportedLanguage = Literal["en"]
MONTH_NAMES : dict[str, dict[int, str]] = {
    "en": {
                1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
        }
}
SEASONS : dict[str, dict[int, str]] = {
    "en": {
                1: "December-to-Feburary", 2: "January-to-March", 3: "Feburary-to-April", 4: "March-to-May",
        5: "April-to-June", 6: "May-to-July", 7: "June-to-August", 8: "July-to-September",
        9: "August-to-October", 10: "September-to-November", 11: "October-to-December", 12: "November-to-January",
        }
}
PROFILE_CONTEXTS:dict[str,list[str]|str] = {'general': ['Water use and management','Demographic characteristics','Location'],'livstock_populn':'agriculture context livestock'}
TEXT:dict[str,dict[str,str|list[str]]] = {"en": {
        "waterpoint_title":"Waterpoint Description",
        "name":"Waterpoint Name",
        "adm1":"Zone",
        "adm2": "District",
        "adm3":"Kebel",
        "area": "Area in hectars",
        "lat" : "Latitude",
        "lon" : "Longitude",     
        "coordinates": "Coordinates",
        "no_zone" : "Not Found  a zone named {zone_name} in the platform",
        "no_waterpoint" : "Not Found  a waterpoint named {waterpoint} in the platform",   
        "no_current_data": "No recent monitoring data was found.",
        "subseasonal_title": "Subseasonal forecast for waterpoint {waterpoint}",
        "seasonal_title": "Sasonal forecast for waterpoint {waterpoint}",
        "profile_title" :"{waterpoint} Waterpoint profile",
        "agriculture context livestock":"Livestock Population by Species",
        "measure":"Rainfall Outlook",
        "lower":"Below Normal",
        "normal":"Normal",
        "upper":"Above Normal",
        "GOOD": {
        "pastoralists": [
          "Proper management of water use for other purposes is recommended.",
          "Utilize available water resources responsibly while avoiding unnecessary wastage.",
          "Avoid overconcentration of livestock in a single area to reduce pressure on surrounding rangelands",
          "Continue regular watering schedules to maintain livestock productivity and health.",
          "Protect waterpoint from contamination by restricting livestock access to designated watering places.",
          "Conserve water where feasible to build resilience for future dry periods"
        ],
        "extension_agents": [
          "Encourage balanced livestock distribution across available grazing and watering areas to prevent localized degradation.",
          "Educate pastoralists on the importance of clean water sources and proper sanitation to prevent waterborne diseases among livestock",
          "Use this favorable period to strengthen drought preparedness and community water management practices",
          "Recommended use of efficient irrigation techniques to minimize water wastage and ensure sustainable water management",
          "Participate in the community routine cleaning, maintenance, and protection of water infrastructure."
        ]        
      },
      "WATCH" :{
        "pastoralists": [
          "It is advisable to reduce pond water use for other purposes",
          "Follow community watering schedules to ensure equitable access.",
          "Reduce prolonged livestock stays at the water point.",
          "Participate in protecting the waterpoint from contamination and infrastructure damage"
        ],
        "extension_agents": [
          "Alert communities the waterpoint is declining and promote early water conservation measures.",
          "Support community water committees in implementing water-use regulations.",
          "Increase monitoring of water levels, water quality, and livestock pressure around the waterpoint"
        ]
      },
          
      "ALERT":{
        "pastoralists": [
          "Follow the community water-use schedule strictly to prevent rapid depletion of the remaining water.",
          "Prioritize watering weak, lactating, pregnant, and young animals before healthy adult livestock.",
          "Consider moving part of the herd to alternative grazing and watering areas where available.",
          "Regularly monitor livestock health and notify local leaders or extension agents if water shortages begin affecting animal condition"
        ],
        "extension_agents": [
          "Advise pastoralists to prioritize vulnerable livestock groups and implement livestock segregation where necessary.",
          "Utilize the EIAR Rangeland Monitoring portal to identify and map out alternative water sources and grazing areas.",
          "Support pastoralists and agro-pastoralists in exploring alternative water sources such as groundwater wells, water trucking, community water supply schemes or accessing emergency livestock watering points to meet immediate water needs.",
          "Prepare contingency plans in case the waterpoint rapidly declines to emergency levels"
        ]
      },
      "NEAR-DRY": {
        "pastoralists": [
          "Reserve the remaining pond water for drinking purposes and critical livestock needs",
          "Initiate emergency measures such as rationing water",
          "Strictly follow community water rationing schedules to extend the availability of the remaining water supply.",
          "Migrate to areas with better water and grazing availability with community leaders and authorities guidance.",
          "Maintain good hygiene practices around the waterpoint to reduce the risk of waterborne diseases."
        ],
        "extension_agents": [
          "Coordinate with the District and Regional DRM Office to communicate the severity of the water shortage and support emergency response planning.",
          "Facilitate and monitor livestock and pastoralist migration to identified areas with available water and pasture while minimizing resource-use conflicts.",
          "Support community water committees in implementing and enforcing water rationing measures",
          "Conduct intensive hygiene and sanitation awareness campaigns with Health Extension Workers to prevent waterborne diseases.",
          "Coordinate with local authorities or humanitarian organizations to facilitate access to emergency water sources",
          "Involve local communities in pond restoration efforts through participatory planning, awareness-raising campaigns, and capacity-building workshops on water conservation and sustainable land management practices"
        ]
      },
      "SEASONALY-DRY": {
          "pastoralists": [
          "Organize remaining community members to clean, desilt, and repair the pond in preparation for the next rainy season.",
          "Support elderly people, women, children, and vulnerable households who remain in the settlement while other family members migrate with livestock.",
          "protect the communal water sources from contamination and overuse.",
          "Explore alternative livelihood activities"
        ],
        "extension_agents": [
          "Provide guidance on sanitation and hygiene practices to minimize health risks.",
          "Mobilize the community to clean, desilt, and repair the pond in preparation for the next rainy season.",
          "Coordinate emergency water supply interventions including water trucking.",
          "Conduct maintenance and repair work on waterpoints during dry periods to ensure they are ready to capture and store water when rainfall returns.",
          "Involve local communities in pond restoration efforts through participatory planning, awareness-raising campaigns, and capacity-building workshops on water conservation and sustainable land management practices"
        ]
      }
      },
}
class ContextBuilder:
    """Convert waterpoint API responses into LLM-readable text.

    Parameters
    ----------
    language:
       Supported value is ``"en"`` 
    """

    def __init__(self, language: SupportedLanguage = "en") -> None:
        self.language = self._normalize_language(language)

    @staticmethod
    def _normalize_language(language: str) -> SupportedLanguage:
        normalized = language.lower().split("-")[0]
        if normalized not in TEXT:
            supported = ", ".join(sorted(TEXT))
            raise ValueError(f"Unsupported language '{language}'. Supported languages: {supported}")
        return normalized  # type: ignore[return-value]

    def with_language(self, language: SupportedLanguage) -> "ContextBuilder":
        """Return a new builder with the requested language."""
        return ContextBuilder(language=language)

    def set_language(self, language: SupportedLanguage) -> None:
        """Update the builder output language in place."""
        self.language = self._normalize_language(language)

    @property
    def months(self) -> dict[int, str]:
        return MONTH_NAMES[self.language]

    def t(self, key: str, **kwargs: Any) -> str:
        return TEXT[self.language][key].format(**kwargs)

    def _location_name(self, location_name: str | None, location_id: int) -> str:
        return location_name or self.t("location_fallback", id=location_id)

    # forecast summary
    def subseasonal_summary(self, subseasonal: list[dict] | dict, waterpoint_name:str)->str:
        if not subseasonal:
            return self.t("no_waterpoint", waterpoint=waterpoint_name)

        lines = [self.t("subseasonal_title", waterpoint=waterpoint_name)]
        for c in subseasonal:
            year = c.get("year")
            month = c.get("month")
            if month and year:
                lines.append(f"{MONTH_NAMES['en'][month]} {year}")
            lines.append(f"{self.t('measure')}")
            weeks = (c.get("weeks"))
            for wk_val in weeks:
                if wk_val.get("week"):
                    lines.append(f"Week {wk_val['week']}")
                if wk_val.get("lower") is not None:
                    lines.append(f" {self.t('lower')} : {wk_val['lower'] * 100:.2f}%")

                if wk_val.get("normal") is not None:
                    lines.append(f" {self.t('normal')} : {wk_val['normal'] * 100:.2f}%")

                if wk_val.get("upper") is not None:
                    lines.append(f" {self.t('upper')} : {wk_val['upper'] * 100:.2f}%")
        return (("\n").join(lines))
            
    def seasonal_summary(self, seasonal: list[dict] | dict, waterpoint_name: str) -> str:

        if not seasonal:
            return self.t("no_waterpoint", waterpoint=waterpoint_name)

        lines = [self.t("seasonal_title", waterpoint=waterpoint_name)]

        for c in seasonal:
            month = c.get("month")
            year = c.get("year")
            if month and year:
                lines.append(f"{SEASONS['en'][month]} {year}")

            if c.get("measure"):
                lines.append(f"{self.t('measure')}")

            if c.get("lower") is not None:
                lines.append(f" {self.t('lower')} : {c['lower'] * 100:.2f}%")

            if c.get("normal") is not None:
                lines.append(f" {self.t('normal')} : {c['normal'] * 100:.2f}%")

            if c.get("upper") is not None:
                lines.append(f" {self.t('upper')} : {c['upper'] * 100:.2f}%")

        return "\n".join(lines)
        # waterpoint metadata and profile
    def waterpoint_summary(self, waterpoint: list[Waterpoints]) -> str:
        if not waterpoint:
            return self.t("no_waterpoint")
        lines = [self.t("waterpoint_title")]
        # lines = [self.t("locations_found", count=len(waterpoint))]
        for loc in waterpoint:
            parts = [f" "] # - [{loc.id}] why the LLM need the id
            if loc.name:
                parts.append(f"  {self.t('name')}:{loc.name}")
            if loc.adm1:
                parts.append(f"    {self.t('adm1')}: {loc.adm1}")
            if loc.adm2:
                parts.append(f"    {self.t('adm2')}: {loc.adm2}")
            if loc.adm3:
                parts.append(f"    {self.t('adm3')}: {loc.adm3}")
            if loc.lat is not None and loc.lon is not None:
                parts.append(f"    {self.t('coordinates')}: {loc.lat:.f}, {loc.lon:.4f}")
            if loc.area:
                parts.append(f"    {self.t('area')}: {loc.area}")

            lines.extend(parts)
        return "\n".join(lines)
    #TODO summary to waterpoints in a district customize the aclimate locations   

    def profile_summary(self, profile: list[dict]|dict,waterpoint_name:str) -> str:
        if not profile:
            return self.t("no_waterpoint")
        lines = [self.t("profile_title",waterpoint=waterpoint_name.capitalize())]
        for c in profile:
            if c.get('contents_wp'):
                wp_contents = c.get('contents_wp')
                for contents in wp_contents:
                    if contents.get("title") in PROFILE_CONTEXTS['general']:
                        lines.append(contents.get("title"))
                        vals = contents.get("values")
                        for val in vals:
                            lines.append(val.get("content"))
                    elif contents.get("title") in PROFILE_CONTEXTS['livstock_populn']:
                        lines.append(self.t(contents.get("title")))
                        vals = contents.get("values")
                        for val in vals:
                            key = next(iter(val))
                            lines.append(f"{key}: {val[key]}")
 
                return"\n".join(lines)
    #Waterpoint dvisory
    #TODO link advisory summary with contexts in t for each STATUS


    
    #TODO summary to current monitoring
     

    # TODO time series records, climatology

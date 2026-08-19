import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Administrative Levels ---

class Adm1(BaseModel):
    id: Optional[str] = Field(None, description="Id Administrative level 1")
    ext_id: Optional[str] = Field(None, description="Extern Id to identify Administrative level 1")
    name: Optional[str] = Field(None, description="Administrative level 1 name")

class Adm2(BaseModel):
    id: Optional[str] = Field(None, description="Id Administrative level 2")
    adm1: Optional[str] = Field(None, description="Id Administrative level 1")
    ext_id: Optional[str] = Field(None, description="Extern Id to identify Administrative level 2")
    name: Optional[str] = Field(None, description="Administrative level 2 name")

class Adm3(BaseModel):
    id: Optional[str] = Field(None, description="Id Administrative level 3")
    adm2: Optional[str] = Field(None, description="Id Administrative level 2")
    ext_id: Optional[str] = Field(None, description="Extern Id to identify Administrative level 3")
    name: Optional[str] = Field(None, description="Administrative level 3 name")

class Woreda(BaseModel):
    id: Optional[str] = Field(None, description="Id of the Woreda")
    ext_id: Optional[str] = Field(None, description="External Id to identify the Woreda")
    name: Optional[str] = Field(None, description="Woreda Name")

# --- Advisory & PDF Models ---

class Advisory(BaseModel):
    advisory: Optional[str] = Field(None, description="status of the waterpoint", example="good")
    language: Optional[str] = Field(None, description="Language of the advisory text", example="en")
    waterpoints: Optional[str] = Field(None, description="waterpoint id", example="5f5e3e3e4f8b9461ac6ed74cb")

class AdvisoryPdfItem(BaseModel):
    name: Optional[str] = Field(None, description="Human readable title")
    description: Optional[str] = Field(None, description="PDF description")
    filename: Optional[str] = Field(None, description="Physical PDF file name")
    url: Optional[str] = Field(None, description="Public download URL")

class AdvisoryPdfGrouped(BaseModel):
    seasonal: Optional[List[AdvisoryPdfItem]] = None
    subseasonal: Optional[List[AdvisoryPdfItem]] = None

# --- Biomass & Trend Models ---

class Forecast(BaseModel):
    date: Optional[datetime.date] = Field(None, description="Date for the forecast")
    mean: Optional[float] = Field(None, description="Mean value for the forecast")

class Mean(BaseModel):
    mean: Optional[float] = Field(None, description="Mean value for the biomass")

class Trend(BaseModel):
    date: Optional[datetime.date] = Field(None, description="Date for the trend")
    mean: Optional[float] = Field(None, description="Mean value for the trend")

# --- Waterpoint Models ---

class WaterpointSimple(BaseModel):
    id: Optional[str] = Field(None, description="Id waterpoint")
    ext_id: Optional[float] = Field(None, description="external id of the waterpoint")
    name: Optional[str] = Field(None, description="waterpoint name")
    area: Optional[float] = Field(None, description="area of the waterpoint")
    lat: Optional[float] = Field(None, description="latitute of the waterpoint")
    lon: Optional[float] = Field(None, description="longitude of the waterpoint")
    watershed: Optional[str] = Field(None, description="Id watershed")

class Waterpoints(BaseModel):
    id: Optional[str] = Field(None, description="Id Waterpoints")
    ext_id: Optional[str] = Field(None, description="Extern Id to identify Waterpoint")
    name: Optional[str] = Field(None, description="Waterpoint name")
    adm1: Optional[str] = Field(None, description="Name of adm1")
    adm2: Optional[str] = Field(None, description="Name of adm2")
    adm3: Optional[str] = Field(None, description="Name of adm3")
    area: Optional[float] = Field(None, description="area of the Waterpoint")
    lat: Optional[float] = Field(None, description="latitude of the Waterpoint")
    lon: Optional[float] = Field(None, description="longityde of the Waterpoint")
    watershed: Optional[str] = Field(None, description="Id watershed")
    watershed_name: Optional[str] = Field(None, description="Name of the watershed")
    contents_wp: Optional[List[str]] = Field(None, description="List of contents associated with the waterpoint")
    contents_ws: Optional[List[str]] = Field(None, description="List of contents associated with the watershed")

class Monitored(BaseModel):
    id: Optional[str] = Field(None, description="Id Monitored data")
    date: Optional[str] = Field(None, description="Date of the monitored data")
    values: Optional[List[dict]] = Field(None, description="List of values of the monitored data")
    waterpoint: Optional[str] = Field(None, description="Id waterpoint")

# --- Waterpoint Forecast Models ---

class SeasonalForecast(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    measure: Optional[str] = None
    lower: Optional[float] = None
    normal: Optional[float] = None
    upper: Optional[float] = None

class SubseasonalWeekForecast(BaseModel):
    week: Optional[int] = None
    measure: Optional[str] = None
    lower: Optional[float] = None
    normal: Optional[float] = None
    upper: Optional[float] = None

class SubseasonalForecast(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    weeks: Optional[List[SubseasonalWeekForecast]] = None

class WaterpointForecast(BaseModel):
    waterpoint_id: Optional[str] = None
    waterpoint_name: Optional[str] = None
    seasonal: Optional[SeasonalForecast] = None
    subseasonal: Optional[SubseasonalForecast] = None

# --- User Subscription ---

class Subscription(BaseModel):
    userId: Optional[str] = Field(None, description="Id of the User")
    waterpoint: Optional[str] = Field(None, description="id to waterpoint to subscribe")
    boletin: Optional[str] = Field(None, description="Boletin to subscribe")
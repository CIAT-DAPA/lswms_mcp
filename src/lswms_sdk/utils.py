from __future__ import annotations

from datetime import date
from typing import Iterable, Any
import numpy as np
from rapidfuzz import process, fuzz
from typing import Optional, Union, List



def csv(value: str | int | Iterable[str | int]) -> str:
    """Convert scalar/list values into the comma-separated format expected by Waterpoint."""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    return ",".join(str(v) for v in value)


def date_str(value: str | date | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return value


def ensure_list(data: Any) -> list[Any]:
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return [data]

def parse_name(data: list[dict], name: str, district: Optional[bool] = None) -> list[dict]:
    if district:
        name_lists = np.unique([wp.get("adm2") for wp in data if wp.get("adm2")])
    else:
        name_lists = np.unique([wp.get("name") for wp in data if wp.get("name")])

    name = name.strip().lower()
    normalized = {n.strip().lower(): n for n in set(name_lists)}
    matched_name = process.extractOne(name, normalized.keys(), scorer=fuzz.WRatio,score_cutoff=50.1)
    

    if matched_name:
        if district:
            matched_details = [wp for wp in data if wp.get("adm2") == normalized[matched_name[0]]]
        else:   
            matched_details = [wp for wp in data if wp.get("name") == normalized[matched_name[0]]]
        return matched_details
    
    return []

def parse_zone_name(data: list[dict],zone_name:str) -> list[dict]:
    if zone_name:
        name_lists = np.unique([wp.get("adm1") for wp in data if wp.get("adm1")])
        name = zone_name.strip().lower()
        normalized = {n.strip().lower(): n for n in set(name_lists)}
        matched_name = process.extractOne(name, normalized.keys(), scorer=fuzz.WRatio,score_cutoff=50.1)
    
        if matched_name:
            matched_details = [wp for wp in data if wp.get("adm1") == normalized[matched_name[0]]]
            return matched_details
    else:
        return []
def parse_waterpoint_status(status:str)->Union[str, List[str]]:
    status_sys= ['GOOD','WATCH','ALERT', 'NEAR_DRY','SESONLY_DRY']
    status = status.strip().lower()
    status_sys = {n.strip().lower(): n for n in set(status_sys)}
    result = process.extractOne(status, status_sys.keys(), scorer=fuzz.WRatio,score_cutoff=50.1)
    
    if not result:
        return "could not identify the status"
    matched_status = result[0]
    if matched_status not in ['NEAR_DRY','SESONLY_DRY']:
        return matched_status
    else:
        return ['NEAR_DRY','SESONLY_DRY']      
    
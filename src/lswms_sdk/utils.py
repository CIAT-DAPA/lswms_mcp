from __future__ import annotations

from datetime import date
from typing import Iterable, Any
import numpy as np
from rapidfuzz import process, fuzz
from typing import Optional 



def csv(value: str | int | Iterable[str | int]) -> str:
    """Convert scalar/list values into the comma-separated format expected by AClimate."""
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
    matched_name = process.extractOne(name, name_lists, scorer=fuzz.WRatio)

    if matched_name:
        if district:
            matched_details = [wp for wp in data if wp.get("adm2") == matched_name[0]]
        else:   
            matched_details = [wp for wp in data if wp.get("name") == matched_name[0]]
        return matched_details
    
    return []


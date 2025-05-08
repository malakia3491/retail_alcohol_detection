from datetime import datetime, timedelta
from typing import Optional

def between(
    date, 
    start, 
    end, 
    inclusive_start=True, 
    inclusive_end=True
):
    if start > end:
        start, end = end, start
    lower_check = (date >= start) if inclusive_start else (date > start)
    upper_check = (date <= end) if inclusive_end else (date < end)
    return lower_check and upper_check

def adjust_day_edge(dt: datetime, end_of_day: bool = False) -> Optional[datetime]:
    """
    Приводит datetime к началу или концу дня с сохранением временной зоны
    
    :param dt: Исходный datetime (может быть наивным или с временной зоной)
    :param end_of_day: Флаг для указания конца дня (23:59:59.999999)
    :return: datetime с изменённым временем или None если входные данные невалидны
    """
    if not isinstance(dt, datetime):
        return None

    try:
        if end_of_day:
            adjusted = dt.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )
        else:
            adjusted = dt.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            
        if dt.tzinfo is not None:
            adjusted = adjusted.astimezone(dt.tzinfo)

        return adjusted

    except (ValueError, TypeError) as e:
        print(f"Error adjusting datetime: {e}")
        return None
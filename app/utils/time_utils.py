from datetime import datetime,timedelta
from typing import List,Tuple

def parse_window(window:str)->timedelta:
    window_map={
        "1m":timedelta(minutes=1),
        "5m":timedelta(minutes=5),
        "1h":timedelta(hours=1)
    }
    if window not in window_map:
        raise ValueError(f"Unsupported window: {window}")
    
    return window_map[window]

def round_to_window(dt:datetime,window:str)->datetime:
    window_delta=parse_window(window)
    timestamp=dt.timestamp()
    window_seconds=window_delta.total_seconds()
    rounded_timestamp=(timestamp//window_seconds)*window_seconds

    return datetime.fromtimestamp(rounded_timestamp,tz=dt.tzinfo)

def generate_time_buckets(start_time:datetime,end_time:datetime,window:str)->List[Tuple[datetime,datetime]]:
    window_delta=parse_window(window)
    buckets=[]
    current=round_to_window(start_time,window)
    while current<end_time:
        bucket_end=current+window_delta
        buckets.append((current,bucket_end))
        current=bucket_end
    return buckets
from datetime import datetime, timedelta
from terracotta_toolbelt import urljoin
import urllib.parse
import binascii
import os
import re

def get_date_range(available):
    """
    Given a list of days that have data, returns a list of days
    that do not have data between the oldest and latest
    date in the list
    """
    min = available[0]
    max = available[0]
    unavailable = []

    for day in available:
        if day < min:
            min = day
        if day > max:
            max = day

    current = min

    while current < max:
        available_dates = [dt.date() for dt in available]

        if current.date() not in available_dates:
            unavailable.append(current)
        
        current += timedelta(days=1)

    return min, max, unavailable

def extract_granule_metadata(filename):
    """
    Parses the date, instrument, and all related data
    from a data sample filename
    e.x.: PACEPAX-AH2MAP-L1C_ER2_20240910T175007_RA.nc
    """
    #             yyyy     mm     dd    hh      mm     ss
    pattern = r"_(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})"
    result = re.search(pattern, filename)

    if not result:
        return None
    
    year, month, day, hour, minute, second = result.groups()
    date = f"{year}-{month}-{day}_{hour}:{minute}:{second}"

    instrument_data = filename.split("_")[0]
    parameters = instrument_data.split("-")

    campaign = parameters[0]
    instrument = parameters[1]
    level = parameters[2]

    if instrument_data == None:
        return None

    return {
        "campaign": campaign,
        "instrument": instrument,
        "date": date,
        "level": level,
        "channel": "" # needs to be separated first into indvidual channels
    }

def get_average_of_coordinates(points):
    """
    Given a list of points in the format:
        [[x1, y1], [x2, y2], [[x3, y3], ...]]
    Returns a point that represents the average
    of all the listed points
    """
    
    x_sum = 0
    y_sum = 0

    for point in points:
        x_sum += point[0]
        y_sum += point[1]

    total_points = len(points)
    
    return [x_sum / total_points, y_sum / total_points]

def rgb_url(api_url, *keys, red_key, green_key, blue_key, stretch_range):
    """
    Returns a terracotta rgb server end point url
    given the base keys, and RGB channel keys
    """
    url = urljoin(api_url, "rgb", *keys, "{z}/{x}/{y}.png")

    lookup = {
        "r": red_key,
        "g": green_key,
        "b": blue_key ,
        "stretch_range": f"[{stretch_range[0]},{stretch_range[1]}]"
    }
    
    return f"{url}?{urllib.parse.urlencode(lookup)}"

def generate_uuid():
    """
        Generate a new random uuid
    """
    random_bytes = os.urandom(16)
    hex_string = binascii.hexlify(random_bytes).decode('utf-8')
    
    return '-'.join([
        hex_string[:8],
        hex_string[8:12],
        '4' + hex_string[13:16],
        hex(int(hex_string[16:20], 16) & 0x3fff | 0x8000)[2:],
        hex_string[20:]
    ])
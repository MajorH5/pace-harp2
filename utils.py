from datetime import datetime, timedelta
import re

def get_date_range(available):
    """
        Given a list of days that have data, returns a list of days
        that do not have data between the oldest and latest
        date in the list
    """
    min = available[0]
    max = available[0]
    unavailble = []

    for day in available:
        if day < min:
            min = day
        if day > max:
            max = day

    current = min

    while current < max:
        if current not in available:
            unavailble.append(current)
        
        current += timedelta(days=1)

    return min, max, unavailble

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
    date = datetime.strptime(f"{year}-{month}-{day}-{hour}-{minute}-{second}", "%Y-%m-%d-%H-%M-%S")

    instrument_data = filename.split("_")[0]

    if instrument_data == None:
        return None

    return {
        "instrument": instrument_data,
        "date": date
    }
import openmeteo_requests
from geopy.geocoders import Nominatim
import pandas as pd
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

geolocator = Nominatim(user_agent="haladoprog_idojaras_projekt")

#felhasználó input
def idojaras_lekeres(varos_nev: str, kezdo_datum: str, veg_datum: str):
    hely = geolocator.geocode(varos_nev)
    if not hely:
        return None

    parameterek = {
        "latitude": hely.latitude,
        "longitude": hely.longitude,
        "start_date": kezdo_datum,
        "end_date": veg_datum,
        "daily": ["temperature_2m_mean", "wind_speed_10m_max", "precipitation_sum"],
        "timezone": "Europe/Budapest"
    }

    response = openmeteo.weather_api("https://archive-api.open-meteo.com/v1/archive", params=parameterek)[0]
    daily = response.Daily()

    return pd.DataFrame({
        "Dátum": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "Hőmérséklet (°C)": daily.Variables(0).ValuesAsNumpy(),
        "Max. szélsebesség (km/h)": daily.Variables(1).ValuesAsNumpy(),
        "Csapadék (mm)": daily.Variables(2).ValuesAsNumpy()
    })

"""
if name == "main":
    teszt = idojaras_lekeres("Budapest", "2024-01-01", "2024-01-05")
    print(teszt)
"""

"""
A kiirás minta

Index   Dátum                       Hőmérséklet (°C)
0       2005-01-01 00:00:00+00:00   -3
1       2005-01-02 00:00:00+00:00   -4
2       2005-01-03 00:00:00+00:00   -5
"""
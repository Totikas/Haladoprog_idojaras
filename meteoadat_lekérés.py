import openmeteo_requests
from geopy.geocoders import Nominatim
import pandas as pd
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

open_meteo_api = "https://api.open-meteo.com/v1/forecast"

geolocator = Nominatim(user_agent="haladoprog_idojaras_projekt")

# felhasználó input
v_nev = input("Adja meg a keresett város nevét: ").lower()
helyseg_koordinata = geolocator.geocode(v_nev)

paraméterek = {
    "latitude": helyseg_koordinata.latitude,
    "longitude": helyseg_koordinata.longitude,
    "hourly": ["temperature_2m", "precipitation"],
    "timezone": "Europe/Budapest"
}

# Lekérés indítása
print("Adatok lekérése...")
responses = openmeteo.weather_api(open_meteo_api, params = paraméterek)
response = responses[0]

# Adatok kinyerése
hourly = response.Hourly()
homerseklet = hourly.Variables(0).ValuesAsNumpy()
csapadek = hourly.Variables(1).ValuesAsNumpy()

# Időbélyegek generálása
ido_adatok = pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left"
)

# Táblázat (DataFrame) összeállítása
df = pd.DataFrame({
    "Dátum": ido_adatok,
    "Hőmérséklet (°C)": homerseklet,
    "Csapadék (mm)": csapadek
})



print(f"\nSIKERES LEKÉRÉS! Íme az első 5 óra adatai {v_nev}:")
print("-" * 60)
print(df.head())
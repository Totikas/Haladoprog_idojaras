import openmeteo_requests
from geopy.geocoders import Nominatim
import pandas as pd
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Ez majd akkor ha össze vetjük a mi elörejelzésünkkel
# open_meteo_api = "https://api.open-meteo.com/v1/forecast"
open_meteo_api = "https://archive-api.open-meteo.com/v1/archive"
geolocator = Nominatim(user_agent="haladoprog_idojaras_projekt")

# felhasználó input
v_nev = input("Adja meg a keresett város nevét: ").lower()
helyseg_koordinata = geolocator.geocode(v_nev)

paraméterek = {
    "latitude": helyseg_koordinata.latitude,
    "longitude": helyseg_koordinata.longitude,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "daily": ["temperature_2m_mean"],
    "timezone": "Europe/Budapest"
}

# Lekérés indítása
print("Adatok lekérése...")
responses = openmeteo.weather_api(open_meteo_api, params = paraméterek)
response = responses[0]

# Adatok kinyerése
daily = response.Daily()
homerseklet = daily.Variables(0).ValuesAsNumpy()


# Időbélyegek generálása
ido_adatok = pd.date_range(
    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=daily.Interval()),
    inclusive="left"
)

# Táblázat (DataFrame) összeállítása
df = pd.DataFrame({
    "Dátum": ido_adatok,
    "Hőmérséklet (°C)": homerseklet,
})



print(f"\nSIKERES LEKÉRÉS! Íme az első 5 óra adatai {v_nev}:")
print("-" * 60)
print(df.head(30))
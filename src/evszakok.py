import pandas as pd

from adat_lekeres import idojaras_lekeres


def evszakos_atlagok(napi_adatok: pd.DataFrame) -> pd.DataFrame:
    adatok = napi_adatok.copy()

    # A budapesti éjfél UTC-ben az előző estére eshet.
    # A legközelebbi éjfélre kerekítve megkapjuk a napi adat dátumát.
    adatok["Dátum"] = adatok["Dátum"].dt.round("D")

    # Az évszakok decemberben, márciusban, júniusban és szeptemberben kezdődnek.
    evszakok = (
        adatok.resample("QS-DEC", on="Dátum")["Hőmérséklet (°C)"]
        .agg(atlag="mean", napok="count")
    )

    # Csak azok az évszakok kerülnek a táblázatba, amelyekhez megvan minden nap.
    kezdet = evszakok.index
    kovetkezo_evszak = kezdet + pd.DateOffset(months=3)
    vart_napok = (kovetkezo_evszak - kezdet).days
    teljes_evszakok = evszakok.loc[evszakok["napok"] == vart_napok]

    evszaknevek = {12: "Tél", 3: "Tavasz", 6: "Nyár", 9: "Ősz"}
    kezdet = teljes_evszakok.index

    # A decemberben kezdődő telet a január és február évéhez soroljuk.
    return pd.DataFrame({
        "Év": kezdet.year + (kezdet.month == 12),
        "Évszak": [evszaknevek[honap] for honap in kezdet.month],
        "Átlaghőmérséklet (°C)": teljes_evszakok["atlag"].round(2).to_numpy(),
    })

if __name__ == "__main__":
    napi_adatok = idojaras_lekeres("Budapest", "2022-12-01", "2024-11-30")

    if napi_adatok is None:
        print("A város nem található.")
    else:
        print(evszakos_atlagok(napi_adatok).to_string(index=False))
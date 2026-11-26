import pandas as pd


def evszakos_osszesites(napi_adatok: pd.DataFrame) -> pd.DataFrame:
    adatok = napi_adatok.copy()
    adatok["Dátum"] = adatok["Dátum"].dt.round("D")
    evszakok = adatok.resample("QS-DEC", on="Dátum")

    tabla = pd.DataFrame({
        "Átlaghőmérséklet (°C)": evszakok["Hőmérséklet (°C)"].mean(),
        "Összes csapadék (mm)": evszakok["Csapadék (mm)"].sum(min_count=1),
        "Maximális szélsebesség (km/h)": evszakok["Max. szélsebesség (km/h)"].max(),
    })

    # Az időszak szélén csak a teljes évszakokat vesszük figyelembe.
    kezdet = tabla.index
    vart_napok = (kezdet + pd.DateOffset(months=3) - kezdet).days
    tabla = tabla.loc[evszakok.size() == vart_napok].copy()

    kezdet = tabla.index
    evszaknevek = {12: "Tél", 3: "Tavasz", 6: "Nyár", 9: "Ősz"}

    # A decemberben kezdődő tél a január és február évéhez tartozik.
    tabla.insert(0, "Év", kezdet.year + (kezdet.month == 12))
    tabla.insert(1, "Évszak", kezdet.month.map(evszaknevek))

    return tabla.round(2).reset_index(drop=True)


def evszakos_osszehasonlitas(evszakos_tabla: pd.DataFrame) -> pd.DataFrame:
    if evszakos_tabla["Év"].nunique() < 2:
        return pd.DataFrame()

    elso_ev = int(evszakos_tabla["Év"].min())
    utolso_ev = int(evszakos_tabla["Év"].max())
    kozepso_ev = (elso_ev + utolso_ev) // 2

    korabbi_nev = f"{elso_ev}–{kozepso_ev}"
    kesobbi_nev = f"{kozepso_ev + 1}–{utolso_ev}"

    mutatok = {
        "Átlaghőmérséklet (°C)": "Átlaghőmérséklet (°C)",
        "Összes csapadék (mm)": "Átlagos szezonális csapadék (mm)",
        "Maximális szélsebesség (km/h)": "Szezonális szélmaximumok átlaga (km/h)",
    }

    sorrend = ["Tél", "Tavasz", "Nyár", "Ősz"]
    korabbi_evek = evszakos_tabla["Év"] <= kozepso_ev

    korabbi = (
        evszakos_tabla.loc[korabbi_evek]
        .groupby("Évszak")[list(mutatok)]
        .mean()
        .reindex(sorrend)
    )
    kesobbi = (
        evszakos_tabla.loc[~korabbi_evek]
        .groupby("Évszak")[list(mutatok)]
        .mean()
        .reindex(sorrend)
    )

    sorok = []
    for evszak in sorrend:
        for oszlop, mutato in mutatok.items():
            elotte = korabbi.loc[evszak, oszlop]
            utana = kesobbi.loc[evszak, oszlop]

            sorok.append({
                "Évszak": evszak,
                "Mutató": mutato,
                korabbi_nev: elotte,
                kesobbi_nev: utana,
                "Változás": utana - elotte,
            })

    return pd.DataFrame(sorok).round(2)
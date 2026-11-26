import numpy as np

from adat_feldolgozas_hofok import eves_atlagok
from adat_lekeres import idojaras_lekeres
from evszakok import evszakos_osszehasonlitas, evszakos_osszesites
from ltsm_elorejelzes import modell


if __name__ == "__main__":
    varos = input("Adj meg egy városnevet: ").strip()
    kezdo_ev = 1940
    zaro_ev = 2025

    napi_adatok = idojaras_lekeres(
        varos_nev=varos,
        kezdo_datum=f"{kezdo_ev}-01-01",
        veg_datum=f"{zaro_ev}-12-31",
    )

    if napi_adatok is None:
        print("A város nem található.")
        raise SystemExit(1)

    evszakos_tabla = evszakos_osszesites(napi_adatok)
    # Az éves számításban is a záróév előtti év az utolsó.
    evszakos_tabla = evszakos_tabla.loc[evszakos_tabla["Év"] < zaro_ev]
    osszehasonlitas = evszakos_osszehasonlitas(evszakos_tabla)

    print(f"\nÉvszakos változások – {varos}")

    if osszehasonlitas.empty:
        print("Az összehasonlításhoz legalább két év adata szükséges.")
    else:
        print(osszehasonlitas.to_string(
            index=False,
            na_rep="–",
            float_format=lambda ertek: f"{ertek:.2f}",
            formatters={"Változás": lambda ertek: f"{ertek:+.2f}"},
        ))

    adatok = eves_atlagok(
        varos=varos,
        indu_ev=kezdo_ev,
        veg_ev=zaro_ev,
    ).sort_values("Év")
    print(f"\nÉves időjárási adatok – {varos}")
    print(adatok.to_string(index=False, na_rep="–"))
    atlagok = adatok["Átlaghőmérséklet (°C)"].to_numpy()

    x = np.array([atlagok[i - 5:i] for i in range(5, len(atlagok))])
    x = x.reshape(-1, 5, 1)
    y = atlagok[5:]

    modell.fit(x, y, epochs=30, verbose=0)
    kozep = atlagok.mean()
    atlagok = atlagok - kozep

    utolso_ot_ev = atlagok[-5:].reshape(1, 5, 1)
    tipp = modell.predict(utolso_ot_ev, verbose=0).item() + kozep
    ev = adatok["Év"].iloc[-1] + 1

    print(f"\n{ev} becsült éves átlaga: {tipp:.2f} °C")
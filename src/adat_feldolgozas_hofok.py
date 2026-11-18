from adat_lekeres import idojaras_lekeres
import pandas as pd

def eves_atlagok(varos: str, indu_ev: int = 1940, veg_ev: int = 2025):
    lekeres = idojaras_lekeres(varos_nev=varos, kezdo_datum=f"{indu_ev}-01-01", veg_datum=f"{veg_ev}-12-31")

    eredmenyek = []
    for ev in range(indu_ev, veg_ev):
        ev_adatai = lekeres[lekeres["Dátum"].dt.year == ev]
        atlag_hofok = ev_adatai["Hőmérséklet (°C)"].mean()
        eredmenyek.append({
            "Év": ev,
            "Átlaghőmérséklet (°C)": round(atlag_hofok, 2)
        })

    return pd.DataFrame(eredmenyek)


"""
if __name__ == "__main__":
    print(eves_atlagok("Budapest").to_string(index=False))
"""
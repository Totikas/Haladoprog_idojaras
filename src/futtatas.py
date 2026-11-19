from adat_feldolgozas_hofok import eves_atlagok
from ltsm_elorejelzes import modell
import numpy as np

if __name__ == "__main__":
    varos = input("Adj meg egy városnevet: ")

    print(eves_atlagok(varos=varos).to_string(index=False))

    adatok = eves_atlagok(varos=varos).sort_values("Év")
    atlagok = adatok["Átlaghőmérséklet (°C)"].to_numpy()

    x = np.array([atlagok[i - 5:i] for i in range(5, len(atlagok))])
    x = x.reshape(-1, 5, 1)
    y = atlagok[5:]

    modell.fit(x, y, epochs=30)
    kozep = atlagok.mean()
    atlagok = atlagok - kozep

    utolso_ot_ev = atlagok[-5:].reshape(1, 5, 1)
    tipp = modell.predict(utolso_ot_ev, verbose=0).item() + kozep
    ev = adatok["Év"].iloc[-1] + 1
    print(f"{ev} becsült éves átlaga: {tipp:.2f} °C")

    


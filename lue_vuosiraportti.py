from __future__ import annotations

import csv
from datetime import datetime, date
from typing import List, Dict, Tuple

def lue_data(tiedoston_nimi: str) -> List[Dict[str, object]]:
    """
    Lukee viikkodatan CSV-tiedostosta ja palauttaa listan mittauksia.
    Jokainen mittaus sisältää päivän, kulutuksen ja tuotannon
    vaiheittain.
    """
    mittaukset: List[Dict[str, object]] = []

    with open(tiedoston_nimi, encoding="utf-8") as tiedosto:
        lukija = csv.DictReader(tiedosto, delimiter=";")

        for rivi in lukija:
            aika_str = rivi["Aika"]
            aika = datetime.fromisoformat(aika_str)
            paiva = aika.date()
            kulutus_v1 = float(rivi["Kulutus vaihe 1 Wh"])
            kulutus_v2 = float(rivi["Kulutus vaihe 2 Wh"])
            kulutus_v3 = float(rivi["Kulutus vaihe 3 Wh"])
            tuotanto_v1 = float(rivi["Tuotanto vaihe 1 Wh"])
            tuotanto_v2 = float(rivi["Tuotanto vaihe 2 Wh"])
            tuotanto_v3 = float(rivi["Tuotanto vaihe 3 Wh"])

            mittaukset.append(
                {
                    "paiva": paiva,
                    "kulutus": (kulutus_v1, kulutus_v2, kulutus_v3),   
                    "tuotanto": (tuotanto_v1, tuotanto_v2, tuotanto_v3)  
                }
            )

    return mittaukset

def laske_paivasummat(
    mittaukset: List[Dict[str, object]]
) -> Dict[date, Dict[str, Tuple[float, float, float]]]:
    """
    Laskee päiväkohtaiset kulutus ja tuotantosummat.
    Palauttaa sanakirjan, jossa avaimina ovat päivämäärät ja arvoina
    sanakirjat, kulutus ja tuotantoarvot on kWh-yksikössä.
    """
    paiva_summat_wh: Dict[date, Dict[str, List[float]]] = {}

    for mittaus in mittaukset:
        paiva = mittaus["paiva"]
        kulutus_wh = mittaus["kulutus"]
        tuotanto_wh = mittaus["tuotanto"]

        if paiva not in paiva_summat_wh:
            paiva_summat_wh[paiva] = {
                "kulutus_wh": [0.0, 0.0, 0.0],
                "tuotanto_wh": [0.0, 0.0, 0.0],
            }

        for i in range(3):
            paiva_summat_wh[paiva]["kulutus_wh"][i] += kulutus_wh[i]
            paiva_summat_wh[paiva]["tuotanto_wh"][i] += tuotanto_wh[i]

    paiva_summat_kwh: Dict[date, Dict[str, Tuple[float, float, float]]] = {}
    for paiva, arvot in paiva_summat_wh.items():
        kulutus_kwh = tuple(x / 1000.0 for x in arvot["kulutus_wh"])
        tuotanto_kwh = tuple(x / 1000.0 for x in arvot["tuotanto_wh"])
        paiva_summat_kwh[paiva] = {
            "kulutus": kulutus_kwh,
            "tuotanto": tuotanto_kwh,
        }

    return paiva_summat_kwh

def muotoile_pvm(paiva: date) -> str:
    """
    Palauttaa päivämäärän merkkijonona muodossa pv.kk.vvvv.
    """
    return f"{paiva.day}.{paiva.month}.{paiva.year}"

def muotoile_kwh(arvo: float) -> str:
    """
    Palauttaa kWh-arvon merkkijonona kahden desimaalin tarkkuudella.
    """
    arvo_str = f"{arvo:.2f}"
    return arvo_str.replace(".", ",")

def viikonpaivan_nimi(paiva: date) -> str:
    """
    Palauttaa viikonpäivän nimen suomeksi.
    """
    nimet = [
        "maanantai",
        "tiistai",
        "keskiviikko",
        "torstai",
        "perjantai",
        "lauantai",
        "sunnuntai",
    ]
    return nimet[paiva.weekday()]

def tulosta_raportti(
    paiva_summat: Dict[date, Dict[str, Tuple[float, float, float]]]
) -> None:
    """
    Tulostaa viikon sähkönkkulutus ja tuotantotiedot taulukkona.
    """
    print("Viikon 42 sähkönkulutus ja tuotanto\n")
    print(
        f"{'Päivä':<12} {'Pvm':<12} "
        f"{'Kulutus [kWh]':>26} {'Tuotanto [kWh]':>26}"
    )
    print(
        f"{'':<12} {'(pv.kk.vvvv)':<12}"
        f"{'v1':>8}{'v2':>8}{'v3':>8} {'v1':>8}{'v2':>8}{'v3':>8}"
    )
    print("-" * 80)

    for paiva in sorted(paiva_summat.keys()):
        paiva_nimi = viikonpaivan_nimi(paiva)
        pvm_str = muotoile_pvm(paiva)

        kul_v1, kul_v2, kul_v3 = paiva_summat[paiva]["kulutus"]
        tuo_v1, tuo_v2, tuo_v3 = paiva_summat[paiva]["tuotanto"]

        print(
            f"{paiva_nimi:<12} {pvm_str:<12}"
            f"{muotoile_kwh(kul_v1):>8}"
            f"{muotoile_kwh(kul_v2):>8}"
            f"{muotoile_kwh(kul_v3):>8}"
            f"{muotoile_kwh(tuo_v1):>8}"
            f"{muotoile_kwh(tuo_v2):>8}"
            f"{muotoile_kwh(tuo_v3):>8}"
        )


def main() -> None:
    """
    Ohjelman pääfunktio: lukee CSV-datan laskee päiväkohtaiset kulutus ja tuotantosumat
    tulostaa raportin konsoliin.
    """
    tiedoston_nimi = "viikko42.csv"
    mittaukset = lue_data(tiedoston_nimi)
    paiva_summat = laske_paivasummat(mittaukset)
    tulosta_raportti(paiva_summat)


if __name__ == "__main__":
    main()

"""Étape 2 : nettoyage -> série horaire continue de la consommation (MW)."""
import pandas as pd

from common import PROC, ROOT, load_params


def main():
    p = load_params()["data"]
    df = pd.read_csv(ROOT / p["raw_path"], usecols=[p["timestamp_col"], p["target_col"]])
    ts = pd.to_datetime(df[p["timestamp_col"]], utc=True).dt.tz_localize(None)  # UTC sans fuseau
    s = pd.Series(df[p["target_col"]].values, index=ts, name="load_mw").sort_index()
    s = s[~s.index.duplicated(keep="first")]
    s = s.resample("h").mean()                      # pas horaire régulier
    print("Valeurs manquantes avant :", int(s.isna().sum()))
    s = s.interpolate(limit=6)                      # on ne comble que les trous <= 6 h
    s = s.loc[s.first_valid_index(): s.last_valid_index()]
    block = (s.isna() != s.isna().shift()).cumsum()  # on garde le plus long segment sans trou
    sizes = s.groupby(block).apply(lambda x: len(x) if x.notna().all() else 0)
    s = s[block == sizes.idxmax()]
    assert s.notna().all() and (s > 0).all(), "Série invalide après nettoyage"
    PROC.mkdir(parents=True, exist_ok=True)
    s.rename_axis("timestamp").to_csv(PROC / "load_hourly.csv")
    print(f"OK : {len(s)} heures, du {s.index[0]} au {s.index[-1]}")


if __name__ == "__main__":
    main()

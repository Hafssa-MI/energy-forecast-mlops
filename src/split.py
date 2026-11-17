"""Étape 3 : découpage chronologique train / val / test / stream (jamais aléatoire)."""
from common import PROC, load_params, read_series


def split_series(s, stream_days, test_days, val_days):
    n_stream, n_test, n_val = stream_days * 24, test_days * 24, val_days * 24
    assert len(s) > 2 * (n_stream + n_test + n_val), "Série trop courte pour ce découpage"
    return {
        "train": s.iloc[: -(n_stream + n_test + n_val)],
        "val": s.iloc[-(n_stream + n_test + n_val): -(n_stream + n_test)],
        "test": s.iloc[-(n_stream + n_test): -n_stream],
        "stream": s.iloc[-n_stream:],
    }


def main():
    p = load_params()["split"]
    parts = split_series(read_series(PROC / "load_hourly.csv"),
                         p["stream_days"], p["test_days"], p["val_days"])
    for name, part in parts.items():
        part.rename_axis("timestamp").to_csv(PROC / f"{name}.csv")
        print(f"{name:7s} {len(part):6d} h   {part.index[0]} -> {part.index[-1]}")


if __name__ == "__main__":
    main()

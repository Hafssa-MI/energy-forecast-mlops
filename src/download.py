"""Étape 1 : télécharge le fichier brut (Open Power System Data) sans le modifier."""
import requests

from common import ROOT, load_params


def main():
    p = load_params()["data"]
    out = ROOT / p["raw_path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    print("Téléchargement :", p["url"])
    with requests.get(p["url"], stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print(f"OK : {out} ({out.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()

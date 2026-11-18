"""Vérifie la connexion MLflow (DagsHub) en journalisant un petit run de test."""
import os
import sys
import tempfile
from pathlib import Path

import mlflow

uri = os.getenv("MLFLOW_TRACKING_URI")
if not uri:
    sys.exit("MLFLOW_TRACKING_URI n'est pas défini (voir README, section MLflow).")

mlflow.set_tracking_uri(uri)
mlflow.set_experiment("connexion-test")
with mlflow.start_run(run_name="ping"):
    mlflow.log_param("source", "check_mlflow.py")
    mlflow.log_metric("ok", 1.0)
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "ping.txt"
        f.write_text("ok")
        mlflow.log_artifact(str(f))
print("OK : run enregistré sur", uri)
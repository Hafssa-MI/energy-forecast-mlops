
import os
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
mlflow.set_experiment("connexion-test")

c = MlflowClient()

with mlflow.start_run() as run:
    mlflow.log_text("ok", "m/x.txt")

mv = mlflow.register_model(
    f"runs:/{run.info.run_id}/m",
    "alias-test"
)

c.set_registered_model_alias("alias-test", "demo", mv.version)

got = c.get_model_version_by_alias("alias-test", "demo")
print("ALIAS OK : version", got.version)

path = mlflow.artifacts.download_artifacts(
    artifact_uri="models:/alias-test@demo"
)
print("TELECHARGEMENT PAR ALIAS OK :", path)

c.delete_registered_model("alias-test")

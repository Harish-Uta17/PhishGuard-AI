### Network Security Projects For Phishing Data

### MLflow Tracking

This project logs experiments to DagsHub by default through `dagshub.init(...)`.

If you want to use a local MLflow backend instead, set `MLFLOW_TRACKING_URI` before running the pipeline, for example:

```powershell
$env:MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```
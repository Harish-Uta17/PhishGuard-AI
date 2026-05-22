import mlflow
from mlflow.tracking import MlflowClient
import os

def main():
    exp_name = os.getenv('MLFLOW_EXPERIMENT_NAME','NetworkSecurity')
    print('Experiment name:', exp_name)
    exp = mlflow.get_experiment_by_name(exp_name)
    if not exp:
        print('Experiment not found via mlflow API')
        return
    client = MlflowClient()
    runs = client.search_runs([exp.experiment_id], order_by=['attributes.start_time DESC'], max_results=5)
    if not runs:
        print('No runs found')
        return
    latest = runs[0]
    print('Latest run id:', latest.info.run_id)
    print('Metrics:')
    for k,v in latest.data.metrics.items():
        print(k, v)
    print('\nParams:')
    for k,v in latest.data.params.items():
        print(k, v)

if __name__ == '__main__':
    main()

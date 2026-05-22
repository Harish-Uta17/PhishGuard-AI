import os
import pickle
from networksecurity.utils.main_utils.utils import load_numpy_array_data
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score


def main():
    model_path = os.path.join('final_model','model.pkl')
    if not os.path.exists(model_path):
        print('Model not found at', model_path)
        return

    # locate latest artifact run
    base = 'Artifacts'
    if not os.path.exists(base):
        print('Artifacts directory not found')
        return
    runs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base,d))]
    if not runs:
        print('No artifact runs')
        return
    runs.sort()
    latest = runs[-1]
    test_path = os.path.join(base, latest, 'data_transformation', 'transformed', 'test.npy')
    if not os.path.exists(test_path):
        print('Test file not found at', test_path)
        return

    test_arr = load_numpy_array_data(test_path)
    X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    y_pred = model.predict(X_test)
    metrics = get_classification_score(y_true=y_test, y_pred=y_pred)

    print('Precision:', metrics.precision_score)
    print('Recall:', metrics.recall_score)
    print('F1:', metrics.f1_score)


if __name__ == '__main__':
    main()

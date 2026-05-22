import os
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier,AdaBoostClassifier
from sklearn.linear_model import LogisticRegression

def main():
    base = 'Artifacts'
    if not os.path.exists(base):
        print('Artifacts directory not found')
        return

    dirs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base,d))]
    if not dirs:
        print('No artifact runs found')
        return

    dirs.sort()
    latest = dirs[-1]
    print('Using artifact run:', latest)

    train = os.path.join(base, latest, 'data_transformation', 'transformed', 'train.npy')
    test = os.path.join(base, latest, 'data_transformation', 'transformed', 'test.npy')
    if not os.path.exists(train) or not os.path.exists(test):
        print('Train/test npy not found at expected locations')
        return

    train_arr = load_numpy_array_data(train)
    test_arr = load_numpy_array_data(test)
    X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
    X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

    models = {
        'Random Forest': RandomForestClassifier(),
        'Decision Tree': DecisionTreeClassifier(),
        'Gradient Boosting': GradientBoostingClassifier(),
        'Logistic Regression': LogisticRegression(),
        'AdaBoost': AdaBoostClassifier(),
    }

    params = {
        'Decision Tree': {'criterion':['gini','entropy','log_loss']},
        'Random Forest': {'n_estimators': [8,16,32,128,256]},
        'Gradient Boosting': {'learning_rate':[.1,.01,.05,.001],'subsample':[0.6,0.7,0.75,0.85,0.9],'n_estimators':[8,16,32,64,128,256]},
        'Logistic Regression': {},
        'AdaBoost': {'learning_rate':[.1,.01,.001],'n_estimators':[8,16,32,64,128,256]}
    }

    report = evaluate_models(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test,models=models,param=params)
    print('Model scores:')
    for k,v in report.items():
        print(k, v)

    best_score = max(sorted(report.values()))
    best_name = list(report.keys())[list(report.values()).index(best_score)]
    print('\nBest model:', best_name)

if __name__ == '__main__':
    main()

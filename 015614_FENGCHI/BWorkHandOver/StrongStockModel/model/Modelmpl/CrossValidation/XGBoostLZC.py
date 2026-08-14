import pandas as pd
import time
import gc,os

def set_model():
    config = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
    import xgboost as xgb
    xgb.config = config
    return xgb


def train_model(X_train, y_train, X_test, y_test, xgb, model_name, model_root, model_idx):
    if os.path.exists(f'{model_root}/{model_name}/conf/{model_idx}_param.pkl') and os.path.exists(f'{model_root}/{model_name}/conf/{model_idx}.json'):
        model = xgb.Booster()
        model.load_model(f'{model_root}/{model_name}/conf/{model_idx}.json')
        return model
    X_train = xgb.DMatrix(X_train, label=y_train)
    X_test = xgb.DMatrix(X_test, label=y_test)

    model = xgb.train(xgb.config, X_train, num_boost_round=xgb.config['n_estimators'],
                      early_stopping_rounds=15, evals=[(X_train, 'train'), (X_test, 'test')],
                      verbose_eval=True)
    config = xgb.config.copy()
    config.update({'best_ntree': model.best_ntree_limit})
    pd.to_pickle(config,f'{model_root}/{model_name}/conf/{model_idx}_param.pkl')
    model.save_model(f'{model_root}/{model_name}/conf/{model_idx}.json')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model


def pred_model(X, d, t, c, model, model_name, model_root, model_idx, pred_type='pred', **kwargs):
    import xgboost as xgb
    para = pd.read_pickle(f'{model_root}/{model_name}/conf/{model_idx}_param.pkl')
    yh = model.predict(xgb.DMatrix(X),ntree_limit=para['best_ntree']).flatten()
    df_pred = {'date': d, 'time': t, 'code': c, 'yh': yh}
    df_pred.update(kwargs)
    df_pred = pd.DataFrame(df_pred)
    df_pred.to_pickle(f'{model_root}/{model_name}/{pred_type}/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish {pred_type} model {model_idx}')
    return df_pred

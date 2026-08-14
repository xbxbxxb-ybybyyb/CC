import pandas as pd
import time
import os

def prepare_model_fold(model_name, model_root):

    sub_folds = ['conf', 'train', 'test', 'pred', 'analyse', 'score']
    for f in sub_folds:
        path = f'{model_root}/{model_name}/{f}/'
        if not os.path.exists(path):
            os.makedirs(path)

def set_model():

    config = dict(

        process_type='default',
        boooster='gbtree',
        objective='reg:linear',
        silent=False,
        nthread=-1,
        tree_method='gpu_hist',

        eta=0.15,
        # num_boost_round=20,
        max_depth=4,
        min_child_weight=50,
        gamma=0,
        subsample=1,
        colsample_bytree=1,
        # reg_alpha=0,
        reg_lambda=0,
        scale_pos_weight=1,
        max_delta_step=0,
        num_boost_round=1000,
        xgb_model=None
    )

    import xgboost as xgb
    xgb.config = config
    return xgb

def train_model(X_train, y_train, d_train, c_train, ry_train, xgb, model_name, model_root, model_idx):

    X_train = xgb.DMatrix(X_train, label=y_train)
    model = xgb.train(xgb.config, X_train, num_boost_round=xgb.config['num_boost_round'],
                      xgb_model=xgb.config['xgb_model'])
    model.save_model(f'{model_root}/{model_name}/conf/{model_idx}.json')
    yh_train = model.predict(X_train).flatten()
    df_train = pd.DataFrame({'date': d_train, 'code': c_train, 'ry': ry_train, 'y': y_train, 'yh': yh_train})
    df_train.to_pickle(f'{model_root}/{model_name}/train/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model

def train_test_model(X_train, y_train, d_train, c_train, ry_train,
                     X_test, y_test, xgb, model_name, model_root, model_idx):

    X_train = xgb.DMatrix(X_train, label=y_train)
    X_test = xgb.DMatrix(X_test, label=y_test)

    model = xgb.train(xgb.config, X_train, num_boost_round=xgb.config['num_boost_round'],
                      early_stopping_rounds=50, evals=[(X_train, 'train'), (X_test, 'test')],
                      verbose_eval=True)
    config = xgb.config.copy()
    config.update({'num_boost_round': model.best_ntree_limit})
    model = xgb.train(config, X_train, num_boost_round=config['num_boost_round'])

    model.save_model(f'{model_root}/{model_name}/conf/{model_idx}.json')
    yh_train = model.predict(X_train).flatten()
    df_train = pd.DataFrame({'date': d_train, 'code': c_train, 'ry': ry_train, 'y': y_train, 'yh': yh_train})
    df_train.to_pickle(f'{model_root}/{model_name}/train/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model

def pred_model(X, y, d, c, ry, model, model_name, model_root, model_idx, pred_type='pred'):

    import xgboost as xgb
    yh = model.predict(xgb.DMatrix(X)).flatten()
    df_pred = pd.DataFrame({'date': d, 'code': c, 'ry': ry, 'y': y, 'yh': yh})
    df_pred.to_pickle(f'{model_root}/{model_name}/{pred_type}/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish {pred_type} model {model_idx}')

def load_model(model_name, model_root, model_idx):

    import xgboost as xgb
    model = xgb.Booster(model_file=f'{model_root}/{model_name}/conf/{model_idx}.json')
    return model

if __name__ == '__main__':

    model_root = '/arch1/user/015836/HFmodel/MorningModel/Tree/XGB/'
    model_name = '20210402TSF400T488P10'
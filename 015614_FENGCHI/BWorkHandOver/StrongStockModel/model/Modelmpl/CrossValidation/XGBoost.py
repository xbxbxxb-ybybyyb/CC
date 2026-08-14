import pandas as pd
import time
import gc

def set_model():
    config = dict(

        process_type='default',
        boooster='gbtree',
        objective='reg:linear',
        silent=False,
        nthread=-1,
        tree_method='gpu_hist',

        eta=0.2,
        # num_boost_round=20,
        max_depth=8,
        min_child_weight=50,
        gamma=0,
        subsample=0.8,
        colsample_bytree=0.8,
        # reg_alpha=0,
        reg_lambda=0,
        scale_pos_weight=1,
        max_delta_step=0,
        num_boost_round=500,
        xgb_model=None
    )

    import xgboost as xgb
    xgb.config = config
    xgb.train()
    return xgb


def train_model(X_train, y_train, X_test, y_test, xgb, model_name, model_root, model_idx):
    X_train = xgb.DMatrix(X_train, label=y_train)
    X_test = xgb.DMatrix(X_test, label=y_test)

    model = xgb.train(xgb.config, X_train, num_boost_round=xgb.config['num_boost_round'],
                      early_stopping_rounds=50, evals=[(X_train, 'train'), (X_test, 'test')],
                      verbose_eval=True)
    config = xgb.config.copy()
    config.update({'num_boost_round': model.best_ntree_limit})
    del model
    gc.collect()
    model = xgb.train(config, X_train, num_boost_round=config['num_boost_round'])

    model.save_model(f'{model_root}/{model_name}/conf/{model_idx}.json')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model


def pred_model(X, d, t, c, model, model_name, model_root, model_idx, pred_type='pred', **kwargs):
    import xgboost as xgb
    yh = model.predict(xgb.DMatrix(X)).flatten()
    df_pred = {'date': d, 'time': t, 'code': c, 'yh': yh}
    df_pred.update(kwargs)
    df_pred = pd.DataFrame(df_pred)
    df_pred.to_pickle(f'{model_root}/{model_name}/{pred_type}/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish {pred_type} model {model_idx}')
    return df_pred

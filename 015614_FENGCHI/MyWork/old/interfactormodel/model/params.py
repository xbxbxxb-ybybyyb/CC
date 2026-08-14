import numpy as np
from hyperopt import hp
from hyperopt.pyll import scope


@scope.define
def add_func(a, b):

    return a + b

@scope.define
def mul_func(a, b):

    return a * b

params = {}

params['XGBTR'] = {
    'objective': 'reg:linear',
    'eval_metric': 'rmse',
    'learning_rate': hp.quniform('learning_rate', 0.01, 0.1, 0.01),
    'n_estimators': scope.mul_func(scope.add_func(hp.randint('n_estimators', 60), 10), 10),
    'max_depth': scope.add_func(hp.randint('max_depth', 10), 1),
    'min_child_weight': scope.add_func(hp.randint('min_child_weight', 10), 1),
    'gamma': hp.quniform('gamma', 0, 1, 0.1),
    'subsample': hp.quniform('subsample', 0.5, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 1, 0.1),
    'reg_lambda': hp.qloguniform('reg_lambda', np.log(0.01), np.log(100), 0.01),
    'reg_alpha': hp.qloguniform('reg_alpha', np.log(0.01), np.log(100), 0.01),
    'scale_pos_weight': 1,
    'max_delta_step': 0,
}

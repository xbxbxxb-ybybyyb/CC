import pandas as pd
import numpy as np
import xgboost as xgb
from tqdm import tqdm
from sklearn.linear_model import LinearRegression
from model.alphaBaseModel import AlphaBaseModel
from model.metrics import top_ret, rmse

class XGBDT(AlphaBaseModel):

    def __init__(self, start_date, end_date, future_days_max, future_day_index,
                 model_days, predict_days, cv_first_folds, cv_policy, cv_folds_limit, cv_supports,
                 middle_address, stock_pool_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 factor_rank_type='double', factor_rank_address=None,
                 future_type='future_mv', future_address=None):

        super(XGBDT, self).__init__(
            start_date, end_date, future_days_max, future_day_index, middle_address, stock_pool_address,
            factor_type, factor_address, factor_rank_type, factor_rank_address, future_type, future_address)

        self.get_model_date_list(model_days, predict_days)
        self.get_cv_date_list(cv_first_folds, cv_supports, cv_policy, cv_folds_limit)

    def load_data(self, date):

        self.split_day_data(date)
        self.clean_day_data()

        self.predict_X = self.predict_X[0]
        self.predict_y = self.predict_y[0]
        self.predict_y[~np.isfinite(self.predict_y)] = np.nanmean(self.predict_y)

        self.xgb_train = xgb.DMatrix(self.train_X, label=self.train_y)
        self.xgb_test =  xgb.DMatrix(self.predict_X, label=self.predict_y)

    def lr_model(self):

        model = LinearRegression()
        model.fit(self.train_X, self.train_y)

        train_fit = model.predict(self.train_X)
        train_metric1 = config['metric1'](train_fit, self.train_y)
        train_metric2 = config['metric2'](train_fit, self.train_y)

        predict_fit = model.predict(self.predict_X)
        predict_metric1 = config['metric1'](predict_fit, self.predict_y)
        predict_metric2 = config['metric2'](predict_fit, self.predict_y)

        self.lr_metrics = [train_metric1, train_metric2, predict_metric1, predict_metric2]

    def set_params(self, config):

        xgb_params = ['process_type', 'boooster', 'objective', 'silent', 'nthread', 'eta', 'max_depth',
                      'min_child_weight', 'gamma', 'subsample', 'colsample_bytree', 'reg_alpha', 'reg_lambda',
                      'scale_pos_weight', 'max_delta_step']

        self.config = config
        self.xgb_params = {x: config[x] for x in xgb_params}
        self.model = None
        self.xgb_round = 0

    def _xgb_model(self):

        model = xgb.train(self.xgb_params, self.xgb_train, num_boost_round=500, xgb_model=self.model)
        self.xgb_round += 1
        self.model = model

        train_fit = model.predict(xgb.DMatrix(self.train_X))
        train_metric1 = self.config['metric1'](train_fit, self.train_y)
        train_metric2 = self.config['metric2'](train_fit, self.train_y)

        predict_fit = model.predict(xgb.DMatrix(self.predict_X))
        predict_metric1 = self.config['metric1'](predict_fit, self.predict_y)
        predict_metric2 = self.config['metric2'](predict_fit, self.predict_y)

        self.xgb_metrics = [train_metric1, train_metric2, predict_metric1, predict_metric2]

    def xgb_model(self):

        def _feval(_y, dtrain):
            y = dtrain.get_label()
            metric2 = self.config['metric2'](_y, y)
            return 'metric2', metric2

        evals_result = {}
        model = xgb.train(self.xgb_params, self.xgb_train, num_boost_round=500,
                          evals=[(self.xgb_train, 'train'), (self.xgb_test, 'test')],
                          xgb_model=self.model, feval=_feval, evals_result=evals_result, verbose_eval=True)
        self.evals_result = evals_result

if __name__ == '__main__':

    config = dict(

        metric1 = rmse,
        metric2 = top_ret,

        process_type='default',
        boooster='gbtree',
        objective='reg:linear',
        silent=True,
        nthread=24,

        eta=0.1,
        max_depth=4,
        min_child_weight=1,
        gamma=0,
        subsample=1,
        colsample_bytree=1,
        reg_alpha=0,
        reg_lambda=1,
        scale_pos_weight=1,
        max_delta_step=0,
    )

    start_date = 20140102
    end_date = 20181228
    future_days_max = 5
    future_day_index = 4

    model_days = 120
    predict_days = 1

    cv_first_folds = 120
    cv_policy = 'long'
    cv_folds_limit = 10
    cv_supports = 120


    factor_type = 'factor_standardize'
    factor_rank_type = 'double'
    future_type = 'future'
    middle_address2 = '/data/user/015836/model/temp20200609/'
    middle_address = '/data/user/015836/model/temp20200527/'

    self = XGBDT(start_date, end_date, future_days_max, future_day_index,
                 model_days, predict_days, cv_first_folds, cv_policy, cv_folds_limit, cv_supports,
                 middle_address=middle_address,
                 factor_address=middle_address2, factor_rank_address=middle_address2,
                 factor_type=factor_type, factor_rank_type=factor_rank_type, future_type=future_type)

    model_date_list = [x for x in self.model_date_list if x > 20151223]
    for date in tqdm(model_date_list):

        self.load_data(date)
        df = pd.DataFrame(columns=['train_rmse', 'train_ret', 'test_rmse', 'test_ret'])
        self.lr_model()
        print(self.lr_metrics)
        df.loc[0] = self.lr_metrics
        self.set_params(config)
        self.xgb_model()
        df1 = self.evals_result
        df1 = pd.DataFrame([df1['train']['rmse'], df1['train']['metric2'], df1['test']['rmse'], df1['train']['metric2']],
                           index=['train_rmse', 'train_ret', 'test_rmse', 'test_ret']).T
        df1.index = df1.index.map(lambda x : x + 1)
        df = pd.concat([df, df1])
        df.to_hdf('/data/user/015836/model/xgboost/%s.h5' % date, str(date), format='t')
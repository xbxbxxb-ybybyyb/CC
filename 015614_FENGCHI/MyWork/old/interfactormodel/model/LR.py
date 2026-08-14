import numpy as np
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from model.alphaBaseModel import AlphaBaseModel
from model.metrics import top_ret, rmse

class LR(AlphaBaseModel):

    def __init__(self, start_date, end_date, future_days_max, future_day_index,
                 model_days, predict_days, cv_first_folds, cv_policy, cv_folds_limit, cv_supports,
                 middle_address, stock_pool_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 factor_rank_type='double', factor_rank_address=None,
                 future_type='future_mv', future_address=None):

        super(LR, self).__init__(
            start_date, end_date, future_days_max, future_day_index, middle_address, stock_pool_address,
            factor_type, factor_address, factor_rank_type, factor_rank_address, future_type, future_address)

        self.get_model_date_list(model_days, predict_days)
        self.get_cv_date_list(cv_first_folds, cv_supports, cv_policy, cv_folds_limit)

    def load_data(self, date):

        self.split_day_data(date)
        self.clean_day_data()

    def train(self, config):

        model = Lasso(alpha=config['alpha'], tol=1e-8)
        model.fit(self.train_X, self.train_y)

        train_fit = model.predict(self.train_X)
        train_metric1 = config['metric1'](train_fit, self.train_y)
        train_metric2 = config['metric2'](train_fit, self.train_y)

        self.model = model
        self.train_metric = [train_metric1, train_metric2]

    def predict(self, config):

        predict_fit = tuple(self.model.predict(self.predict_X[x]) for x in range(len(self.predict_X)))
        predict_metric1 = [config['metric1'](predict_fit[x], self.predict_y[x]) for x in range(len(self.predict_X))]
        predict_metric2 = [config['metric2'](predict_fit[x], self.predict_y[x]) for x in range(len(self.predict_X))]
        self.predict_metric = [predict_metric1, predict_metric2]


if __name__ == '__main__':

    config = dict(
        alpha = 1e-6,
        metric1 = rmse,
        metric2 = top_ret,
    )


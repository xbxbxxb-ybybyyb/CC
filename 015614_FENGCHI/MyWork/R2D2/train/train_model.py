# coding: utf-8
# Author：fengchi863
# Date ：2021/6/9 14:49

from R2D2.data_processing.DataProcessing import DataProcessing
from R2D2.RLModel.env.environment import EnvSetup
from StrongStockModel.model.ModelBase import ModelNewLoading
import pandas as pd
from StrongStockModel.conf.path_config import root_path



class A2CModel(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None,
                 factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)
        agent = EnvSetup()

    def get_fix_factor_evaluation(self, num, end_index):
        factor_evaluation = pd.read_pickle(root_path + 'external_data/ic_half.pkl')  # .set_index('name')
        factor_evaluation = pd.DataFrame(factor_evaluation)
        if not self.eval_indicator in factor_evaluation.index.levels[0]:
            raise Exception('Unavailable indicator')
        factor_evaluation = factor_evaluation.loc[self.eval_indicator]
        target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index)))
        factor_evaluation = factor_evaluation.loc[target_date]
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        return sorted(factor_list)

    def train_model(self, X_train, y_train, params, end_date=None):
        pass



# print('start_training')
#
# train, test = DataProcessing.get_dataset()
# env_setup = EnvSetup()
#
# env_train = env_setup.create_env_training(data=train, env_class=None)



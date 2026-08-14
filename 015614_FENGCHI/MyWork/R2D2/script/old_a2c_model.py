# coding: utf-8
# Author：fengchi863
# Date ：2021/6/28 20:00

from R2D2.model.TrainBase import TrainBase
from stable_baselines import A2C
from stable_baselines.common.vec_env import DummyVecEnv
from R2D2.Env.FixEnv import StockEnv
from tqdm import tqdm
import datetime, time
import os

class A2CModel(TrainBase):
    def __init__(self, start, end, env, env_kwd, model_output_path):
        super.__init__(start, end, env, env_kwd)
        self.model_output_path = model_output_path

    def train_model(self, params, env, log_path='/data/user/015614/R2D2/test.log'):
        model = A2C(
            policy=params['policy'],
            env=env,
            tensorboard_log=log_path,
            verbose=True,
            # policy_kwargs=policy_kwargs,
            # **model_kwargs,
        )
        model.learn(total_timesteps=10000)
        return model

    def rolling_and_train_model(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])
            env_train = DummyVecEnv([lambda: StockEnv(start=train_start_idx, end=train_end_idx)])
            model = self.train_model(params, env_train)
            model.save('')
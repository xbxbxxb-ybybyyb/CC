# coding: utf-8
# Author：fengchi863
# Date ：2021/7/16 14:45

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/R2D2')

from R2D2.model.TrainBase import TrainBase
from R2D2.Env.FixEnv import StockEnv
from R2D2.conf.path_conf import root_path
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.save_util import load_from_pkl, save_to_pkl
import os, gc
import pandas as pd
import dill

class PPOModel(TrainBase):
    def __init__(self, start, end, base_dir, env_kwd, model_kwd, start_cash=2e8, env=StockEnv):
        super().__init__(start, end, base_dir, env_kwd, model_kwd, start_cash=start_cash, env=env)

    def train_model(self, start, end, n_cpu, model_kwargs=None):
        if os.path.exists(f'{self.base_dir}/model/test_model_{start}_{end}.zip'):
            model = PPO.load(f'{self.base_dir}/model/test_model_{start}_{end}')
            if os.path.exists(f'{self.base_dir}/stk_list/{start}_{end}.pkl'):
                stk_list = pd.read_pickle(f'{self.base_dir}/stk_list/{start}_{end}.pkl')
            else:
                env = self.env(start, end, initial_cash=self.account_val, **self.env_kwd)
                pd.to_pickle(env.stk_list, f'{self.base_dir}/stk_list/{start}_{end}.pkl')
                stk_list = env.stk_list
            print(f'{start}-{end} model exist')
            return model, stk_list
        env = self.env(start, end, initial_cash=self.account_val, **self.env_kwd)
        env_test = DummyVecEnv([lambda: env])
        if model_kwargs is None:
            model_kwargs = self.model_kwd.copy()
        model = PPO(
            'MlpPolicy',
            env=env_test,
            **model_kwargs
        )
        model.learn(total_timesteps=20000) # 10000
        model.save(f'{self.base_dir}/model/test_model_{start}_{end}')
        pd.to_pickle(env.stk_list, f'{self.base_dir}/stk_list/{start}_{end}.pkl')
        print('以保存至%s' % f'{self.base_dir}/stk_list/{start}_{end}.pkl')
        stk_list = env.stk_list
        del env
        gc.collect()
        return model, stk_list

    def pred(self, model, stk_list, start, end, extra_pool=None):
        env = self.env(start, end, stock_pool=extra_pool, stk_list=stk_list, **self.env_kwd)
        obs = env.reset()
        terminal = False
        while not terminal:
            action = model.predict(obs.reindex(stk_list).fillna(0))
            state, reward, terminal, _ = env.step(action[0])
        res = [env.accout_value, env.account_index, env.cash_series, env.daily_holding]
        self.account_val = env.accout_value[-1]
        pd.to_pickle(res, f'{self.base_dir}pred_res/pred_{start}.pkl')


if __name__ == '__main__':
    train_period = 40
    test_period = 20
    root_path = root_path + 'fengchi/'  # 区分路径
    path = f'{root_path}/TainingRes/PPOTest_train{train_period}_test{test_period}_20210719/'

    PPO_PARAMS = {'n_steps':128,
			  'ent_coef':0.01,
			  'learning_rate':0.00025,
              'batch_size':2 ** 12,
			  'verbose':0,
              'tensorboard_log': path + 'log/'}

    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path + 'stk_list/')
        os.makedirs(path + 'pred_res/')
        os.makedirs(path + 'log/')
    train_conn = PPOModel(20170101, 20201231, base_dir=path, model_kwd=PPO_PARAMS,
                           env_kwd={'reward_type': 'total_return'})
    period_info = train_conn.split_date_period(train_period, test_period)
    train_conn.run_backtest(period_info, n_cpu=10)
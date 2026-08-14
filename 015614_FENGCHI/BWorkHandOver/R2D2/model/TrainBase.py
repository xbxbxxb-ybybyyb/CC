# @Time : 2021/6/24 14:55
# @Author : Zhichen Lu
# @File : TrainBase.py

from dataApi.tradeDate import get_date_range
from R2D2.Env.FixEnv import StockEnv
from R2D2.conf.path_conf import root_path

from stable_baselines3 import A2C
from abc import abstractmethod
import os, gc
from tqdm import tqdm
import pandas as pd
from dataApi.sendInfo import send_message


def recusrsive_mkdir(dir):
    if os.path.exists(dir):
        return
    sub = os.path.split(dir)[0]
    recusrsive_mkdir(sub)
    if not os.path.exists(dir):
        os.mkdir(dir)
    else:
        return


class TrainBase:

    def __init__(self, start, end, base_dir, env_kwd, model_kwd, start_cash=2e8, env=StockEnv):
        self.date_list = get_date_range(start, end)
        self.env = env
        self.env_kwd = env_kwd
        self.model_kwd = model_kwd
        self.base_dir = base_dir
        self.account_val = start_cash

        for each in ['', 'model', 'pred_res']:
            if not os.path.exists(f'{base_dir}{each}'):
                os.mkdir(f'{base_dir}/{each}')

    def split_date_period(self, train_period, test_period):

        date_list = self.date_list
        train_start = date_list[0:-test_period - train_period:test_period]
        train_end = [date_list[date_list.index(x) + train_period - 1] for x in train_start]
        predict_start = [date_list[date_list.index(x) + train_period] for x in train_start]
        predict_end = [date_list[date_list.index(x) + test_period - 1] for x in predict_start]

        period_info = list(zip(train_start, train_end, predict_start, predict_end))
        if period_info[-1][-1] != date_list[-1]:
            last_period = tuple([date_list[date_list.index(x) + test_period] for x in period_info[-1][:-1]]) + (date_list[-1],)
            period_info.append(last_period)
        return period_info

    @abstractmethod
    def train_model(self, start, end, n_cpu, model_kwargs=None):
        if os.path.exists(f'{self.base_dir}/model/test_model_{start}_{end}.zip'):
            model = A2C.load(f'{self.base_dir}/model/test_model_{start}_{end}')
            if os.path.exists(f'{self.base_dir}/stk_list/{start}_{end}.pkl'):
                stk_list = pd.read_pickle(f'{self.base_dir}/stk_list/{start}_{end}.pkl')
            else:
                env = self.env(start, end, initial_cash=self.account_val, **self.env_kwd)
                pd.to_pickle(env.stk_list, f'{self.base_dir}/stk_list/{start}_{end}.pkl')
                stk_list = env.stk_list
            print(f'{start}-{end} model exist')
            return model, stk_list
        env = self.env(start, end, initial_cash=self.account_val, **self.env_kwd)
        env_test, _ = env.get_multiproc_env(n_cpu)
        if model_kwargs is None:
            model_kwargs = self.model_kwd.copy()
        model = A2C(
            env=env_test,
            **model_kwargs
        )
        model.learn(total_timesteps=200000)
        model.save(f'{self.base_dir}/model/test_model_{start}_{end}')
        pd.to_pickle(env.stk_list, f'{self.base_dir}/stk_list/{start}_{end}.pkl')
        stk_list = env.stk_list
        del env, env_test
        gc.collect()
        return model, stk_list

    @abstractmethod
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

    def run_backtest(self, rolling_period_info=None, start_cash=None, n_cpu=1, model_kwd=None, send_msg=False):
        if model_kwd is None:
            model_kwd = self.model_kwd
        for train_start, train_end, test_start, test_end in tqdm(rolling_period_info):
            model, stk_list = self.train_model(train_start, train_end, n_cpu, model_kwargs=model_kwd)
            self.pred(model, stk_list, test_start, test_end)
            if send_msg:
                send_message(['015664'], f'{test_start}-{test_end} is done')


train_period = 20
test_period = 20
path = f'{root_path}/TainingRes/A2CTest2_train{train_period}_test{test_period}/'
if not os.path.exists(path):
    recusrsive_mkdir(path)
train_conn = TrainBase(20170101, 20201231, base_dir=path, model_kwd={'policy': "MlpPolicy", 'verbose': True}, env_kwd={'reward_type': 'total_return'})
period_info = train_conn.split_date_period(train_period, test_period)
train_conn.run_backtest(period_info, n_cpu=10)

# from stable_baselines3.common.policies import ActorCriticPolicy

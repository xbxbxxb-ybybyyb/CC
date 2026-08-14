# @Time : 2021/6/21 22:35
# @Author : Zhichen Lu
# @File : trainRL.py

import pandas as pd

from stable_baselines3 import A2C
from R2D2.Env.FixEnv import StockEnv
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
import time
from stable_baselines3.common.logger import configure

import gym

start = 20170101
end = 20170430
rwd_tp = 'total_return'
base_path = '/data/user/015664/R2D2/A2C/'

env = StockEnv(start=start, end=end,reward_type=rwd_tp)
env_test,_ = env.get_multiproc_env(5)
# env_test = DummyVecEnv([lambda : StockEnv()])

model = A2C(
    policy="MlpPolicy",
    env=env_test,
    tensorboard_log=f'{base_path}log/',
    verbose=True,
    # policy_kwargs=policy_kwargs,
    # **model_kwargs,
)
e = time.time()
model.learn(total_timesteps=200000,
    eval_log_path=f'{base_path}training_log.log')

total =time.time() - e

model.save(f'{base_path}/test_model_{start}_{end}_{rwd_tp}')

print(f'total learn time:{total}')
from dataApi.sendInfo import send_message

send_message(['015664'], f'total learn time:{total}')

env_test = StockEnv(start=20170501, end=20170531, reward_type=rwd_tp)

model = A2C.load(f'{base_path}/test_model_{start}_{end}_{rwd_tp}')

obs = env_test.reset()
termial = False
action_list = []
while not termial:
    action = model.predict(obs)
    obs, reward, termial, _ = env_test.step(action[0])
    print(reward)
    action_list.append(action)

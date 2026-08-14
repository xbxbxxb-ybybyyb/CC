# coding: utf-8
# Author：fengchi863
# Date ：2021/6/3 15:21

## Model Parameters
A2C_PARAMS = {'n_steps':5,
			  'ent_coef':0.01,
			  'learning_rate':0.0007,
			  'verbose':0,
			  'timesteps':20000}
PPO_PARAMS = {'n_steps':128,
			  'ent_coef':0.01,
			  'learning_rate':0.00025,
			  'nminibatches':4,
			  'verbose':0,
			  'timesteps':20000}
TD3_PARAMS = {'batch_size':128,
			   'buffer_size':50000,
			   'learning_rate':1e-4,
			   'verbose':0,
			   'timesteps':20000}
SAC_PARAMS = {'batch_size': 64,
			  'buffer_size': 100000,
			  'learning_rate': 0.0001,
			  'learning_starts':100,
			  'batch_size':64,
			  'ent_coef':'auto_0.1',
			  'timesteps': 50000,
			  'verbose': 0}

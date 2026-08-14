# coding: utf-8
# Author：fengchi863
# Date ：2021/6/3 15:32

from stable_baselines.common.vec_env import DummyVecEnv

class EnvSetup:
    def __init__(self,
                 stock_dim: int,
                 state_space: int,
                 hmax=100,
                 initial_amount=1000000,
                 transaction_cost_pct=0.001,
                 reward_scaling=1e-4):
        self.stock_dim = stock_dim
        self.hmax = hmax
        self.initial_amount = initial_amount
        self.transaction_cost_pct = transaction_cost_pct
        self.reward_scaling = reward_scaling
        # account balance + close price + shares + technical indicators
        self.state_space = state_space
        self.action_space = self.stock_dim

    def create_env_training(self, data, env_class, turbulence_threshold=150):
        env_train = DummyVecEnv([lambda: env_class(df=data,
                                                   stock_dim=self.stock_dim,
                                                   hmax=self.hmax,
                                                   initial_amount=self.initial_amount,
                                                   transaction_cost_pct=self.transaction_cost_pct,
                                                   reward_scaling=self.reward_scaling,
                                                   state_space=self.state_space,
                                                   action_space=self.action_space,
                                                   turbulence_threshold=turbulence_threshold)])
        return env_train

    def create_env_validation(self, data, env_class, turbulence_threshold=150):
        env_validation = DummyVecEnv([lambda: env_class(df=data,
                                                        stock_dim=self.stock_dim,
                                                        hmax=self.hmax,
                                                        initial_amount=self.initial_amount,
                                                        transaction_cost_pct=self.transaction_cost_pct,
                                                        reward_scaling=self.reward_scaling,
                                                        state_space=self.state_space,
                                                        action_space=self.action_space,
                                                        turbulence_threshold=turbulence_threshold)])
        obs_validation = env_validation.reset()

        return env_validation, obs_validation

    def create_env_trading(self, env_class, data, turbulence_threshold=150):
        env_trade = DummyVecEnv([lambda: env_class(df=data,
                                                   stock_dim=self.stock_dim,
                                                   hmax=self.hmax,
                                                   initial_amount=self.initial_amount,
                                                   transaction_cost_pct=self.transaction_cost_pct,
                                                   reward_scaling=self.reward_scaling,
                                                   state_space=self.state_space,
                                                   action_space=self.action_space,
                                                   turbulence_threshold=turbulence_threshold)])
        obs_trade = env_trade.reset()

        return env_trade, obs_trade
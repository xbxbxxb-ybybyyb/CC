import math

import numpy as np
from collections import deque
import torch


class TradingFilterEnv(object):
    def __init__(self, data_provider, init_balance=1.0, open_fee=0.00009, close_fee=0.00009):
        self.data = data_provider
        self.init_balance = 1
        self.total_money = 100000000
        self.open_fee = open_fee
        self.close_fee = close_fee
        self.max_position = 1.0
        self.clock = 15
        self.last_trade_action = 0
        self.action_space = np.array([-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.10, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        self.position = 0.0
        self.real_position = 0.0
        self.reset()

    def reset(self):
        self.balance = self.init_balance
        self.position = 0.0
        self.net_returns = deque(maxlen=50)
        self.cumulative_return = 0.0
        self.current_step = 0
        self.clock = 15
        self.last_trade_action = 0
        self.volatility = self._update_volatility()

        return self._get_observation()

    def _get_observation(self):
        factors = self.data.get_factors(self.current_step)
        return {
            'factors': factors,
            'state': {
                'cum_return': self.cumulative_return,
                'position': self.position,
                'volatility': self.volatility
            }
        }

    def _update_volatility(self):
        prices = self.data.get_obs_price(self.current_step)
        clean_price = prices[~np.isnan(prices)]
        self.volatility = np.std((clean_price[1:] - clean_price[:-1]) / clean_price[:-1]) * 1000
        return self.volatility

    # returns = np.array(self.net_returns)
    # mean_return = returns.mean() * 100
    # std_return = returns.std() * 100 + 1e-6
    # self.sharpe_ratio = mean_return / std_return * math.sqrt(250) if std_return > 0 else 0.0
    # self.volatility = returns.std() * 100 #+ 1e-6
    # print(self.volatility)

    def get_panalty(self, action):
        delta = 0
        if self.current_step != 0 and self.current_step != 1 and action == 0 and self.clock >= 10:
            delta = 0.8 * (math.sqrt(self.clock) - 9)
        if self.volatility > 0.65 and abs(action) >= 0.15:
            delta = -10
        if self.volatility < 0.35 and abs(action) <= 0.05:
            delta = -10
        if self.volatility > 0.65 and abs(action) <= 0.05:
            delta = 10
        if self.volatility < 0.35 and abs(action) >= 0.15:
            delta = 10

        return 0.00003 * (abs(self.last_trade_action) + abs(action) + delta) / (
                    math.sqrt(self.clock) * pow(self.volatility, 2))
        # prices = self.data.get_obs_price(self.current_step)

    # def _calculate_transaction_cost(self, old_pos, new_pos, trade_amount):
    #     # if np.sign(old_pos) != np.sign(new_pos):
    #     #    return abs(trade_amount) * self.close_fee
    #     return abs(trade_amount) * self.open_fee #if abs(new_pos) > abs(old_pos) else 0.0

    def _calculate_time_reward(self):
        # self._update_volatility()
        raw_return = self.net_returns[-1] if self.net_returns else 0.0
        return raw_return * 100

    def get_valid_actions(self):
        return np.array(
            [-self.max_position <= self.position + delta <= self.max_position for delta in self.action_space])

    def step(self, action_idx):
        # 执行动作
        position_delta = self.action_space[action_idx]

        # self._update_volatility()
        if self.current_step >= len(self.data) - 1:
            new_position = 0
        else:
            new_position = np.clip(self.position + position_delta, -self.max_position, self.max_position)
        # print(new_position)
        # 计算价格变化
        old_price = self.data.get_price(self.current_step + 0)
        if self.current_step >= len(self.data) - 1:
            new_price = self.data.get_last_price(self.current_step)
        else:
            new_price = self.data.get_price(self.current_step + 1)

        time10_price = self.data.get_time_10_price(self.current_step)
        price_change = (new_price - old_price) / old_price
        # print("price change is: ", price_change)
        time10_price_change = 0

        for i in range(len(time10_price)):
            time10_price_change += (time10_price[i].item() - old_price) / old_price * ((10 - i) / 10)  # lambda
        # print("time 10 price change is:", time10_price_change)
        # reward_for_train = price_change * new_price
        # 计算成本和收益
        # trade_amount = abs(new_position - self.position)
        old_position = self.position
        fee = abs(new_position - self.position) * self.open_fee
        step_reward = 10000 * ((new_position - self.position) * price_change - fee)
        # if abs(new_position) > 0.75:
        #     step_reward = step_reward * 10.0
        future_reward = 10000 * 0.1 * (new_position - self.position) * time10_price_change
        if abs(new_position) > 0.8:
            future_reward = future_reward * 3.0
        penalty = self.get_panalty(position_delta)
        # future_reward = 0
        train_reward = step_reward + future_reward - penalty



        if math.isnan(train_reward):
            train_reward = 0.0
            future_reward = 0.0
            penalty = 0.0

        position_return = self.position * price_change
        if math.isnan(train_reward):
            position_return = 0.0
            fee = 0.0
        net_return = position_return - fee
        old_real_position = self.real_position
        # 更新状态
        self.net_returns.append(net_return)
        self.cumulative_return += net_return
        self.balance *= (1 + net_return)
        self.position = new_position
        change_flag = 0
        if self.position >= 0.8 and self.real_position == 0 and change_flag == 0:
            self.real_position = 0.5
            change_flag = 1
        if self.position >= 0.9 and self.real_position == 0.5 and change_flag == 0:
            self.real_position = 1
            change_flag = 1
        if self.position <= 0.4 and self.position == 1 and change_flag == 0:
            self.real_position = 0.5
            change_flag = 1
        if self.position <= 0.3 and self.position == 0.5 and change_flag == 0:
            self.real_position = 0
            change_flag = 1

        if self.position <= -0.8   and self.real_position == 0 and change_flag == 0:
            self.real_position = -0.5
            change_flag = 1
        if self.position <= -0.9 and self.real_position == -0.5 and change_flag == 0:
            self.real_position = -1
            change_flag = 1
        if self.position >=-0.4 and self.position == -1 and change_flag == 0:
            self.real_position = -0.5
            change_flag = 1
        if self.position >= -0.3 and self.position == -0.5 and change_flag == 0:
            self.real_position = 0
            change_flag = 1
        if change_flag:
            fee = 0.5 * self.open_fee
        else:
            fee = 0
        time_reward = old_real_position*price_change - fee
        self.current_step += 1
        if action_idx != 5:
            self.clock = 1
            self.last_trade_action = position_delta
        else:
            self.clock += 1
        if self.current_step < len(self.data) - 1:
            self._update_volatility()
        # 返回结果
        done = self.current_step >= len(self.data)
        obs = self._get_observation() if not done else None
        #time_reward = self._calculate_time_reward()
        time_step = self.data.get_timestamp(self.current_step) if not done else None
        info = {
            'balance': self.balance,
            'position': self.position,
            'volatility': self.volatility,
            'step': self.current_step
        }

        # print("reward train time", train_reward, time_reward)
        return obs, train_reward, time_reward, done, info, time_step, step_reward, future_reward, penalty

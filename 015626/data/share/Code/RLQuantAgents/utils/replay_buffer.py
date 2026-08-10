import numpy as np
from collections import deque
import random


class ReplayBuffer(object):
    def __init__(self, capacity, hist_length=15, num_factors=824):
        """
        Args:
            capacity: 最大存储量
            hist_length: 历史因子序列长度
            num_factors: 因子维度
        """
        self.capacity = capacity
        self.hist_length = hist_length
        self.num_factors = num_factors

        # 核心存储结构
        self.factor_sequences = deque(maxlen=capacity)  # 历史因子序列 (hist_length, num_factors)
        self.states = deque(maxlen=capacity)  # 状态三元组 (cum_return, position, volatility)
        self.actions = deque(maxlen=capacity)  # 动作
        self.rewards = deque(maxlen=capacity)  # 即时奖励
        self.dones = deque(maxlen=capacity)  # 终止标记
        self.next_states = deque(maxlen=capacity)  # 下一状态（预计算优化）

    def store_transition(self, factors, state, action, reward, done, next_state):
        """
        存储单次转移
        Args:
            factors: (hist_length, num_factors) 历史因子窗口
            state: (cum_return, position, volatility) 当前状态
            action: 采取的动作
            reward: 即时奖励
            done: 是否终止
            next_state: 下一状态
        """
        assert factors.shape == (self.hist_length, self.num_factors)

        self.factor_sequences.append(factors)
        self.states.append(np.array([state['cum_return'], state['position'], state['volatility']]))
        self.actions.append(float(action))
        self.rewards.append(float(reward))
        self.dones.append(done)
        self.next_states.append(np.array([next_state['cum_return'], next_state['position'], next_state['volatility']]))

    def can_sample(self, batch_size):
        return len(self.factor_sequences) >= batch_size

    def sample(self, batch_size):
        """采样批量数据"""
        assert self.can_sample(batch_size)

        # 确保不采样最后一条数据（因为需要next_factors）
        max_valid_idx = len(self.factor_sequences) - 2
        indices = random.sample(range(max_valid_idx + 1), min(batch_size, max_valid_idx + 1))

        batch = {
            'factors': np.stack([self.factor_sequences[i] for i in indices]),
            'states': np.stack([self.states[i] for i in indices]),
            'actions': np.array([self.actions[i] for i in indices]),
            'rewards': np.array([self.rewards[i] for i in indices]),
            'next_factors': np.stack([
                self.factor_sequences[i + 1] if not self.dones[i] else
                np.zeros_like(self.factor_sequences[i])
                for i in indices
            ]),
            'next_states': np.stack([self.next_states[i] for i in indices]),
            'dones': np.array([self.dones[i] for i in indices])
        }
        return batch

    def get_latest(self):
        """获取最新状态"""
        return {
            'factors': self.factor_sequences[-1],
            'state': {
                'cum_return': self.states[-1][0],
                'position': self.states[-1][1],
                'volatility': self.states[-1][2]
            }
        }

# 1. 初始化缓冲区
buffer = ReplayBuffer(capacity=10, hist_length=15, num_factors=824)



from progress.bar import Bar


from models.simpleDQN import SimpleQNetwork
from env.signal_env import TradingFilterEnv
#from env.env import TradingEnv
from env.env import TradingEnv
from utils.replay_buffer import ReplayBuffer
from dataloader.dataprocessor import IntradayEpisodeDataset
from dataloader.dataloader import RLDataLoader
import torch.nn.functional as F
import torch
import torch.optim as optim
import numpy as np
from tensorboardX import SummaryWriter
from collections import deque
import random
import os
from datetime import datetime
from progress.bar import Bar

# 确保可复现性
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)


#
class TradingEvaluator(object):
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 初始化组件
        self._init_components()
        self._init_evaludating()

    def _init_components(self):
        self.val_dataset = IntradayEpisodeDataset(
            factor_path=self.config['factor_path'],
            price_path=self.config['price_path'],
            hist_length=self.config['hist_length'],
            pred_length=self.config['pred_length'],
            train_ratio=1,
            test_pos=[0, 1],
            mode='test'
        )
        self.val_loader = RLDataLoader(
            dataset=self.val_dataset,
            batch_size=1,
            shuffle=False
        )
        self.val_minute_reward_list = []
        self.val_day_reward_list = []
        self.val_minute_pos = []
        self.val_minute_time_step =  []
        self.val_day_time_step = []
        # 3. 交易环境（适配IntradayDataset接口）
        class DatasetAdapter(object):
            def __init__(self, dataset):
                self.dataset = dataset
                self.current_idx = 0

            def get_factors(self, t):
                episode = self.dataset.episodes[self.current_idx]
                return episode['observations'][t].numpy()

            def get_obs_price(self, t):
                episode = self.dataset.episodes[self.current_idx]
                return episode['obs_prices'][t].numpy()

            def get_price(self, t):
                episode = self.dataset.episodes[self.current_idx]
                return episode['targets'][t][1].item()  # 取预测窗口第2个价格

            def get_last_price(self, t):
                episode = self.dataset.episodes[self.current_idx]
                return episode['targets'][t][2].item()  # 取预测窗口第3个价格

            def get_time_10_price(self, t):
                episode = self.dataset.episodes[self.current_idx]
                return episode['targets'][t][1: 1 + 10]

            def get_timestamp(self, t):
                episode = self.dataset.episodes[self.current_idx]
                return episode['time_index'][t]

            def __len__(self):
                return len(self.dataset.episodes[self.current_idx]['observations'])

        self.val_env = TradingFilterEnv(
            data_provider=DatasetAdapter(self.val_dataset),
            init_balance=self.config['init_balance'],
            open_fee=self.config['open_fee'],
            close_fee=self.config['close_fee']
        )
        # 4. 模型
        self.model = SimpleQNetwork(
            factor_dim=self.val_dataset.episodes[0]['observations'].shape[-1],  # 从数据获取因子维度
            d_model=self.config['d_model'],
            num_actions=len(self.val_env.action_space)
        ).to(self.device)
        self.model.load_state_dict(torch.load('/home/appadmin/RLQuantAgents/runs/20250423-161342_dmodel128_lr1e-05/train_epoch11.pt'))
        print('load_success!')

    def _init_evaludating(self):
        """初始化训练相关设置"""
        # 创建日志目录
        self.log_dir = os.path.join(
            "runs",
            datetime.now().strftime("%Y%m%d-%H%M%S") + \
            f"_dmodel{self.config['d_model']}_lr{self.config['lr']}_test"
        )
        os.makedirs(self.log_dir, exist_ok=True)
        self.writer = SummaryWriter(self.log_dir, max_queue=1)

    def _run_episode(self, env, data_loader, episode_idx, is_training=False):
        """运行单个episode"""
        # 通过DataLoader获取episode
        # batch = next(iter(data_loader))
        # factors, prices = batch['observations'], batch['targets']
        episode_length = next(iter(data_loader))['observations'].shape[0]
        # episode_length = lengths[0].item()  # 取第一个样本的长度
        episode_loss = 0
        # 初始化环境状态
        env.data.current_idx = episode_idx #% len(self.dataset.episodes)
        obs = env.reset()
        episode_reward = 0
        done = False

        for step in range(episode_length):
            with torch.no_grad():
                factors_tensor = torch.FloatTensor(obs['factors']).unsqueeze(0).to(self.device)
                state_tensor = torch.FloatTensor([
                    obs['state']['position'],
                    obs['state']['volatility']
                ]).unsqueeze(0).to(self.device)

                q_values, _,_,_,_ = self.model(factors_tensor, state_tensor)
                # 过滤无效动作
                valid_mask = torch.unsqueeze(torch.BoolTensor(env.get_valid_actions()).to(self.device), dim=0)
                q_values[~valid_mask] = -float('inf')
                action = q_values.argmax().item()

            # 2. 执行动作
            print(action)
            next_obs, train_reward, time_reward, done, info, time_stamp, step_reward, future_reward, penalty = env.step(
                action)

            self.val_minute_reward_list.append(float(time_reward))
            self.val_minute_pos.append(float(info['position']))
            self.val_minute_time_step.append(time_stamp)

            obs = next_obs
            episode_reward += time_reward

            if done:
                break
        return episode_reward

    def validate(self):
        self.model.eval()
        bar = Bar('Validate Process:', max=len(self.val_dataset))
        total_reward = 0
        for idx in range(len(self.val_dataset)):
            episode_reward = self._run_episode(self.val_env,
                                                                                                self.val_loader,
                                                                                                episode_idx=idx,
                                                                                                is_training=False)
            self.val_day_reward_list.append(float(episode_reward))
            self.val_day_time_step.append(self.val_minute_time_step[-1])
            total_reward += episode_reward
            bar.next()
            bar.suffix = f'Episode Reward: {episode_reward:.2f} | Mean Reward: {total_reward / (idx+1):.2f} | Total Reward: {total_reward:.2f}'
        return total_reward


    def eval(self):
        """主训练循环"""
        self.model.eval()
        self.val_minute_reward_list = []
        self.val_day_reward_list = []
        self.val_minute_pos = []
        self.val_minute_time_step =  []
        self.val_day_time_step = []

        val_rewards = self.validate()
        import pickle
        f = open(os.path.join(self.log_dir, f'val_day_reward.pkl'), 'wb')
        pickle.dump(self.val_day_reward_list, f)
        f.close()
        f = open(os.path.join(self.log_dir, f'val_minute_reward.pkl'), 'wb')
        pickle.dump(self.val_minute_reward_list, f)
        f.close()
        f = open(os.path.join(self.log_dir, f'val_day_timestamp.pkl'), 'wb')
        pickle.dump(self.val_day_time_step, f)
        f.close()
        f = open(os.path.join(self.log_dir, f'val_minute_timestamp.pkl'), 'wb')
        pickle.dump(self.val_minute_time_step, f)
        f.close()
        f = open(os.path.join(self.log_dir, f'val_minute_pos.pkl'), 'wb')
        pickle.dump(self.val_minute_pos, f)
        f.close()

# 配置参数
CONFIG = {
    # 数据参数
    'factor_path': '/dfs/group/800466/intern/wyb/23_X.pkl',
    'price_path': '/dfs/group/800466/intern/wyb/23_y.pkl',
    'hist_length': 15,
    'pred_length': 15,

    # 环境参数
    'init_balance': 1.0,
    'open_fee': 0.00009,
    'close_fee': 0.00009,
    # 模型参数
    'd_model': 128,
    'nhead': 4,
    'num_layers': 3,
    # 训练参数
    'epoches': 45,
  #  'episodes': 1000,
    'batch_size': 1,
    'sample_batch_size': 64,
    'buffer_size': 75000,
    'lr': 7e-5,
    'weight_decay': 1e-5,
    'gamma': 0.995,
    'epsilon': 1.0,
    'epsilon_min': 0.045,
    'epsilon_decay': 0.99,
    'target_update': 1100,
    'save_interval': 400
}

if __name__ == "__main__":
    evaluator = TradingEvaluator(CONFIG)
    evaluator.eval()

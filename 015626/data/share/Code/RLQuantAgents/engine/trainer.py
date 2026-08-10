from models.TransDQN import TransformerQNetwork
from models.simpleDQN import SimpleQNetwork
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
class TradingTrainer(object):
    def __init__(self, config):
        self.config = config
        self.device = self.config['device']

        # 初始化组件
        self._init_components()
        self._init_training()

    def _init_components(self):
        """初始化所有核心组件"""
        # 1. 数据集和数据加载器
        self.dataset = IntradayEpisodeDataset(
            factor_path=self.config['factor_path'],
            price_path=self.config['price_path'],
            hist_length=self.config['hist_length'],
            pred_length=self.config['pred_length'],
            train_start_time=self.config['train_start_time'],
            train_end_time=self.config['train_end_time'],
            train_ratio=1,
            test_pos=None,
            mode='train',
        )
        self.val_dataset = IntradayEpisodeDataset(
            factor_path=self.config['val_factor_path'],
            price_path=self.config['val_price_path'],
            hist_length=self.config['hist_length'],
            pred_length=self.config['pred_length'],
            test_start_time=self.config['test_start_time'],
            test_end_time=self.config['test_end_time'],
            mode='test'
        )
        # 2. 使用RLLoader加载数据
        g = torch.Generator()
        g.manual_seed(42)
        self.data_loader = RLDataLoader(
            dataset=self.dataset,
            batch_size=1,
            shuffle=False,
        )
        self.val_loader = RLDataLoader(
            dataset=self.val_dataset,
            batch_size=1,
            shuffle=False
        )
        # minute level
        self.train_minute_reward_list = []
        # day level
        self.train_day_reward_list = []
        self.val_minute_reward_list = []
        self.val_day_reward_list = []
        self.train_episode_loss = []
        self.train_minute_pos = []
        self.val_minute_pos = []
        self.train_minute_time_step = []
        self.val_minute_time_step = []
        self.train_day_time_step = []
        self.val_day_time_step = []

        # 3. 交易环境（适配IntradayDataset接口）f
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

        self.env = TradingEnv(
            data_provider=DatasetAdapter(self.dataset),
            init_balance=self.config['init_balance'],
            open_fee=self.config['open_fee'],
            close_fee=self.config['close_fee']
        )
        self.val_env = TradingEnv(
            data_provider=DatasetAdapter(self.val_dataset),
            init_balance=self.config['init_balance'],
            open_fee=self.config['open_fee'],
            close_fee=self.config['close_fee']
        )
        # 4. 模型
        self.model = SimpleQNetwork(
            factor_dim=self.dataset.episodes[0]['observations'].shape[-1],  # 从数据获取因子维度
            d_model=self.config['d_model'],
            num_actions=len(self.env.action_space)
        ).to(self.device)

        # 5. 目标网络
        self.target_model = SimpleQNetwork(
            factor_dim=self.dataset.episodes[0]['observations'].shape[-1],
            d_model=self.config['d_model'],
            num_actions=len(self.env.action_space)
        ).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())

        # 6. 优化器
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config['lr'],
            weight_decay=self.config['weight_decay']
        )

        # 7. 使用您之前提供的ReplayBuffer
        self.replay_buffer = ReplayBuffer(
            capacity=self.config['buffer_size'],
            hist_length=self.config['hist_length'],
            num_factors=self.dataset.episodes[0]['observations'].shape[-1]
        )

    def _init_training(self):
        """初始化训练相关设置"""
        # 创建日志目录
        self.log_dir = os.path.join(
            "runs",
            datetime.now().strftime("%Y%m%d-%H%M%S") + \
            f"_dmodel{self.config['d_model']}_lr{self.config['lr']}"
        )
        os.makedirs(self.log_dir, exist_ok=True)
        self.writer = SummaryWriter(self.log_dir, max_queue=1)

        # 训练状态跟踪
        self.global_step = 0
        self.episode = 0
        # self.best_sharpe = -np.inf

    def _store_transition(self, transition):
        """存储转移样本到ReplayBuffer"""
        self.replay_buffer.store_transition(
            # timestamp=transition['timestamp'],
            factors=transition['factors'],
            state=transition['state'],
            # position=transition['state'][1],  # position在state的索引1
            action=transition['action'],
            reward=transition['reward'],
            done=transition['done'],
            next_state=transition['next_state']
            # cum_return=transition['state'][0],  # cum_return在state的索引0
            # sharpe=transition['state'][2]  # sharpe在state的索引2
        )

    def _sample_batch(self):
        """从ReplayBuffer采样批次"""
        if len(self.replay_buffer.factor_sequences) < self.config['sample_batch_size']:
            return None

        batch = self.replay_buffer.sample(self.config['sample_batch_size'])
        # 转换为PyTorch张量
        return {
            'factors': torch.FloatTensor(batch['factors']).to(self.device),
            'states': torch.FloatTensor(batch['states']).to(self.device),
            'actions': torch.LongTensor(batch['actions']).to(self.device),
            'rewards': torch.FloatTensor(batch['rewards']).to(self.device),
            'next_factors': torch.FloatTensor(batch['next_factors']).to(self.device),
            'next_states': torch.FloatTensor(batch['next_states']).to(self.device),
            'dones': torch.FloatTensor(batch['dones']).to(self.device)
        }

    def _train_step(self):
        """执行单次训练更新"""
        if self.global_step < self.config['learning_starts']:
            return None
        batch = self._sample_batch()
        if batch is None:
            return None

        # 1. 计算当前Q值
        current_q, _, _, _, _ = self.model(batch['factors'], batch['states'])
        current_q = current_q.gather(1, batch['actions'].unsqueeze(1))
        # 2. 计算目标Q值 (Double DQN)

        with torch.no_grad():
            next_q, _, _, _, _ = self.model(batch['next_factors'], batch['next_states'])
            next_actions = next_q.argmax(dim=1, keepdim=True)
            next_q_target, _, _, _, _ = self.target_model(batch['next_factors'], batch['next_states'])
            next_q_target_values = next_q_target.gather(1, next_actions).squeeze(1)
            target_q = batch['rewards'] + (1 - batch['dones']) * self.config['gamma'] * next_q_target_values
            target_q = torch.nan_to_num(target_q, nan=0.0)
        # 3. 计算损失
        loss = F.mse_loss(current_q.squeeze() * (1 - batch['dones']), target_q * (1 - batch['dones']))
        # 4. 反向传播
        self.optimizer.zero_grad()
        # if has_nan:
        #     print("next factors")
        #     print(batch['next_factors'])
        #     print("cu_q, tar_q, loss", current_q.squeeze(), target_q, loss)
        #     print("batch rewards")
        #     print(batch['rewards'])
        #     print("batch dones")
        #     print(batch['dones'])
        #     print("next q")
        #     print(next_q)
        #     print("next_q max")
        #     print(next_q.max(1)[0])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=0.9)
        self.optimizer.step()
        # return loss.item()
        return loss.item()

    def _run_episode(self, env, data_loader, episode_idx, is_training=True):
        """运行单个episode"""
        # 通过DataLoader获取episode
        # print(data_loader.dataset.used_indices)
        # batch = next(iter(data_loader))

        # episode_idx = data_loader.dataset.used_indices[-1]
        # print(episode_idx)
        episode_length = next(iter(data_loader))['observations'].shape[0]
        # episode_length = lengths[0].item()  # 取第一个样本的长度
        episode_loss = 0
        # 初始化环境状态
        env.data.current_idx = episode_idx  # % len(self.dataset.episodes)
        obs = env.reset()
        episode_reward = 0
        done = False
        episode_penalty = 0
        episode_penalty = 0
        episode_step_rw = 0
        episode_fu_rw = 0
        episode_train_rw = 0
        for step in range(episode_length):
            # 1. 选择动作 (ε-greedy)
            if is_training and (
                    random.random() < self.config['epsilon'] or self.global_step < self.config['learning_starts']):
                valid_actions = env.get_valid_actions()
                action = random.choice(np.where(valid_actions)[0])
            else:
                with torch.no_grad():
                    factors_tensor = torch.FloatTensor(obs['factors']).unsqueeze(0).to(self.device)
                    state_tensor = torch.FloatTensor([
                        obs['state']['position'],
                        obs['state']['volatility']
                    ]).unsqueeze(0).to(self.device)
                    q_values, _, x2, adv, value = self.model(factors_tensor, state_tensor)
                    # 过滤无效动作
                    valid_mask = torch.unsqueeze(torch.BoolTensor(env.get_valid_actions()).to(self.device), dim=0)
                    q_values[~valid_mask] = -float('inf')
                    valid_q = q_values[valid_mask]
                    if torch.isnan(valid_q[0]):
                        print("factors")
                        print(factors_tensor)
                        print("pos")
                        print(obs['state']['position'])
                        print("q")
                        print(q_values)
                        print("x2")
                        print(x2)
                        print("adv")
                        print(adv)
                        print("value")
                        print(value)
                        exit(0)
                    action = q_values.argmax().item()
                    # print(action)

            # 2. 执行动作
            next_obs, train_reward, time_reward, done, info, time_stamp, step_reward, future_reward, penalty = env.step(
                action)
            if is_training:
                self.train_minute_reward_list.append(float(time_reward))
                self.train_minute_pos.append(float(info['position']))
                self.train_minute_time_step.append(time_stamp)
            else:
                self.val_minute_reward_list.append(float(time_reward))
                self.val_minute_pos.append(float(info['position']))
                self.val_minute_time_step.append(time_stamp)
            # 3. 存储转移
            if is_training and not done:
                self._store_transition({
                    # 'timestamp': step,
                    'factors': obs['factors'],
                    'state': obs['state'],
                    #     [
                    #     obs['state']['cum_return'],
                    #     obs['state']['position'],
                    #     obs['state']['sharpe']
                    # ],
                    'action': action,
                    'reward': train_reward,
                    'next_factors': next_obs['factors'],
                    'next_state':
                        next_obs['state'],
                    #     [
                    #     next_obs['state']['cum_return'],
                    #     next_obs['state']['position'],
                    #     next_obs['state']['sharpe']
                    # ],
                    'done': done
                })

                # 4. 训练模型
                loss = self._train_step()
                # 5. 定期更新目标网络
                self.global_step += 1
                if self.global_step % self.config['target_update'] == 0:
                    self.target_model.load_state_dict(self.model.state_dict())
                if loss is not None:
                    episode_loss += loss
                # 6. 记录日志
                # if loss is not None:
                #     self.writer.add_scalar('Loss/step_train', loss, self.global_step)
                # self.writer.add_scalar('Reward/step_train', reward, self.global_step)
                # self.writer.add_scalar('Position/train', info['position'], self.global_step)
                # self.writer.add_scalar('Balance/train', info['balance'], self.global_step)
            # 7. 更新状态
            obs = next_obs

            episode_reward += time_reward
            episode_penalty += penalty
            episode_step_rw += step_reward
            episode_fu_rw += future_reward
            episode_train_rw += train_reward
            if done:
                break

        # 记录episode统计信息
        if is_training:
            self.train_episode_loss.append(float(episode_loss))
            # self.writer.add_scalar('Train_Reward/episode', episode_reward, self.episode)
        # else:
        #    self.writer.add_scalar('Val_Reward/episode', episode_reward, episode_idx)
        # self.writer.add_scalar('Sharpe/episode', sharpe, self.episode)

        # 保存最佳模型
        # if sharpe > self.best_sharpe:
        #     self.best_sharpe = sharpe
        #     torch.save(self.model.state_dict(),
        #                os.path.join(self.log_dir, 'best_model.pt'))

        return episode_reward, episode_penalty, episode_step_rw, episode_fu_rw, episode_train_rw

    def validate(self):
        self.model.eval()
        bar = Bar('Validate Process:', max=len(self.val_dataset))
        total_reward = 0.0
        total_penalty = 0.0
        total_step_rw = 0.0
        total_fu_rw = 0.0
        total_val_rw = 0.0
        for idx in range(len(self.val_dataset)):
            episode_reward, episode_penalty, episode_step_rw, episode_fu_rw, episode_val_rw = self._run_episode(
                self.val_env,
                self.val_loader,
                episode_idx=idx,
                is_training=False)
            self.val_day_reward_list.append(float(episode_reward))
            self.val_day_time_step.append(self.val_minute_time_step[-1])
            total_reward += episode_reward
            total_penalty += episode_penalty
            total_step_rw += episode_step_rw
            total_fu_rw += episode_fu_rw
            total_val_rw += episode_val_rw
            bar.next()

            bar.suffix = f'Episode Reward: {episode_reward:.2f} | Mean Reward: {total_reward / self.episode:.2f} | Total Reward: {total_reward:.2f} | ' \
                         f'MP: {total_penalty / self.episode:.2f} | MS:{total_step_rw / self.episode:.2f} | MF:{total_fu_rw / self.episode:.2f} | MV:{total_val_rw / self.episode:.2f}'
        return total_reward

    def train(self):
        """主训练循环"""
        best_rewards = -np.inf
        best_val_rewards = -np.inf
        print(f"Starting training with config:\n{self.config}")
        print(f"Device: {self.device}")
        indices = torch.arange(0, len(self.dataset))
        shuffled = indices[torch.randperm(len(indices))]
        idxs = shuffled.tolist()
        for i in range(self.config['epoches']):
            self.model.train()
            self.train_minute_reward_list = []
            self.train_day_reward_list = []
            self.val_day_reward_list = []
            self.val_minute_reward_list = []
            self.train_episode_loss = []
            self.train_minute_pos = []
            self.val_minute_pos = []
            self.train_minute_time_step = []
            self.val_minute_time_step = []
            self.train_day_time_step = []
            self.val_day_time_step = []

            self.episode = 0
            bar = Bar(f'Training Epoch {i}:', max=len(self.dataset))
            # print(f"Model architecture:\n{self.model}")
            total_reward = 0.0
            total_penalty = 0.0
            total_step_rw = 0.0
            total_fu_rw = 0.0
            total_train_rw = 0.0
            while self.episode < len(self.dataset):
                # 运行一个episode
                episode_idx = self.episode  # idxs[self.episode]
                episode_reward, episode_penalty, episode_step_rw, episode_fu_rw, episode_train_rw = self._run_episode(
                    self.env,
                    self.data_loader,
                    episode_idx,
                    is_training=True)
                self.train_day_reward_list.append(float(episode_reward))
                self.train_day_time_step.append(self.train_minute_time_step[-1])
                total_reward += episode_reward
                total_penalty += episode_penalty
                total_step_rw += episode_step_rw
                total_fu_rw += episode_fu_rw
                total_train_rw += episode_train_rw
                # 打印进度
                # print(f"Episode {self.episode}: Reward={episode_reward:.2f}, "
                #   f"Sharpe={sharpe:.2f}")

                # 衰减ε
                self.config['epsilon'] = max(
                    self.config['epsilon_min'],
                    self.config['epsilon'] * self.config['epsilon_decay']
                )

                self.episode += 1
                bar.next()
                bar.suffix = f'Episode Reward: {episode_reward:.2f} | Mean Reward: {total_reward / self.episode:.2f} | Total Reward: {total_reward:.2f} | ' \
                             f'MP: {total_penalty / self.episode:.2f} | MS:{total_step_rw / self.episode:.2f} | MF:{total_fu_rw / self.episode:.2f} | MT:{total_train_rw / self.episode:.2f}'

                # 定期保存检查点
                # if self.episode % self.config['save_interval'] == 0:
                #     torch.save(
                #         self.model.state_dict(),
                #         os.path.join(self.log_dir, f'model_{self.episode}_epoch_{i}.pt')
                #     )
            if total_reward > best_rewards:
                best_rewards = total_reward
                torch.save(self.model.state_dict(),
                           os.path.join(self.log_dir, 'best_train_model.pt'))
                print('epoch: ', i)
                print('best_rewards:', best_rewards)

            torch.save(self.model.state_dict(),
                       os.path.join(self.log_dir, f'train_epoch{i}.pt'))
            print(f'start validate for Epoch {i}!')

            val_rewards = self.validate()
            if val_rewards > best_val_rewards:
                best_val_rewards = val_rewards
                torch.save(self.model.state_dict(),
                           os.path.join(self.log_dir, 'best_val_model.pt'))
                print('epoch: ', i)
                print('best_val_rewards:', val_rewards)
            import pickle
            f = open(os.path.join(self.log_dir, f'train_day_reward_epoch{i}.pkl'), 'wb')
            pickle.dump(self.train_day_reward_list, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'train_minute_reward_epoch{i}.pkl'), 'wb')
            pickle.dump(self.train_minute_reward_list, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'val_day_reward_epoch{i}.pkl'), 'wb')
            pickle.dump(self.val_day_reward_list, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'val_minute_reward_epoch{i}.pkl'), 'wb')
            pickle.dump(self.val_minute_reward_list, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'train_minute_pos_epoch{i}.pkl'), 'wb')
            pickle.dump(self.train_minute_pos, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'val_minute_pos_epoch{i}.pkl'), 'wb')
            pickle.dump(self.val_minute_pos, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'train_episode_loss_epoch{i}.pkl'), 'wb')
            pickle.dump(self.train_episode_loss, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'val_minute_time_stamp_epoch{i}.pkl'), 'wb')
            pickle.dump(self.val_minute_time_step, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'train_minute_time_stamp_epoch{i}.pkl'), 'wb')
            pickle.dump(self.train_minute_time_step, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'val_day_time_stamp_epoch{i}.pkl'), 'wb')
            pickle.dump(self.val_day_time_step, f)
            f.close()
            f = open(os.path.join(self.log_dir, f'train_day_time_stamp_epoch{i}.pkl'), 'wb')
            pickle.dump(self.train_day_time_step, f)
            f.close()
        # while
        print(f"Training completed. Best Rewards: {best_rewards:.2f}")


# 配置参数
CONFIG = {
    # 数据参数
    # 'factor_path': '/dfs/group/800466/intern/wyb/RAW_DATA/X_IF.pkl',
    # 'price_path': '/dfs/group/800466/intern/wyb/RAW_DATA/y_IF.pkl',
    # 'val_factor_path': '/dfs/group/800466/intern/wyb/RAW_DATA/X_IF.pkl',
    # 'val_price_path': '/dfs/group/800466/intern/wyb/RAW_DATA/y_IF.pkl',
    'factor_path': '/dfs/group/800466/intern/wyb/X.pkl',
    'price_path': '/dfs/group/800466/intern/wyb/y.pkl',
    'val_factor_path': '/dfs/group/800466/intern/wyb/X.pkl',
    'val_price_path': '/dfs/group/800466/intern/wyb/y.pkl',
    'train_start_time': '2017-01-01',
    'train_end_time': '2021-12-31',
    'test_start_time': '2023-01-01',
    'test_end_time': '2023-03-31',
    'hist_length': 15,
    'pred_length': 15,
    'device': 'cuda:1',
    # 环境参数
    'init_balance': 1.0,
    'open_fee': 0.00005,
    'close_fee': 0.00005,

    # 模型参数
    'd_model': 128,
    'nhead': 4,
    'num_layers': 3,
    # 训练参数
    'epoches': 45,
    'learning_starts': 10000,
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
    trainer = TradingTrainer(CONFIG)
    trainer.train()

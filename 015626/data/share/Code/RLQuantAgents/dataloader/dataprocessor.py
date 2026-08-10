import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from torch.nn.utils.rnn import pad_sequence
from tqdm import tqdm


class IntradayEpisodeDataset(Dataset):
    def __init__(self, factor_path, price_path, mode='train', train_ratio=0.85,
                 hist_length=15, pred_length=15, normalize=True, train_start_time=None, test_start_time=None, train_end_time=None, test_end_time=None, test_pos=None, random_seed=42):
        """
        Args:
            hist_length: 历史窗口长度（分钟）
            pred_length: 预测窗口长度（分钟）
            mode: train/test 模式
            normalize: 是否进行标准化
        """
        self.hist_length = hist_length
        self.pred_length = pred_length
        self.mode = mode
        self.train_start_time = train_start_time
        self.train_end_time = train_end_time
        self.test_start_time=test_start_time
        self.test_end_time=test_end_time
        self.normalize = normalize
        np.random.seed(random_seed)
        self.test_pos = test_pos
        # 加载并预处理原始数据
        factors = pd.read_pickle(factor_path).fillna(0)
        prices = pd.read_pickle(price_path)

        # 时间对齐和过滤
        common_idx = factors.index.intersection(prices.index)
        self.factors = factors.loc[common_idx]
        self.prices = prices.loc[common_idx]
        self.dates = pd.to_datetime(common_idx).date

        # 划分训练测试集
        unique_dates = np.unique(self.dates)
        self.unique_dates = unique_dates
        split_idx = int(len(unique_dates) * train_ratio)
        self.train_dates = unique_dates[:split_idx]
        self.test_dates = unique_dates[split_idx:]
        self.volatility = []
        self.start_end = []
        # 生成episode数据
        self.episodes = self._create_episodes()

    def _create_episodes(self):
        episodes = []
        if self.mode=='train':
            start_date = pd.Timestamp(self.train_start_time).date()
            end_date = pd.Timestamp(self.train_end_time).date()
            selected_dates = [date for date in self.unique_dates if start_date<=date<=end_date]
        else:
            start_date = pd.Timestamp(self.test_start_time).date()
            end_date = pd.Timestamp(self.test_end_time).date()
            selected_dates = [date for date in self.unique_dates if start_date <= date <= end_date]
        #selected_dates = self.train_dates if self.mode == 'train' else self.test_dates
        # if self.test_pos is not None:
        #     selected_dates = self.unique_dates[int(len(self.unique_dates) * self.test_pos[0]):int(
        #         len(self.unique_dates) * self.test_pos[1])]
        min_length = self.hist_length + self.pred_length  # 最小数据要求
        max_val = 0
        min_val = 0
        for date in tqdm(selected_dates):
            date_mask = self.dates == date
            day_factors = self.factors[date_mask]
            day_prices = self.prices[date_mask].values.astype(np.float32)

            # 排除数据不足的交易日
            if len(day_factors) < min_length:
                continue

            # # 当日数据标准化（仅对因子）
            # if self.normalize:
            #     scaler = StandardScaler().fit(day_factors.values)
            #     features = scaler.transform(day_factors.values)
            # else:
            features = day_factors.values.astype(np.float32)

            # 生成序列数据
            observations = []
            targets = []
            obs_prices = []
            max_start = len(day_factors) - self.pred_length
            for t in range(self.hist_length, max_start):
                hist_window = features[t - self.hist_length:t]  # 历史因子窗口
                hist_window = torch.nan_to_num(torch.tensor(hist_window, dtype=torch.float32), nan=0.0)
                hist_window = torch.clamp(hist_window, min=-1.5, max=1.5)
                assert not torch.isnan(hist_window).any()
                future_prices = day_prices[t:t + self.pred_length]  # 未来价格窗口
                obs_price = day_prices[t - self.hist_length:t]
                # obs_prices = torch.()
                # assert not torch.isnan(torch.tensor(future_prices, dtype=torch.float32)).any()
                observations.append(hist_window)
                obs_prices.append(torch.tensor(obs_price, dtype=torch.float32))
                targets.append(torch.tensor(future_prices, dtype=torch.float32))

                clean_price = obs_price[~np.isnan(obs_price)]
                volatility = np.std((clean_price[1:] - clean_price[:-1]) / clean_price[:-1]) * 1000
                start_end = clean_price[0] - clean_price[-1]
                self.start_end.append(start_end)
                self.volatility.append(volatility)

            episodes.append({
                'observations': torch.stack(observations),  # (T, hist_len, num_features)
                'obs_prices': torch.stack(obs_prices),  # (T, hist_len)
                'targets': torch.stack(targets),  # (T, pred_len)
                'date': date,
                'time_index': day_factors.index[self.hist_length:max_start]
            })

        vol = 0
        high_low_red = 0
        red_idx = 0
        high_low_green = 0
        green_idx = 0
        for i in range(len(self.volatility)):
            vol += self.volatility[i]
        for i in range(len(self.start_end)):
            if self.start_end[i]>0:
                high_low_red += self.start_end[i]
                red_idx += 1
            else:
                high_low_green += self.start_end[i]
                green_idx += 1


        print(vol / len(self.volatility))
        print(high_low_red / red_idx)
        print(high_low_green / green_idx)
        print(max(self.start_end))
        print(min(self.start_end))
        print(max(self.volatility))
        return episodes

    def __len__(self):
        return len(self.episodes)

    def __getitem__(self, idx):
        """返回一个完整交易日的episode数据"""
        return self.episodes[idx]['observations'], self.episodes[idx]['targets']


if __name__ == '__main__':
    # factor_data = pd.read_pickle('/dfs/group/800466/intern/X.pkl')
    # print(factor_data.columns)
    # print(factor_data.head())
    # y_data = pd.read_pickle('/dfs/group/800466/intern/y.pkl')
    # print(y_data.columns)
    # print(len(factor_data))
    # print(len(y_data))
    dataset = IntradayEpisodeDataset('/dfs/group/800466/intern/wyb/17_22_X.pkl', '/dfs/group/800466/intern/wyb/17_22_y_index.pkl',
                                     mode='train', train_ratio=1)
    print(len(dataset))
    # for i in range(len(dataset)):
    print(dataset.episodes[0]['time_index'])
    # exit(dataset.episodes[-1]['time_index'])

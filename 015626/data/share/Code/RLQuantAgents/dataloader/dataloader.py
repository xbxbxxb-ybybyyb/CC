from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence
import torch
from torch.utils.data import DataLoader

def collate_episodes(batch):
    obs_list = [item[0] for item in batch]
    target_list = [item[1] for item in batch]
    obs_tensor = torch.stack(obs_list, dim=0)
    target_tensor = torch.stack(target_list, dim=0)
    print(target_tensor.shape)
    print(obs_tensor.shape)
    return {
        'observations': obs_tensor.permute(1, 0, 2, 3),  # (max_T,batch_size, seq_len, features)
        'targets': target_tensor.permute(1, 0, 2, 3),  # (max_T, batch_size, seq_len, features)
    }


class RLDataLoader(DataLoader):
    """优化后的强化学习数据加载器"""
    def __init__(self, dataset, batch_size=1, shuffle=False, generator=None,num_workers=0):
        self.dataset = dataset
        super().__init__(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            collate_fn=collate_episodes,
            num_workers=num_workers,
            pin_memory=True,
            generator=generator
        )
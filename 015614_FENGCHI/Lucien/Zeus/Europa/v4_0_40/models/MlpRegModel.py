# coding: utf-8
# Author：fengchi863
# Date ：2023/12/13 17:07

from torch.utils.data import DataLoader
import torch.nn as nn
import torch.optim as optim
import torch
import numpy as np
import scipy.stats as stats
from Zeus.Europa.v4_0_40.models.MLP import MLP
from Zeus.Europa.v4_0_40.models.utils import *

class MlpRegModel:

    def __init__(self, input_dim, hidden_dim, dropout, layers, epochs, gpu_id, lr, batch_size, wd, seed):
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        self.epochs = epochs
        self.device = self.set_device(gpu_id)
        self.batch_size = batch_size
        self.loss = nn.MSELoss().to(self.device)
        self.model = MLP(input_dim, [hidden_dim] + [hidden_dim // 2] * (layers - 1), dropout).to(self.device)

        self.init_lr = lr
        self.optimizer = optim.Adam([{'params': [param for name, param in self.model.named_parameters()], 'lr': lr, 'weight_decay': wd}])

    @staticmethod
    def set_device(gpu_id):
        if gpu_id is None:
            return 'cpu'
        else:
            return 'cuda:{}'.format(gpu_id)

    def torch_loader(self, x, y=None, mode='train'):
        shuffle = True if mode == 'train' else False
        dataset = BaseDataset(x, y)
        loader = DataLoader(dataset, batch_size=self.batch_size, num_workers=8, pin_memory=True, shuffle=shuffle)
        return loader

    def train(self, x, y, x_test=None, y_test=None):
        data_loader = self.torch_loader(x, y, 'train')
        for epoch_i in range(self.epochs):
            train_loss = self.train_one_epoch(data_loader, epoch_i)
            if x_test is not None:
                pred_test = self.predict(x_test)
                ic = stats.spearmanr(pred_test.flatten(), y_test.flatten())[0]
                mse = np.mean((pred_test - y_test) ** 2)
                print(f'Epoch {epoch_i}/{self.epochs}, IC {round(ic, 3)}, Loss {round(train_loss, 3)}, MSE {round(mse, 3)}')

    def train_one_epoch(self, data_loader, epoch_i):
        self.model.train()
        losses = AverageMeter()
        for i, (inputs, targets) in enumerate(data_loader):
            inputs = inputs.to(self.device).float()
            targets = targets.to(self.device).float()
            pred = self.model(inputs)
            loss = self.loss(pred, targets)

            losses.update(to_python_float(loss), inputs.size(0))

            self.optimizer.zero_grad()
            loss.backward()
            clip_gradient(self.optimizer, 0.5)
            self.optimizer.step()
        print(f'Train Epoch {epoch_i}/{self.epochs}, Loss {round(losses.avg, 2)}')
        return losses.avg

    def predict(self, x):
        out = []
        self.model.eval()
        data_loader = self.torch_loader(x, mode='test')
        for i, (inputs) in enumerate(data_loader):
            inputs = inputs.to(self.device).float()
            pred = self.model(inputs)
            out.append(pred)
        out = torch.cat(out, dim=0).data.cpu().numpy()
        return out

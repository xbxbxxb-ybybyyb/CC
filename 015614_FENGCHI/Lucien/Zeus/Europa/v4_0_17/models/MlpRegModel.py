# coding: utf-8
# Author：fengchi863
# Date ：2023/12/13 17:07

import copy
import os
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import torch

class MlpRegModel:

    def __init__(self, input_dim, hiddens, dropout, norm, layers, epochs, gpu_id, lr, batch_size, wd, seed, dnn_structure='mlp'):
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        self.epochs = epochs
        self.device = self.set_device(gpu_id)
        self.batch_size = batch_size
        self.loss = nn.MSELoss().to(self.device)
        if dnn_structure == 'mlp':
            self.model = MLP(input_dim, [hiddens] + [hiddens // 2] * (layers - 1), dropout).to(self.device)
        elif dnn_structure == 'conv':
            self.model = Conv(input_dim, [hiddens] + [hiddens // 2] * (layers - 1), dropout).to(self.device)

        self.init_lr = lr
        self.x_norm = None
        self.y_norm = None
        self.optimizer = optim.Adam([{'params': [param for name, param in self.model.named_parameters()],
                                      'lr': lr,
                                      'weight_decay': wd}],
                                       betas=(0.9, 0.999))

    @staticmethod
    def set_device(gpu_id):
        if gpu_id is None:
            return 'cpu'
        else:
            return 'cuda:{}'.format(gpu_id)

    @staticmethod
    def statistics(data):
        mean = data.mean(axis=0, keepdims=True)
        std = data.std(axis=0, keepdims=True)
        data_norm = {
            'edge_up': 3,
            'edge_low': -3,
            'mean': mean,
            'std': std
        }
        return data_norm

    def torch_loaders(self, x, y=None, mode='test'):
        if mode == 'train':
            shuffle = True
            self.x_norm = self.statistics(x)
            # self.y_norm = self.statistics(y)
            dataset = BaseDataset(x, y, self.x_norm, self.y_norm)
        else:
            shuffle = False
            dataset = BaseDataset(x, y, self.x_norm)

        loader = DataLoader(dataset, batch_size=self.bs, num_workers=8, pin_memory=True, shuffle=shuffle)
        return loader

    def fit(self, x, y, x_test=None, y_test=None):
        # print(x.shape, y.shape)
        data_loader = self.torch_loaders(x, y, 'train')
        best_model = None
        best_ic = -100
        for epoch_i in range(self.epochs):
            # adjust_lr(self.optimizer, self.init_lr, epoch_i, decay_rate=0.1, decay_epoch=10)
            train_loss = self.train_one_epoch(data_loader, epoch_i)
            if x_test is not None:
                pred_test = self.predict(x_test)
                ic = np.corrcoef(np.stack([pred_test, y_test]))[0, 1]
                if ic > best_ic:
                    best_model = copy.deepcopy((self.model))
                    best_ic = ic
                print('Train-Valid Epoch {}/{}, LR {:.5f} IC {:.4f}/{:.4f}, Loss {:.4f}/{:.4f}'.format(
                    epoch_i, self.epochs, self.optimizer.param_groups[0]['lr'],
                    ic, best_ic,
                    train_loss, np.mean((pred_test - y_test) ** 2)))
        # self.model = best_model
        return 0

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
            # import pdb; pdb.set_trace()
            clip_gradient(self.optimizer, 0.5)
            self.optimizer.step()
            # print(inputs.shape, targets.shape, pred.shape, loss.mean())

            # if i >10:
            #     break
        # print('Train Epoch {}/{}, Loss {:.4f}'.format(epoch_i, self.epochs, losses.avg))

        return losses.avg

    def predict(self, x):
        out = []
        self.model.eval()
        data_loader = self.torch_loaders(x, mode='test')
        for i, (inputs) in enumerate(data_loader):
            inputs = inputs.to(self.device).float()
            pred = self.model(inputs)
            out.append(pred)
            # import pdb; pdb.set_trace()
        out = torch.cat(out, dim=0).data.cpu().numpy()
        return out

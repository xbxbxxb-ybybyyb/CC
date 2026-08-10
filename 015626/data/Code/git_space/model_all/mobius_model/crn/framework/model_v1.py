import copy
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from network.utils import build_network
from framework.dataset import Dataset2D, Dataset3D
from framework.utils import load_pickle, save_pickle


class Model(object):
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.device = None
        self.network = None
        self.criterion = None
        self.optimizer = None
        self.scheduler = None
        self.best_loss = None
        self.best_corr = None
        self.best_dict = None
        self.network = build_network(self.config)

    def train(self, x_train, y_train, x_valid, y_valid):
        # set device
        self.move_to_gpu()

        # set loss function
        if self.config['objective'] is None:
            self.move_to_cpu()
            return None
        elif self.config['objective'] == 'MSE':
            self.criterion = nn.MSELoss()
        elif self.config['objective'] == 'BCE':
            self.criterion = nn.BCEWithLogitsLoss()
        else:
            raise AssertionError('Invalid objective: {}'.format(self.config['objective']))

        # set optimizer
        params_with_wd = []
        params_zero_wd = []
        for name, param in self.network.named_parameters():
            if 'weight' in name:
                params_with_wd.append(param)
            else:
                params_zero_wd.append(param)
        param_group = [
            {'params': params_with_wd, 'weight_decay': self.config['weights_decay']},
            {'params': params_zero_wd, 'weight_decay': 0.0},
        ]
        self.optimizer = torch.optim.Adam(params=param_group, lr=self.config['initial_lr'])

        # set scheduler
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=self.config['shrink_factor'], patience=self.config['shrink_rounds'], min_lr=self.config['minimum_lr'], verbose=False)

        # set best_loss and best_corr
        self.best_loss = +np.inf
        self.best_corr = -np.inf

        # set training dataset
        if self.config['window_size'] is None:
            train_dataset = Dataset2D(x=x_train, y=y_train)
        else:
            train_dataset = Dataset3D(x=x_train, y=y_train, window_size=self.config['window_size'])
        train_sampler = RandomSampler(train_dataset)
        train_loader = DataLoader(train_dataset, sampler=train_sampler, batch_size=self.config['batch_size'], drop_last=False)

        # set validation dataset
        if self.config['window_size'] is None:
            valid_dataset = Dataset2D(x=x_valid, y=y_valid)
        else:
            valid_dataset = Dataset3D(x=x_valid, y=y_valid, window_size=self.config['window_size'])
        valid_sampler = SequentialSampler(valid_dataset)
        valid_loader = DataLoader(valid_dataset, sampler=valid_sampler, batch_size=self.config['batch_size'], drop_last=False)

        # train model
        patience = 0
        for epoch in range(self.config['num_epochs']):
            train_loss = self.run_train(train_loader)
            valid_loss, valid_output, valid_target = self.run_valid(valid_loader)
            valid_corr = self.calculate_metrics(valid_output, valid_target)

            # check criterion
            if valid_corr > self.best_corr + self.config['minimum_boost']:
                patience = 0
                self.best_loss = valid_loss
                self.best_corr = valid_corr
                self.best_dict = copy.deepcopy(self.network.state_dict())
            else:
                patience += 1

            # print info
            lr = self.optimizer.param_groups[0]['lr']
            info = 'epoch: {:03d}, patience: {:02d}, train_loss: {:.4f}, valid_loss: {:.4f}, valid_corr: {:.4f}, lr: {:.2e}'.format(epoch, patience, train_loss, valid_loss, valid_corr, lr)
            action = 'skip' if patience > 0 else 'save'
            info = '{}, {}'.format(info, action)
            self.logger.print(info)

            # check early stop
            if patience >= self.config['early_stop']:
                self.logger.print('Finish training')
                break

            # update learning rate
            self.scheduler.step(valid_loss)

        # post process
        self.network.load_state_dict(self.best_dict)  # reload best state_dict
        self.move_to_cpu()  # move model to cpu
        return None

    def predict(self, x):
        # set device
        self.move_to_gpu()

        # set inference dataset
        if self.config['window_size'] is None:
            infer_dataset = Dataset2D(x=x, y=None)
        else:
            infer_dataset = Dataset3D(x=x, y=None, window_size=self.config['window_size'])
        infer_sampler = SequentialSampler(data_source=infer_dataset)
        infer_loader = DataLoader(dataset=infer_dataset, sampler=infer_sampler, batch_size=self.config['batch_size'], drop_last=False)

        # make prediction
        y_pred = self.run_infer(infer_loader)
        return y_pred

    def run_train(self, data_loader):
        self.network.train()
        train_loss = 0.0
        for x, y in data_loader:
            output = self.network(x.to(self.device))
            target = y.to(self.device)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()
            train_loss = loss.item()
        return train_loss

    def run_valid(self, data_loader):
        self.network.eval()
        valid_samples = 0
        valid_loss = 0.0
        output_list = []
        target_list = []
        for x, y in data_loader:
            output = self.network(x.to(self.device))
            target = y.to(self.device)
            loss = self.criterion(output, target)
            valid_samples += x.shape[0]
            valid_loss += loss.item() * x.shape[0]
            output_list.append(output.detach().cpu().numpy())
            target_list.append(target.detach().cpu().numpy())
        valid_loss = valid_loss / valid_samples
        output = np.concatenate(output_list, axis=0)
        target = np.concatenate(target_list, axis=0)
        return valid_loss, output, target

    def run_infer(self, data_loader):
        self.network.eval()
        output_list = []
        for x, _ in data_loader:
            output = self.network(x.to(self.device))
            output_list.append(output.detach().cpu().numpy())
        output = np.concatenate(output_list, axis=0)
        return output

    def load_model(self, model_path):
        self.network.load_state_dict(load_pickle(model_path))
        return None

    def save_model(self, model_path):
        save_pickle(self.network.state_dict(), model_path)
        return None

    def move_to_cpu(self):
        self.device = 'cpu'
        self.network.to(self.device)
        return None

    def move_to_gpu(self):
        self.device = 'cuda:0'
        self.network.to(self.device)
        return None

    @staticmethod
    def calculate_metrics(output, target):
        output = pd.Series(output)
        target = pd.Series(target)
        corr = output.corr(target)
        return corr

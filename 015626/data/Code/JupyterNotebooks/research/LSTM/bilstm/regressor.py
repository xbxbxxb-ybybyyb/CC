# -*- coding: utf-8 -*-

import time
import copy
import pickle
import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm
from torch.utils.data import DataLoader
from torch.utils.data.sampler import RandomSampler, SequentialSampler
from bilstm.dataset import Dataset
from bilstm.model import Model


class BiLSTMRegressor(object):
    def __init__(self,
                 window_size=60,  # 记忆期
                 hidden_size=200, # 每一层大小
                 num_layers=2,	  # 层数	
                 dropout_prob=0.2, # 替换率 
                 initial_lr=1e-3,   # 学习率 
                 weight_decay=1e-4, # 参数权重（惩罚项）
                 batch_size=4000,   # 并行化大小
                 max_num_epochs=100, # 最大训练轮数
                 max_no_improve=10): # 最大未提升轮数
        self.window_size = window_size
        self.input_size = None
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        self.initial_lr = initial_lr
        self.weight_decay = weight_decay
        self.batch_size = batch_size
        self.max_num_epochs = max_num_epochs
        self.max_no_improve = max_no_improve

        self.use_gpu = torch.cuda.is_available()
        print('use_gpu: ', self.use_gpu)
        self.model = None

    def fit(self, x_train, y_train, x_valid, y_valid):
        assert x_train.shape[0] == y_train.shape[0]
        assert x_valid.shape[0] == y_valid.shape[0]
        assert x_train.shape[1] == x_valid.shape[1]
        self.input_size = x_train.shape[1]

        self.print_config()

        # dataset
        train_dataset = Dataset(window_size=self.window_size, input_size=self.input_size)
        train_dataset.load_data(x_train, y_train)
        train_sampler = RandomSampler(train_dataset)
        train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=self.batch_size)
        print("number of training samples: {}".format(train_dataset.num_samples))

        valid_dataset = Dataset(window_size=self.window_size, input_size=self.input_size)
        valid_dataset.load_data(x_valid, y_valid)
        valid_sampler = SequentialSampler(valid_dataset)
        valid_dataloader = DataLoader(valid_dataset, sampler=valid_sampler, batch_size=self.batch_size)
        print("number of validation samples: {}".format(valid_dataset.num_samples))

        # model
        self.model = Model(window_size=self.window_size,
                           input_size=self.input_size,
                           hidden_size=self.hidden_size,
                           num_layers=self.num_layers,
                           dropout_prob=self.dropout_prob)
        if self.use_gpu:
            self.model.cuda()

        # loss function
        loss_function = nn.MSELoss()

        # optimizer
        optim_group_params = [
            {
                "params": [param for name, param in self.model.named_parameters() if "bias" not in name],
                "lr": self.initial_lr,
                "weight_decay": self.weight_decay,
            },
            {
                "params": [param for name, param in self.model.named_parameters() if "bias" in name],
                "lr": self.initial_lr,
                "weight_decay": 0.0,
            },
        ]
        optimizer = torch.optim.Adam(optim_group_params)

        # scheduler
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2, min_lr=1e-5)

        # train & validate
        num_no_improve = 0
        best_epoch = 0
        best_score = 0.0
        best_state_dict = None
        for epoch in range(self.max_num_epochs):
            print("-------- epoch: {} --------".format(epoch + 1))

            # train
            self.model.train()
            train_loss = 0.0
            time.sleep(0.5)
            bar = tqdm(total=train_dataset.num_samples)
            for step, batch in enumerate(train_dataloader):
                if self.use_gpu:
                    batch = self.cpu_to_gpu(batch)
                inputs = batch["inputs"]  # (batch_size, window_size, input_size)
                targets = batch["targets"]  # (batch_size)
                batch_size = inputs.shape[0]

                outputs = self.model(inputs)

                loss = loss_function(outputs, targets)
                loss.backward()
                train_loss = train_loss + loss.item() * batch_size

                optimizer.step()
                optimizer.zero_grad()

                bar.set_description("lr={:.6f}, loss={:.4f}".format(optimizer.state_dict()["param_groups"][0]["lr"], loss.item()))
                bar.update(batch_size)
            bar.close()
            time.sleep(0.5)
            train_loss = train_loss / train_dataset.num_samples
            print("training loss: {:.4f}".format(train_loss))

            # validate
            self.model.eval()
            valid_loss = 0.0
            y_true_list = []
            y_pred_list = []
            for step, batch in enumerate(valid_dataloader):
                if self.use_gpu:
                    batch = self.cpu_to_gpu(batch)
                inputs = batch["inputs"]  # (batch_size, window_size, input_size)
                targets = batch["targets"]  # (batch_size)
                batch_size = inputs.shape[0]

                with torch.no_grad():
                    outputs = self.model(inputs)

                loss = loss_function(outputs, targets)
                valid_loss = valid_loss + loss.item() * batch_size

                y_true_list.append(targets.detach().cpu().numpy())
                y_pred_list.append(outputs.detach().cpu().numpy())
            valid_loss = valid_loss / valid_dataset.num_samples
            print("validation loss: {:.4f}".format(valid_loss))
            y_true = np.concatenate(y_true_list, axis=0)
            y_pred = np.concatenate(y_pred_list, axis=0)

            # update learning rate
            scheduler.step(valid_loss)

            # metrics
            valid_score = np.corrcoef(y_true, y_pred)[0, 1]
            print("correlation coefficient: {:.4f}".format(valid_score))

            # early stop
            if valid_score > best_score:
                num_no_improve = 0
                best_epoch = epoch
                best_score = valid_score
                print(">> save model parameters <<")
                best_state_dict = copy.deepcopy(self.model.state_dict())
            else:
                num_no_improve += 1
                if num_no_improve == self.max_no_improve:
                    break

        print("-------- best model --------")
        print("best epoch: {}".format(best_epoch + 1))
        print("best score: {:.4f}".format(best_score))
        print("----------------------------")
        self.model.load_state_dict(best_state_dict)

    def predict(self, x_test):
        assert x_test.shape[1] == self.input_size

        self.print_config()

        # dataset
        test_dataset = Dataset(window_size=self.window_size, input_size=self.input_size)
        test_dataset.load_data(x_test, None)
        test_sampler = SequentialSampler(test_dataset)
        test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=self.batch_size)
        print("number of testing samples: {}".format(test_dataset.num_samples))

        # test
        self.model.eval()
        y_pred_list = []
        # time.sleep(0.5)
        bar = tqdm(total=test_dataset.num_samples)
        for step, batch in enumerate(test_dataloader):
            if self.use_gpu:
                batch = self.cpu_to_gpu(batch)
            inputs = batch["inputs"]
            batch_size = inputs.shape[0]

            with torch.no_grad():
                outputs = self.model(inputs)

            y_pred_list.append(outputs.detach().cpu().numpy())

            bar.update(batch_size)
        bar.close()
        # time.sleep(0.5)
        y_pred = np.concatenate(y_pred_list, axis=0)
        return y_pred

    def save(self, model_file):
        param_dict = {
            "window_size": self.window_size,
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout_prob": self.dropout_prob,
            "initial_lr": self.initial_lr,
            "weight_decay": self.weight_decay,
            "batch_size": self.batch_size,
            "max_num_epochs": self.max_num_epochs,
            "max_no_improve": self.max_no_improve,
        }
        state_dict = self.model.state_dict()
        torch.save(self.model.state_dict(), model_file.replace('bin', 'pth'))
        with open(model_file, mode="wb") as file:
            pickle.dump((param_dict, state_dict), file)


    def load(self, param_dict, model_file):
        self.window_size = param_dict["window_size"]
        self.input_size = param_dict["input_size"]
        self.hidden_size = param_dict["hidden_size"]
        self.num_layers = param_dict["num_layers"]
        self.dropout_prob = param_dict["dropout_prob"]

        self.model = Model(window_size=self.window_size,
                           input_size=self.input_size,
                           hidden_size=self.hidden_size,
                           num_layers=self.num_layers,
                           dropout_prob=self.dropout_prob)

        if self.use_gpu:
            state_dict = torch.load(model_file)
            self.model.cuda()
            self.model.load_state_dict(state_dict)
        else:
            state_dict = torch.load(model_file, map_location=torch.device('cpu'))
            self.model.load_state_dict(state_dict)
            self.model.to(torch.device('cpu'))   

    def load3(self, model_file):
        with open(model_file, mode="rb") as file:
            param_dict, state_dict = pickle.load(file)
        
        self.window_size = param_dict["window_size"]
        self.input_size = param_dict["input_size"]
        self.hidden_size = param_dict["hidden_size"]
        self.num_layers = param_dict["num_layers"]
        self.dropout_prob = param_dict["dropout_prob"]
        self.initial_lr = param_dict["initial_lr"]
        self.weight_decay = param_dict["weight_decay"]
        self.batch_size = param_dict["batch_size"]
        self.max_num_epochs = param_dict["max_num_epochs"]
        self.max_no_improve = param_dict["max_no_improve"]

        self.model = Model(window_size=self.window_size,
                           input_size=self.input_size,
                           hidden_size=self.hidden_size,
                           num_layers=self.num_layers,
                           dropout_prob=self.dropout_prob)
        if self.use_gpu:
            self.model.cuda()
        
        self.model.load_state_dict(state_dict)


    def load2(self, model_file):
        self.use_gpu = True
        with open(model_file, mode="rb") as file:
            # 反序列化过程中显式地指定 map_location
            param_dict, buffer = pickle.load(file)
            # buffer = pickle.load(file)
            state_dict = torch.load(io.BytesIO(buffer), map_location=torch.device('cpu'))
        self.use_gpu = False

        self.window_size = param_dict["window_size"]
        self.input_size = param_dict["input_size"]
        self.hidden_size = param_dict["hidden_size"]
        self.num_layers = param_dict["num_layers"]
        self.dropout_prob = param_dict["dropout_prob"]
        self.initial_lr = param_dict["initial_lr"]
        self.weight_decay = param_dict["weight_decay"]
        self.batch_size = param_dict["batch_size"]
        self.max_num_epochs = param_dict["max_num_epochs"]
        self.max_no_improve = param_dict["max_no_improve"]

        self.model = Model(window_size=self.window_size,
                           input_size=self.input_size,
                           hidden_size=self.hidden_size,
                           num_layers=self.num_layers,
                           dropout_prob=self.dropout_prob)
        
        if self.use_gpu:
            self.model.cuda()
        
        self.model.load_state_dict(state_dict)

        if not self.use_gpu:
            self.model.to(torch.device('cpu'))    
        

    def print_config(self):
        print("-------- configuration --------")
        print("window_size   : {}".format(self.window_size))
        print("input_size    : {}".format(self.input_size))
        print("hidden_size   : {}".format(self.hidden_size))
        print("num_layers    : {}".format(self.num_layers))
        print("dropout_prob  : {}".format(self.dropout_prob))
        print("initial_lr    : {}".format(self.initial_lr))
        print("weight_decay  : {}".format(self.weight_decay))
        print("batch_size    : {}".format(self.batch_size))
        print("max_num_epochs: {}".format(self.max_num_epochs))
        print("max_no_improve: {}".format(self.max_no_improve))
        print("-------------------------------")

    @staticmethod
    def cpu_to_gpu(cpu_batch):
        gpu_batch = {}
        for key in cpu_batch.keys():
            gpu_batch[key] = cpu_batch[key].cuda()
        return gpu_batch

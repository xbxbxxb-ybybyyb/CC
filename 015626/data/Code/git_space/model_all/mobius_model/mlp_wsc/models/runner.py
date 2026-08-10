import copy
import torch
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader
from models.datasets import Dataset2D
from torch.utils.data.sampler import RandomSampler, SequentialSampler
from utils.help_functions_wsc import replace_zero, cv_split_helper
from models.config import model_mapping, loss_mapping
from models.utils import model_train, model_valid, model_predict


class NNModelWSC(object):
    def __init__(self,
                 x_path,
                 y_path,
                 logger_used,
                 objective,
                 model,
                 model_params,
                 obj_params,
                 training_params,
                 ret_target,
                 insample_range,
                 outsample_range,
                 x_need_zscore=True,
                 x_need_clip=False,
                 y_label_need_zscore=True,
                 y_label_need_clip=False,
                 x_clip_range=('q_0.005', 'q_0.995'),
                 y_clip_range=('q_0.005', 'q_0.995'),
                 cv_num=5,
                 cv_num_selected=4,
                 ):

        assert (cv_num_selected >= 0) & (cv_num_selected < cv_num)
        assert isinstance(insample_range, tuple) & isinstance(outsample_range, tuple)
        self.x_path = x_path
        self.y_path = y_path
        self.logger_used = logger_used
        self.objective = objective
        self.model_params = model_params
        self.obj_params = obj_params
        self.training_params = training_params
        self.ret_target = ret_target
        self.insample_range = insample_range
        self.outsample_range = outsample_range
        self.x_need_zscore = x_need_zscore
        self.x_need_clip = x_need_clip
        self.y_label_need_zscore = y_label_need_zscore
        self.y_label_need_clip = y_label_need_clip
        self.x_clip_range = x_clip_range
        self.y_clip_range = y_clip_range
        self.cv_num = cv_num
        self.cv_num_selected = cv_num_selected

        self.use_gpu = torch.cuda.is_available()
        self.model = model_mapping[model]
        self.loss_function = loss_mapping[self.objective](**self.obj_params)

        self.x_train = None
        self.y_train = None
        self.x_valid = None
        self.y_valid = None
        self.x_test = None
        self.y_test = None
        self.y_test_index = None
        self.train_dataloader = None
        self.feature_names = None

    def load_data(self):
        x_raw_pd = pd.DataFrame(pd.read_hdf(self.x_path))
        y_raw_pd = pd.DataFrame(pd.read_hdf(self.y_path))[self.ret_target]
        y_raw_pd = y_raw_pd.reindex(x_raw_pd.index)

        self.feature_names = x_raw_pd.columns

        x_raw_pd_ins = x_raw_pd.loc[self.insample_range[0]: self.insample_range[1]]
        y_raw_pd_ins = y_raw_pd.loc[self.insample_range[0]: self.insample_range[1]]
        x_raw_pd_oos = x_raw_pd.loc[self.outsample_range[0]: self.outsample_range[1]]
        y_raw_pd_oos = y_raw_pd.loc[self.outsample_range[0]: self.outsample_range[1]]

        if self.x_need_clip:
            if np.all([isinstance(i, str) for i in self.x_clip_range]):
                assert np.all([i.startswith('q_') for i in self.x_clip_range])
                self.x_clip_range = (x_raw_pd_ins.quantile(float(self.x_clip_range[0][2:])),
                                     x_raw_pd_ins.quantile(float(self.x_clip_range[1][2:])))
            else:
                assert np.all([isinstance(i, (int, float)) for i in self.x_clip_range])
            x_raw_pd_ins = x_raw_pd_ins.clip(self.x_clip_range[0], self.x_clip_range[1], axis=1)
            x_raw_pd_oos = x_raw_pd_oos.clip(self.x_clip_range[0], self.x_clip_range[1], axis=1)

        if self.x_need_zscore:
            temp_mean = x_raw_pd_ins.mean()
            temp_std = x_raw_pd_ins.std()
            x_raw_pd_ins = (x_raw_pd_ins - temp_mean) / replace_zero(temp_std)
            x_raw_pd_oos = (x_raw_pd_oos - temp_mean) / replace_zero(temp_std)

        if self.y_label_need_clip:
            if np.all([isinstance(i, str) for i in self.y_clip_range]):
                assert np.all([i.startswith('q_') for i in self.y_clip_range])
                self.y_clip_range = (y_raw_pd_ins.quantile(float(self.y_clip_range[0][2:])),
                                     y_raw_pd_ins.quantile(float(self.y_clip_range[1][2:])))
            else:
                assert np.all([isinstance(i, (int, float)) for i in self.y_clip_range])
            y_raw_pd_ins = y_raw_pd_ins.clip(self.y_clip_range[0], self.y_clip_range[1])

        if self.y_label_need_zscore:
            y_raw_pd_ins = (y_raw_pd_ins - y_raw_pd_ins.mean()) / y_raw_pd_ins.std()

        if self.objective == 'binary':
            y_raw_pd_ins = (y_raw_pd_ins > 0).astype(int)
        elif self.objective == 'xentropy':
            y_raw_pd_ins = (y_raw_pd_ins - y_raw_pd_ins.min()) / (y_raw_pd_ins.max() - y_raw_pd_ins.min())

        x_raw_pd_ins = x_raw_pd_ins.replace([-np.inf, np.inf], np.nan).fillna(0)
        x_raw_pd_oos = x_raw_pd_oos.replace([-np.inf, np.inf], np.nan).fillna(0)
        y_raw_pd_ins = y_raw_pd_ins.replace([-np.inf, np.inf], np.nan).fillna(0)
        y_raw_pd_oos = y_raw_pd_oos.replace([-np.inf, np.inf], np.nan).fillna(0)

        x_raw_ins = np.array(x_raw_pd_ins, dtype=np.float32)
        y_raw_ins = np.array(y_raw_pd_ins, dtype=np.float32)
        x_raw_oos = np.array(x_raw_pd_oos, dtype=np.float32)
        y_raw_oos = np.array(y_raw_pd_oos, dtype=np.float32)

        if self.cv_num > 1:
            xy_cv = cv_split_helper(x_raw_ins, self.cv_num)
            self.x_train = x_raw_ins[xy_cv[0][self.cv_num_selected]]
            self.y_train = y_raw_ins[xy_cv[0][self.cv_num_selected]]
            self.x_valid = x_raw_ins[xy_cv[1][self.cv_num_selected]]
            self.y_valid = y_raw_ins[xy_cv[1][self.cv_num_selected]]
        else:
            self.x_train = x_raw_ins
            self.y_train = y_raw_ins
            self.x_valid = x_raw_ins
            self.y_valid = y_raw_ins

        self.x_test = x_raw_oos
        self.y_test = y_raw_oos
        self.y_test_index = y_raw_pd_oos.index

    def fit(self):

        self.logger_used.info('Start to load data.', outputs='file')
        self.load_data()
        self.logger_used.info('Data has been loaded.\n', outputs='file')

        # model
        self.model_params['input_size'] = self.x_train.shape[1]
        self.model = self.model(**self.model_params)
        if self.use_gpu:
            self.model.cuda()

        # dataset
        train_dataset = Dataset2D(x=self.x_train, y=self.y_train)
        self.train_dataloader = DataLoader(train_dataset, sampler=RandomSampler(train_dataset),
                                           batch_size=self.training_params['batch_size'])

        valid_dataset = Dataset2D(x=self.x_valid, y=self.y_valid)
        valid_dataloader = DataLoader(valid_dataset, sampler=SequentialSampler(valid_dataset),
                                      batch_size=self.training_params['batch_size'])

        # optimizer
        optim_group_params = [
            {
                "params": [param for name, param in self.model.named_parameters() if "bias" not in name],
                "lr": self.training_params['initial_lr'],
                "weight_decay": self.training_params['l2_regularization'],
            },
            {
                "params": [param for name, param in self.model.named_parameters() if "bias" in name],
                "lr": self.training_params['initial_lr'],
                "weight_decay": 0.0,
            },
        ]
        optimizer = torch.optim.Adam(optim_group_params)

        # scheduler
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3,
                                                               min_lr=2.5e-5, verbose=False)

        # train & validate
        num_no_improve = 0
        best_epoch = 0
        best_score = 0
        best_state_dict = None
        for epoch in range(self.training_params['num_iterations']):
            train_loss = model_train(self.train_dataloader, self.model, self.loss_function, optimizer, self.use_gpu)
            y_true, y_pred, valid_loss = model_valid(valid_dataloader, self.model, self.loss_function, self.use_gpu)
            valid_score = np.corrcoef(y_true, y_pred)[0, 1]

            # update learning rate
            scheduler.step(valid_loss)

            # early stop
            if valid_score > best_score:
                num_no_improve = 0
                best_epoch = epoch
                best_score = valid_score
                best_state_dict = copy.deepcopy(self.model.state_dict())
                self.logger_used.info(f'epoch {epoch} '
                                      f'learning rate: {optimizer.state_dict()["param_groups"][0]["lr"]}, '
                                      f'train loss: {train_loss:.4e}, valid loss: {valid_loss:.4e}, '
                                      f'information coefficient: {valid_score:.4f}, '
                                      f'the best epoch has been updated', outputs='file')
            else:
                num_no_improve += 1
                self.logger_used.info(f'epoch {epoch} '
                                      f'learning rate: {optimizer.state_dict()["param_groups"][0]["lr"]}, '
                                      f'train loss: {train_loss:.4e}, valid loss: {valid_loss:.4e}, '
                                      f'information coefficient: {valid_score:.4f}', outputs='file')
                if num_no_improve == self.training_params['early_stopping_rounds']:
                    break

        self.logger_used.info('-------- best model --------', outputs='both')
        self.logger_used.info(f'best epoch: {best_epoch + 1}', outputs='both')
        self.logger_used.info(f'best score: {best_score:.4f}', outputs='both')
        self.logger_used.info('----------------------------', outputs='both')
        self.model.load_state_dict(best_state_dict)

    def predict(self):

        test_dataset = Dataset2D(x=self.x_test, y=self.y_test)
        test_sampler = SequentialSampler(test_dataset)
        test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=self.training_params['batch_size'])
        y_pred = model_predict(test_dataloader, self.model, self.use_gpu)
        y_pred = pd.Series(y_pred, index=self.y_test_index)
        return y_pred


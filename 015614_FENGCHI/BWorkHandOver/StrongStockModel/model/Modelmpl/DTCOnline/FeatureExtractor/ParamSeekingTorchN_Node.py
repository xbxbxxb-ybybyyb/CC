# @Time : 2021/8/3 10:53
# @Author : Zhichen Lu
# @File : ParamSeeking.py


import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from typing import Dict, List, Tuple, Type, Union
import os,time,gc,datetime
from StrongStockModel.conf.path_config import root_path
import torch
# from torch import nn
from tqdm import tqdm
from torch.utils.data import DataLoader,TensorDataset
import numpy as np
import copy
torch.set_default_tensor_type(torch.DoubleTensor)

def ic(y_pred,y_true):
    return ((y_pred - y_pred.mean(dim=0)).transpose(0,1)*(y_true-y_true.mean())).mean(dim=1)/(y_pred.std(dim=0)*y_true.std())

def corr_matrix(y_pred):
    norm_y = (y_pred - y_pred.mean(dim=0))/y_pred.std(dim=0)
    shape = torch.ones(norm_y.shape)
    return (norm_y.transpose(0,1)@norm_y)/(shape.sum(dim=0)-1)

def myloss(y_pred,y_true,inter_corr_eof=0):
    corr_loss = ic(y_pred, y_true)
    corr_m = corr_matrix(y_pred)
    loss = 1 - (corr_loss).mean() + inter_corr_eof * (corr_m ** 2).mean() ** 0.5
    return loss,corr_loss,corr_m

class NNIC:
    def __init__(self,net_arch=[200,1],opt=torch.optim.SGD,dropout_ratio=0.3):

        self.net_arch =net_arch
        self.train_log = []
        self.val_log = []
        self.opter = opt
        self.model = None
        self.dropout_ratio = dropout_ratio

    def reinitial(self,dim):
        net = (torch.nn.Linear(dim, self.net_arch[0]),torch.nn.Dropout(p=self.dropout_ratio), torch.nn.ReLU())
        pre_dim = self.net_arch[0]
        for temp_dim in self.net_arch[1:]:
            net += (torch.nn.Linear(pre_dim, temp_dim),torch.nn.Dropout(p=self.dropout_ratio), torch.nn.LogSigmoid(),)
            pre_dim = temp_dim
        net = net[:-1]#+(torch.nn.Tanh(),)
        model = torch.nn.Sequential(*net)
        model.double()
        self.model = model

    def predict(self,X):
        if isinstance(X,np.ndarray):
            return self.model(torch.from_numpy(X).double())
        elif isinstance(X,pd.DataFrame):
            return self.model(torch.from_numpy(X.values).double())
        elif isinstance(X,torch.Tensor):
            return self.model(X).item()
        else:
            raise Exception('Wrong input Type')

    def train(self,X,y,val_split=0.1,batch_size=2**12,learning_rate=0.1,early_stop_round=None,
              max_epoch=100,decay_ratio=0.6,decay_round=5,inter_loss_eof=0.5):
        if early_stop_round is None:
            early_stop_round = np.nan
        self.reinitial(X.shape[1])

        if val_split<1:
            split_num = int(X.shape[0]*val_split)
        else:
            split_num = val_split
        train_set = TensorDataset(X[:-split_num], y[:-split_num])
        X_val,y_val = X[-split_num:],y[-split_num:]
        optimizer = self.opter(self.model.parameters(), lr=learning_rate)
        train_loder = DataLoader(dataset=train_set, batch_size=batch_size, shuffle=True, num_workers=10)
        self.train_log,self.val_log = [],[]
        iteration = 0
        last_min = None
        last_min_iter = 0
        best_model = copy.deepcopy(self.model)
        for i in range(max_epoch):
            bar = tqdm(train_loder)
            loss_eval,corr_loss_eval,corr_m_eval =np.nan,np.nan,np.nan
            for batch in bar:
                bar.set_description(f'loss:{loss_eval:.3f}  corr:{corr_loss_eval:.3f} inter:{corr_m_eval:.3f}')
                inputs,labels = batch
                pred = self.model(inputs)

                loss,corr_loss,corr_m_ = myloss(pred,labels,inter_loss_eof)
                loss_eval, corr_loss_eval,corr_m_eval = loss.item(), abs(corr_loss).mean().item(),abs(corr_m_).mean().item()
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                iteration+=1

                if iteration%10==0:
                    val_pred = self.model(X_val)
                    val_loss, val_corr_loss,val_corr_m = myloss(val_pred,y_val,inter_loss_eof)
                    val_loss, val_corr_loss,val_corr_m = val_loss.item(), abs(val_corr_loss).mean().item(),abs(val_corr_m).mean()
                    self.train_log.append([loss_eval,corr_loss_eval ])
                    self.val_log.append([val_loss, val_corr_loss,val_corr_m])
                    print(f'train_loss {loss_eval:.3f} train_corr:{corr_loss_eval:.4f}inter:{corr_m_eval:.3f} ||',
                          f'val_loss {val_loss:.3f} val_corr:{val_corr_loss:.3f} val_inter{val_corr_m:.3f}')

                    if last_min is None:
                        last_min = val_loss
                        last_min_iter = iteration//10
                        continue
                    if val_loss<last_min:
                        last_min = val_loss
                        last_min_iter = iteration//10
                        best_model = copy.deepcopy(self.model)

                    if ((iteration//10 - last_min_iter)%decay_round==0) and ((iteration//10 - last_min_iter)!=0):
                        learning_rate = max(0.001,learning_rate*decay_ratio)
                        optimizer = self.opter(self.model.parameters(), lr=learning_rate)
                    if (iteration//10 - last_min_iter)>early_stop_round:
                        break

            if (iteration // 10 - last_min_iter) > early_stop_round:
                break

        self.model = best_model
model_conf_path = f'{root_path}TempData/model_conf/'
log_path = f'{root_path}TempData/log/'

if not os.path.exists(model_conf_path):
    os.makedirs(model_conf_path)
if not os.path.exists(log_path):
    os.makedirs(log_path)


X_train,y_train = pd.read_pickle(f'{root_path}TempData/TrainSetForNNexTractorOpt.pkl')



nnic = NNIC([400,100],dropout_ratio=0.1)

# X = torch.from_numpy(X_train.values).double()
# y = torch.from_numpy(y_train['actual_label'].values).double()

nnic.train(X=torch.from_numpy(X_train.values).double(),y=torch.from_numpy(y_train['actual_label'].values).double(),
           val_split=150000,early_stop_round=10,max_epoch=15,learning_rate=0.1,decay_ratio=0.5,decay_round=4)


X_test,y_test = pd.read_pickle(f'{root_path}TempData/TestSetForNNexTractorOpt.pkl')
pred_test = nnic.model(torch.from_numpy(X_test.values))
pred_test = pred_test.detach().numpy()

check = np.concatenate((pred_test,y_test.values),axis=1)
corr = pd.DataFrame(check).corr()
corr
# pred_test = pd.DataFrame(pred_test,index=X_test.index)
#
# # X_val,y_val = torch.from_numpy(X_test.values),torch.from_numpy(y_test['actual_label'].values)
# # a = pd.Series({each:y_test.corrwith(X_test[each]) for each in X_test.columns})
# # a.apply(lambda x : x['actual_label'])
# Feature_test = model(torch.from_numpy(X_test.values))
#
# Feature_test = pd.DataFrame(Feature_test.detach().numpy())
# Feature_test.index = y_test.index
# Feature_test['label'] = y_test
# corr = Feature_test.corr()
# corr_label = corr['label'].drop('label')
# corr_label.min()
#
#


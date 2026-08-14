# @Time : 2021/8/21 12:20
# @Author : Zhichen Lu
# @File : TorchNNEtractor.py


import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import torch
from tqdm import tqdm
from torch.utils.data import DataLoader,TensorDataset
import numpy as np
import copy
torch.set_default_tensor_type(torch.FloatTensor)

def ic(y_pred,y_true):
    return ((y_pred - y_pred.mean(dim=0)).transpose(0,1)*(y_true-y_true.mean())).mean(dim=1)/(y_pred.std(dim=0)*y_true.std())

def myloss(y_pred,y_true,inter_corr_eof=0):
    corr_loss = ic(y_pred, y_true)
    loss = 1 - (corr_loss).mean()
    return loss,corr_loss

class NNExtractor(torch.nn.Module):

    def __init__(self,dim,net_arch=[200,100,1],dropout_ratio=0.3):
        super().__init__()

        net = (torch.nn.Linear(dim, net_arch[0]), torch.nn.Dropout(p=dropout_ratio), torch.nn.ReLU())
        pre_dim = net_arch[0]
        for temp_dim in net_arch[1:]:
            net += (torch.nn.Linear(pre_dim, temp_dim), torch.nn.Dropout(p=dropout_ratio), torch.nn.LogSigmoid(),)
            pre_dim = temp_dim
        net = net[:-1] + (torch.nn.Tanh(),)


        self.last_hidden = torch.nn.Sequential(*net[:-3])
        self.output = torch.nn.Sequential(*net[-3:])
        self.last_hidden.float()
        self.output.float()

    def forward(self,input):
        x = self.last_hidden(input)
        x = self.output(x)
        return x

class TrainWrapper:
    def __init__(self,net_arch,opt=torch.optim.SGD,dropout_ratio=None):

        self.net_arch =net_arch
        self.train_log = []
        self.val_log = []
        self.opter = opt
        self.model = None
        self.dropout_ratio = dropout_ratio

    def reinitial(self,dim):
        model = NNExtractor(dim,self.net_arch,self.dropout_ratio)
        self.model = model

    def predict(self,X):
        if isinstance(X,np.ndarray):
            return self.model(torch.from_numpy(X).float())
        elif isinstance(X,pd.DataFrame):
            return self.model(torch.from_numpy(X.values).float())
        elif isinstance(X,torch.Tensor):
            return self.model(X).item()
        else:
            raise Exception('Wrong input Type')

    def train(self,X,y,val_split=0.1,batch_size=2**12,learning_rate=0.1,early_stop_round=None,max_epoch=100,decay_ratio=0.6,decay_round=5):
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
            loss_eval,corr_loss_eval, =np.nan,np.nan
            for batch in bar:
                bar.set_description(f'loss:{loss_eval:.4f}  corr:{corr_loss_eval:.4f}')
                inputs,labels = batch
                pred = self.model(inputs)

                loss,corr_loss = myloss(pred,labels)
                loss_eval, corr_loss_eval = loss.item(), abs(corr_loss).mean().item()
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                iteration+=1

                if iteration%10==0:
                    val_pred = self.model(X_val)
                    val_loss, val_corr_loss = myloss(val_pred,y_val)
                    val_loss, val_corr_loss = val_loss.item(), abs(val_corr_loss).mean().item()
                    self.train_log.append([loss_eval,corr_loss_eval ])
                    self.val_log.append([val_loss, val_corr_loss])
                    print(f'tain_total_loss {loss_eval:.4f} train_corr:{corr_loss_eval:.4f} ||',
                          f'val_total_loss {val_loss:.4f} val_corr:{val_corr_loss:.4f} ')
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

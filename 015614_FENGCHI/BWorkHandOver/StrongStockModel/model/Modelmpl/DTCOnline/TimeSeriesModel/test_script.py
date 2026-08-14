# @Time : 2022/4/27 16:16
# @Author : Zhichen Lu
# @File : test_script.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading/StockSelection', '/data/user/015664/TriggeredTrading'])

import pandas as pd
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
from dataApi.tradeDate import get_date_range
import numpy as np
import torch,gc,os
from torch.autograd import Variable
from torch.nn import utils as nn_utils
from torch.utils.data import DataLoader,TensorDataset
from torch import optim
from tqdm import tqdm
from StrongStockModel.conf.path_config import root_path
from torch.optim.lr_scheduler import ReduceLROnPlateau
from dataApi.sendInfo import send_message

SEED = 0
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
np.random.seed(SEED)

class LSTMModel(torch.nn.Module):
    def __init__(self,input_dim,hidden_dim,rec_layers,full_conn_dims,dropout):
        super().__init__()
        self.input_dim = input_dim
        self.hiddem_dim = hidden_dim
        # self.full_conn_dim = full_conn_dim
        self.lstm = torch.nn.LSTM(input_size=input_dim,hidden_size=hidden_dim,num_layers=rec_layers,batch_first=True)
        i_o_list = list(zip([hidden_dim]+full_conn_dims,full_conn_dims+[1],dropout))
        self.full_conn = []
        for i,o,d_ratio in i_o_list:
            if self.full_conn:
                self.full_conn.append(torch.nn.ReLU())
            self.full_conn.append(torch.nn.Linear(i,o))
            if d_ratio>0:
                self.full_conn.append(torch.nn.Dropout(d_ratio))
        self.full_conn.append(torch.nn.Tanh())
        if torch.cuda.is_available():
            self.lstm = self.lstm.cuda()
            self.full_conn = [x.cuda() for x in self.full_conn]

    def forward(self,batch):

        output,hn = self.lstm(batch)
        output = self.full_conn[0](output[:,-1,:])
        for layer in self.full_conn[1:]:
            output = layer(output)
        return output*0.2

def corr(x,y):
    return ((x*y).mean() - x.mean()*y.mean())/(x.std()*y.std())

def loss_fn(x,y,corr_eof=1,coef_m=0.5):
    diff = x-y
    m_loss = (diff**2).mean()
    mstd_loss = diff.std()
    c_loss = corr(x,y)
    return 1+coef_m*mstd_loss - corr_eof*c_loss,m_loss,c_loss,mstd_loss


def load_dataset(start,end,split_date):
    date_list = get_date_range(start, end)
    eval_indicator = pd.read_pickle(f'{root_path}external_data/moon_v2/ic_dt.pkl')
    target_date = list(filter(lambda x : x<date_list[-1],eval_indicator.index.tolist()))
    target_date = max(target_date)
    fix_factor_list = eval_indicator.loc[target_date].apply(abs).sort_values(ascending=False).index.tolist()[:100]

    X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=date_list[0], end_date=date_list[-1],
                                                                factor_list=fix_factor_list, model_time_len=7)
    X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time, model_time_len=7)
    X_train, y_train, idx_date_train, idx_code_train, idx_time_train = [x[idx_date[:, -1] < split_date] for x in [X, y, idx_date, idx_code, idx_time]]
    X_test, y_test, idx_date_test, idx_code_test, idx_time_test = [x[idx_date[:, -1] >= split_date] for x in [X, y, idx_date, idx_code, idx_time]]
    pd.to_pickle([X_train, y_train, idx_date_train, idx_code_train, idx_time_train],f'{base_dir}train_set.pkl')
    pd.to_pickle([X_test, y_test, idx_date_test, idx_code_test, idx_time_test],f'{base_dir}test_set.pkl')

# load_dataset(20170501,20171231,20171001)
def train_LSTM(hidden_dim,rec_layers,full_conn_dims,dropout):
    # hidden_dim, rec_layers, full_conn_dims, dropout = 20,2,[20,10,1],[0.3,0.2,0.1]
    tag = f'Param{hidden_dim, rec_layers, full_conn_dims, dropout}'
    print(tag)
    out_dir = f'{base_dir}/ParamSeeking/'
    model_dir = f'{base_dir}/ModelConf/'
    if os.path.exists(f'{out_dir}/{tag}.pkl'):
        return
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    lstm = LSTMModel(100,hidden_dim, rec_layers, full_conn_dims, dropout)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    lstm = lstm.to(device)

    batch_size = 2**15
    val_ratio = 0.2
    epoch = 100
    early_stop = 15
    decay_ep = 5
    decay_ratio = 0.8
    ini_lr = 0.1

    lr = ini_lr
    optmizer = optim.SGD(lstm.parameters(), lr=lr, momentum=0.9)
    X_train, y_train, idx_date_train, idx_code_train, idx_time_train = pd.read_pickle(f'{base_dir}train_set.pkl')
    X_train, y_train = torch.from_numpy(X_train), torch.from_numpy(y_train)
    val_sample = int(X_train.shape[0]*val_ratio)
    train_set = TensorDataset(X_train[:-val_sample], y_train[:-val_sample])
    DLoader = DataLoader(train_set,batch_size=batch_size,shuffle=True,num_workers=0)
    ValLoader = DataLoader(TensorDataset(X_train[-val_sample:], y_train[-val_sample:]), batch_size=batch_size, shuffle=False,num_workers=0)
    losses = []
    current_min = 10
    noBetterEpo = 0
    check_point_file = f'{model_dir}/{tag}.pkl'

    if not os.path.exists(os.path.split(check_point_file)[0]):
        os.makedirs(os.path.split(check_point_file)[0])

    scheduler = ReduceLROnPlateau(optmizer,factor=decay_ratio,patience=decay_ep,min_lr=0.005)
    for idx in range(epoch):
        bar = tqdm(DLoader,desc=f'epoch {idx}/{epoch}')
        for batch,label in bar:
            batch,label = batch.to(device),label.to(device)
            optmizer.zero_grad()
            out = lstm(batch)
            loss,_,_,_ = loss_fn(out[:,0],label)
            loss.backward()
            optmizer.step()
        torch.cuda.empty_cache()
        with torch.no_grad():
            val_out,val_label = [],[]
            for v_batch,v_label in tqdm(ValLoader):
                v_batch = v_batch.to(device)
                val_out_temp = lstm(v_batch)
                val_out.append(val_out_temp.cpu())
                val_label.append(v_label.cpu())
            val_out,val_label = torch.cat(val_out,0),torch.cat(val_label,0)
            val_loss,val_m,val_c,val_mstd = loss_fn(val_out[:,0].cpu(),val_label.cpu())
            val_loss,val_m,val_c,val_mstd = [x.cpu().detach().numpy() for x in [val_loss,val_m,val_c,val_mstd]]
            scheduler.step(val_loss)
            bar.set_description(f'epoch {idx}/{epoch}  val_loss:{val_loss:.5f} val_mse:{val_m:.5f} val_corr:{val_c:.5f} val_mstd:{val_mstd:.5f} lr{optmizer.param_groups[0]["lr"]:.3f}')
            print(f'epoch {idx}/{epoch}  val_loss:{val_loss:.5f} val_mse:{val_m:.5f} val_corr:{val_c:.5f} val_mstd:{val_mstd:.5f} lr{optmizer.param_groups[0]["lr"]:.3f}')
        losses.append([val_loss,val_m,val_c,val_mstd ])
        if val_loss<current_min:
            current_min = val_loss
            noBetterEpo = 0
            torch.save(lstm,check_point_file)
        else:
            noBetterEpo+=1
        if noBetterEpo>=early_stop:
            lstm = torch.load(check_point_file)
            break
    X_test, y_test, idx_date_test, idx_code_test, idx_time_test = pd.read_pickle( f'{base_dir}test_set.pkl')
    X_test, y_test = torch.from_numpy(X_test), torch.from_numpy(y_test)
    TLoader = DataLoader(TensorDataset(X_test,y_test), batch_size=batch_size,shuffle=False, num_workers=0)
    lstm = lstm.to(device)
    actual_label,pred = [],[]
    for batch,label in TLoader:
        batch,label = batch.to(device),label.to(device)
        temp_out = lstm(batch)
        actual_label.append(label.cpu().detach().numpy())
        pred.append(temp_out.cpu().detach().numpy()[:,0])
    torch.cuda.empty_cache()
    actual_label = np.concatenate(actual_label)
    pred = np.concatenate(pred)
    loss,mse,cor,mstd = loss_fn(actual_label,pred)
    res = {
        'loss':loss,'mse':mse,'corr':cor,'diff_sstd':mstd,
        'loss_log':losses
    }
    pd.to_pickle(res,f'{out_dir}/{tag}.pkl')
    info_res = {x:res[x] for x in [ 'loss','mse','corr','diff_sstd']}
    import datetime
    if datetime.datetime.now()<datetime.datetime(2022, 5, 9, 10, 37, 10, 477774):
        send_message(['015664'],f"{tag} \n {info_res}")

base_dir = '/data/user/015664/ModelFile/lstm_fixFIXSEED/'
import argparse
import itertools

# hidden_dims = [20, 40, 60,80,120,160,200]
# layers = [2, 3,4,5]
# structures = [
#     [20, 10, 1],
#     [32, 16, 1],
#     [64, 1],
#     [64, 32, 1],
#     [128, 64, 1],
#     [256, 128, 1],
#     [256, 128,64, 1],
# ]
# dropouts = [[0.3, 0.2, 0.1]]
# para_list = list(itertools.product(hidden_dims, layers, structures, dropouts))
# len(para_list)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p',type=str)
    args = parser.parse_args()
    train_LSTM(*eval(args.p))

    # for p in param_list[::-1]:
    #     train_LSTM(*p)







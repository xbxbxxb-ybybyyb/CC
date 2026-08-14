# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys
import os, gc, time, datetime


sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')

from dataApi.FixFactorRollPrepare import load_fix_data_selfdefined_label, feature_engineering
import numpy as np
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date
import pandas as pd
import xgboost as xgb
from StrongStockModel.model.ModelBase.ModelNonFixWindow import ModelNonFixWindow
from StrongStockModel.conf.path_config import root_path
from dataApi.tradeDate import get_date_range
from tqdm import tqdm
import torch,gc,os
from torch.autograd import Variable
from torch.nn import utils as nn_utils
from torch.utils.data import DataLoader,TensorDataset
from torch import optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

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




class LSTMTrainer(ModelNonFixWindow):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None,label_path=None,future_bar_num=None):
        super().__init__(start, end, stock_pool, feature_address, label_path=label_path, future_bar_num=future_bar_num)

        if label_path is None or future_bar_num is None:
            self.label_path = None
        else:
            self.label_path = f'{label_path}/future_{future_bar_num}_bar.npy'
        self.future_bar_num = future_bar_num

        self.using_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_local_path/available_factor_list.pkl')
        import shutil
        self.eval_indicator = factor_eval_indicator
        self.feature_address = feature_address
        self.date_list = get_date_range(start, end)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        model_time_len = 7
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time, y_1day_train = load_fix_data_selfdefined_label(train_idx[0],
                                        get_pre_trade_date(train_idx[-1]),fix_factor_list,address=self.feature_address,
                                    label_path=self.label_path,return_1day_label=True,model_time_len=model_time_len)
        else:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time, y_1day_train = load_fix_data_selfdefined_label(train_idx[0], train_idx[-1],
                                         fix_factor_list,address=self.feature_address,label_path=self.label_path,return_1day_label=True,model_time_len=model_time_len)

        train_feature, train_label, train_idx_date, train_idx_time, train_idx_code, y_1day_train = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                    train_idx_time, train_idx_code, y_1day_train,model_time_len=model_time_len)

        index_train = pd.MultiIndex.from_tuples(list(zip(train_idx_date[:,-1].tolist(), train_idx_time[:,-1].tolist(), train_idx_code[:,-1].tolist())))
        train_label = pd.DataFrame({'actual_label': train_label, '1_day_label': y_1day_train[:,-1]}, index=index_train)
        train_feature = [train_feature,train_idx_date[:,-1], train_idx_time[:,-1], train_idx_code[:,-1]]
        today = get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            test_feature, test_label = pd.DataFrame(columns=fix_factor_list), pd.DataFrame(columns=fix_factor_list)
        else:
            if test_idx[-1] > today:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time, y_1day = load_fix_data_selfdefined_label(start_date=test_idx[0],
                                       end_date=today,factor_list=fix_factor_list,return_idx=True,
                                address=self.feature_address,label_path=self.label_path,return_1day_label=True,model_time_len=model_time_len)
            else:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time, y_1day = load_fix_data_selfdefined_label(start_date=test_idx[0],
                                   end_date=test_idx[-1],factor_list=fix_factor_list,
                                    return_idx=True,address=self.feature_address,label_path=self.label_path,return_1day_label=True,model_time_len=model_time_len)

            if today <= test_idx[-1]:
                test_label[np.isnan(test_label) & (test_idx_date == today)] = 0
                test_nolimit[(test_label == 0) & (test_idx_date == today)] = True
                print('-----------new update-----------')
            test_feature, test_label, test_idx_date, test_idx_time, test_idx_code, y_1day = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
                                                         test_idx_time, test_idx_code, y_1day,model_time_len=model_time_len)

            index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date[:,-1].tolist(),
                                                            test_idx_time[:,-1].tolist(), test_idx_code[:,-1].tolist())))

            test_label = pd.DataFrame({'actual_label': test_label, '1_day_label': y_1day[:,-1]}, index=index_test)
            test_feature = [test_feature, test_idx_date[:,-1], test_idx_time[:,-1], test_idx_code[:,-1]]
        return train_feature, train_label, test_feature, test_label, time.time() - e
    def get_fix_factor_evaluation(self, num, end_index):

        restrict_path = '/data/group/800442/800319/junkData/StrongStock//external_data/problem_factor/'
        file_list = sorted(list(filter(lambda x: x <= f'{end_index}.pkl', os.listdir(restrict_path))))
        if file_list:
            unavailable_factor = pd.read_pickle(f'{restrict_path}{file_list[-1]}')
        else:
            unavailable_factor = []
        print(f'unavailable {unavailable_factor}')

        factor_evaluation = pd.read_pickle(f'{root_path}external_data/FutureBarBy30Min_8bar/Future_{self.future_bar_num}_bar/{self.eval_indicator}.pkl')
        print(f'{root_path}external_data/FutureBarBy30Min_8bar/Future_{self.future_bar_num}_bar/{self.eval_indicator}.pkl')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(self.using_factor_list))-set(unavailable_factor))
        factor_evaluation = factor_evaluation[inter_col]
        target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index.tolist())))
        print(f'target eval date {target_date}')
        if 'ret' in self.eval_indicator:
            print('ret')
            factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
        elif 'ic' in self.eval_indicator:
            print('ic')
            factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
        else:
            raise Exception('')
        factor_list = factor_evaluation.index.tolist()[:num]
        return sorted(factor_list)

    def predict(self, model, X_test, end_date=None):
        X_test, idx_date_test, idx_time_test, idx_code_test = X_test
        X_test = torch.from_numpy(X_test)
        X_test = X_test.to(self.device)
        out = model(X_test)
        pred_label = pd.Series(out.cpu().detach().numpy()[:,0],
                               pd.MultiIndex.from_tuples(list(zip(idx_date_test, idx_time_test, idx_code_test))))
        return pred_label

    def train_model(self, train_feature, train_label, params, end_date=None):
        batch_size = 2 ** 15
        val_ratio = 0.2
        epoch = 200
        early_stop = 15
        decay_ep = 5
        decay_ratio = 0.8
        ini_lr = 0.1

        date_list = get_date_range(train_label.index[0][0], end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]
        is_left = np.isin(train_feature[1], np.array(val_date))
        X_left, idx_date_left, idx_time_left, idx_code_left, y_left = [x[is_left] for x in train_feature + [train_label['actual_label'].values]]
        LeftLoader = DataLoader(TensorDataset(torch.from_numpy(X_left), torch.from_numpy(y_left)),
                                batch_size=batch_size, shuffle=False, num_workers=0)
        # factor_list = X_train.columns.tolist()
        # pd.to_pickle(factor_list, params['feature_path'] + '%d.pkl' % end_date)
        hidden_dim, rec_layers, full_conn_dims, dropout = params['net_conf']
        model_dir = params['model_conf_path']
        if os.path.exists(f'{model_dir}{end_date}.pkl'):
            lstm = torch.load(f'{model_dir}{end_date}.pkl')
            lstm.to(self.device)
        else:
            X_train, idx_date_train, idx_time_train, idx_code_train, y_train = [x[~is_left] for x in train_feature + [train_label['actual_label'].values]]
            X_train, y_train = torch.from_numpy(X_train), torch.from_numpy(y_train)
            val_sample = int(X_train.shape[0] * val_ratio)
            train_set = TensorDataset(X_train[:-val_sample], y_train[:-val_sample])
            DLoader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=0)
            ValLoader = DataLoader(TensorDataset(X_train[-val_sample:], y_train[-val_sample:]), batch_size=batch_size, shuffle=False, num_workers=0)

            lstm = LSTMModel(X_train.shape[-1], hidden_dim, rec_layers, full_conn_dims, dropout)
            lstm = lstm.to(self.device)
            lr = ini_lr
            optmizer = optim.SGD(lstm.parameters(), lr=lr, momentum=0.9)
            # X_train, idx_date_train, idx_time_train, idx_code_train = train_feature
            losses = []
            current_min = 10
            noBetterEpo = 0
            check_point_file = f'{model_dir}/checkpoint/{end_date}.pkl'
            if not os.path.exists(os.path.split(check_point_file)[0]):
                os.makedirs(os.path.split(check_point_file)[0])
            scheduler = ReduceLROnPlateau(optmizer, factor=decay_ratio, patience=decay_ep, min_lr=0.005)
            for idx in range(epoch):
                bar = tqdm(DLoader, desc=f'epoch {idx}/{epoch}')
                for batch, label in bar:
                    batch, label = batch.to(self.device), label.to(self.device)
                    optmizer.zero_grad()
                    out = lstm(batch)
                    loss, _, _, _ = loss_fn(out[:, 0], label)
                    loss.backward()
                    optmizer.step()
                torch.cuda.empty_cache()
                with torch.no_grad():
                    val_out, val_label = [], []
                    for v_batch, v_label in tqdm(ValLoader):
                        v_batch = v_batch.to(self.device)
                        val_out_temp = lstm(v_batch)
                        val_out.append(val_out_temp.cpu())
                        val_label.append(v_label.cpu())
                    val_out, val_label = torch.cat(val_out, 0), torch.cat(val_label, 0)
                    val_loss, val_m, val_c, val_mstd = loss_fn(val_out[:, 0].cpu(), val_label.cpu())
                    val_loss, val_m, val_c, val_mstd = [x.cpu().detach().numpy() for x in [val_loss, val_m, val_c, val_mstd]]
                    scheduler.step(val_loss)
                    bar.set_description(
                        f'epoch {idx}/{epoch}  val_loss:{val_loss:.5f} val_mse:{val_m:.5f} val_corr:{val_c:.5f} val_mstd:{val_mstd:.5f} lr{optmizer.param_groups[0]["lr"]:.3f}')
                    print(f'epoch {idx}/{epoch}  val_loss:{val_loss:.5f} val_mse:{val_m:.5f} val_corr:{val_c:.5f} val_mstd:{val_mstd:.5f} lr{optmizer.param_groups[0]["lr"]:.3f}')
                losses.append([val_loss, val_m, val_c, val_mstd])
                if val_loss < current_min:
                    current_min = val_loss
                    noBetterEpo = 0
                    torch.save(lstm, check_point_file)
                else:
                    noBetterEpo += 1
                if noBetterEpo >= early_stop:
                    lstm = torch.load(check_point_file)
                    break
            torch.save(lstm,f'{model_dir}{end_date}.pkl')
            if not os.path.exists(f'{model_dir}/losslog/'):
                os.makedirs(f'{model_dir}/losslog/')
            pd.to_pickle(losses,f'{model_dir}/losslog/{end_date}.pkl')
        torch.cuda.empty_cache()
        if not os.path.exists(params['val_pred_path']):
            os.mkdir(params['val_pred_path'])
        left_pred,left_actual = [],[]
        for batch,label in LeftLoader:
            batch,label = batch.to(self.device),label.to(self.device)
            out = lstm(batch)
            left_pred.append(out.cpu().detach().numpy()[:,0])
            left_actual.append(label.cpu().detach().numpy())
        torch.cuda.empty_cache()
        left_actual,left_pred = np.concatenate(left_actual),np.concatenate(left_pred)
        left = pd.DataFrame({
            'actual_label':left_actual,
            'prediction':left_pred},
        index = pd.MultiIndex.from_tuples(list(zip(idx_date_left,idx_time_left,idx_code_left))))
        pd.to_pickle(left,params['val_pred_path']+f'{end_date}.pkl')
        return lstm

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None

        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])

            if os.path.exists(params['feature_path'] + '%d.pkl' % train_end_idx):
                fix_factor_list = pd.read_pickle(params['feature_path'] + '%d.pkl' % train_end_idx)
                X_train, y_train, X_test, y_test, feature_engineering_time = \
                    self.get_dataset((get_pre_trade_date(train_end_idx,12), train_end_idx), (test_start_idx, test_end_idx),
                                     fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            else:
                fix_factor_list = self.get_fix_factor_evaluation(factor_nums, train_end_idx)
                X_train, y_train, X_test, y_test, feature_engineering_time = \
                    self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                     fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            gc.collect()
            training_sample = X_train[0].shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()

            if len(X_train[0]) > 2000:
                print('re-train in this round')
                model = self.train_model(X_train, y_train, params, train_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test[0]) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test, train_end_idx)
                # y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label


from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i, indicator,future_bar_num,label_path):
    train_period = 100
    test_period = 10
    factor_num = 100
    targe_file = 'LSTM_%s_train%d_test%d_factor_num%d' % (indicator, train_period, test_period, factor_num)
    out_file = f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/TimeSeriesModel/{targe_file}/{targe_file}.pkl'
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    train_start = get_pre_trade_date(train_end,99)
    # test_end = 20220317
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(out_file, 'exist')
        # os.remove(base_dir + '%d.pkl' % train_end)
        return
    print(out_file)

    best_param_clf_xgb = {'net_conf':(20, 5, [128, 64, 1], [0.3, 0.2, 0.1])}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')
    model = LSTMTrainer(train_start, test_end, None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num,label_path=label_path,future_bar_num=future_bar_num)
    if not os.path.exists(best_param_clf_xgb['model_conf_path']):
        os.mkdir(best_param_clf_xgb['model_conf_path'])
    if not os.path.exists(best_param_clf_xgb['feature_path']):
        os.mkdir(best_param_clf_xgb['feature_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)


idx_list = list(range(147))[20:-2][::-1]

for i in tqdm(idx_list):
    for f_bar in tqdm(list(range(8, 9))):
        for ind_name in ['ic_dt']:
            main_window_search(i, ind_name,f_bar,label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/')
            gc.collect()


# idx_list = list(range(134))[24:]#[::-1]
# idx_list = list(range(134,152))[::-1]
# for f_bar in tqdm(list(range(1,9))[::-1]):
#     for i in tqdm(idx_list):
#         for ind_name in ['ic_d','ic_t','ic_c']:
#             main_window_search(i, ind_name,f_bar,label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/')
#             gc.collect()
# send_message(['015664'],'XGB done')
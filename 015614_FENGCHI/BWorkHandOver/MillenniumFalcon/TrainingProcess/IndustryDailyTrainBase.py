# @Time : 2021/10/13 14:40
# @Author : Zhichen Lu
# @File : IndustryDailyTrainBase.py
import pandas as pd
import numpy as np
import os
from abc import abstractmethod
from dataApi.tradeDate import get_date_range


def get_split_period_info(date_list, train_period, test_period):
    test_end = date_list[train_period + test_period - 1::test_period]
    test_start = [date_list[date_list.index(x) - test_period + 1] for x in test_end]
    train_end = [date_list[date_list.index(x) - 1] for x in test_start]
    train_start = [date_list[date_list.index(x) - train_period + 1] for x in train_end]

    if test_end[-1] != date_list[-1]:
        train_end.append(test_end[-1])
        train_start.append(date_list[date_list.index(train_end[-1]) - train_period + 1])
        test_start.append(date_list[date_list.index(train_end[-1]) + 1])
        test_end.append(date_list[-1])

    period_info = list(zip(train_start, train_end, test_start, test_end))
    return period_info


def load_daily_factor(factor_list, future_type, start, end, address):
    base_address = os.path.split(os.path.abspath(address))[0]
    label_address = f'{base_address}/label_arr/'
    idx_date = np.load(f'{address}idx_date.npy')
    idx_code = np.load(f'{address}idx_code.npy')

    starts = (idx_date < start).sum()
    shape = (idx_date <= end).sum() - starts

    idx_date = idx_date[starts:][:shape]
    idx_code = idx_code[starts:][:shape]

    X = np.empty((len(factor_list), shape),dtype=np.float32)
    y = np.empty((shape,),dtype=np.float32)

    y[:] = np.memmap(f'{label_address}{future_type}.npy', dtype='float32', mode='r', shape=(shape,), offset=starts * 4 + 128)[:]
    for idx, f_name in enumerate(factor_list):
        fac = np.memmap(f'{address}{f_name}.npy', dtype='float32', mode='r', shape=(shape,), offset=starts * 4 + 128)
        X[idx] = fac[:]
        del fac

    return X,y,idx_date,idx_code

def feature_engineering(X,y,idx_date,idx_code,nan_limit=0.2,extra_confition=None):
    isfinit = np.isfinite(X)
    available = np.isfinite(y) & (((~isfinit).sum(axis=0)/isfinit.shape[0])<nan_limit)
    if not extra_confition is None:
        available = available&extra_confition
    X[~isfinit] = 0
    print(f'feature engineering: {available.sum()}/{available.shape[0]}  {round(available.sum()/available.shape[0],6)*100}%')
    return X[:,available],y[available],idx_date[available],idx_code[available]

def spllit_val_date(X,y,idx_date,idx_code,val_date_list):
    val_tag = np.isin(idx_date,val_date_list)
    X_train,y_train,X_val,y_val = X[~val_tag],y[~val_tag],X[val_tag],y[val_tag]
    idx_date_train,idx_code_train,idx_date_val,idx_code_val = idx_date[~val_tag],idx_code[~val_tag],idx_date[val_tag],idx_code[val_tag]
    return X_train,y_train,idx_date_train,idx_code_train,X_val,y_val,idx_date_val,idx_code_val

class IndustryDailyTrainBase(object):

    def __init__(self,factor_address,label_type,out_base_path,val_idx=list([-1*x for x in range(3,43,2)])):
        self.factor_address = factor_address
        self.label_type = label_type
        self.out_base_path = out_base_path
        self.val_idx = val_idx
        self.model_path = os.path.join(out_base_path,'model_conf')
        self.res_path = os.path.join(out_base_path,'res')
        self.val_path = os.path.join(out_base_path,'val')

        for each in [self.model_path,self.res_path,self.val_path]:
            if not os.path.exists(each):
                os.makedirs(each)

    @abstractmethod
    def train_model(self, start, end, param={}):
        pass

    @abstractmethod
    def pred_by_model(self,model,start,end,param={}):
        pass

    def load_dataset(self, factor_list, date_list):
        date_list.sort()
        feature,label,idx_date,idx_code = load_daily_factor(factor_list, start=date_list[0], end=date_list[-1], address=self.factor_address,future_type=self.label_type)
        isin_condition = np.isin(idx_date,date_list)
        feature, label, idx_date, idx_code = feature_engineering(feature,label,idx_date,idx_code,extra_confition=isin_condition)
        index = pd.MultiIndex.from_tuples(list(zip(list(idx_date),list(idx_code))))
        feature = pd.DataFrame(feature.T,index=index,columns=factor_list)
        label = pd.DataFrame({'actual_label':label},index=index)
        return feature, label

    def train_by_period_info(self,period_info,param={}):
        train_start,train_end,test_start,test_end = period_info
        model = self.train_model(train_start,train_end,param)
        label = self.pred_by_model(model,test_start,test_end)
        pd.to_pickle(label, f'{self.res_path}/{train_end}.pkl')
        return label

    def load_train_set(self,factor_list,start,end):
        date_list = get_date_range(start,end)
        val_date_list = [date_list[x] for x in self.val_idx]
        train_date_list = sorted(list(set(date_list)-set(val_date_list)))[:-1]
        train_feature, train_label = self.load_dataset(factor_list,train_date_list)
        val_feature,val_label = self.load_dataset(factor_list,val_date_list)
        return train_feature,train_label,val_feature,val_label


import pandas as pd
import numpy as np
import xgboost as xgb

class XGBInd(IndustryDailyTrainBase):

    def __init__(self,factor_address,label_type,out_base_path,eval_indicator_file,factor_num,val_idx=list([-1*x for x in range(3,43,2)])):
        super().__init__(factor_address,label_type,out_base_path,val_idx)
        self.factor_list = None
        self.eval_indicator = pd.read_pickle(eval_indicator_file)
        self.factor_num = factor_num

    def update_factor_list(self,date):
        target_date = list(filter(lambda x : x<date,self.eval_indicator.index.tolist()))
        if target_date:
            target_date = max(target_date)
        else:
            raise Exception('No available eval res')
        factor_list = self.eval_indicator.loc[target_date].apply(abs).sort_values(ascending=False).index.tolist()[:self.factor_num]
        self.factor_list = sorted([x.replace('.pkl','') for x in factor_list])

    def train_model(self, start, end, param={}):
        self.update_factor_list(end)
        key_list = set(param.keys()).intersection(
            set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
        args_param = {x: param[x] for x in key_list}

        train_feature,train_label,val_feature,val_label = self.load_train_set(self.factor_list,start,end)
        d_val = xgb.DMatrix(val_feature,label=val_label['actual_label'])

        if os.path.exists(f'{self.model_path}{end}.json'):
            model = xgb.Booster(model_file=f'{self.model_path}{end}.json')
        else:
            d_train = xgb.DMatrix(train_feature, label=train_label['actual_label'])
            model = xgb.train(args_param, d_train,num_boost_round=param['n_estimators'],evals=[(d_val,'eval')],early_stopping_rounds=15,verbose_eval=False)
        model.set_param('predictor','cpu_predictor')

        val_label['prediction'] = model.predict(d_val)
        pd.to_pickle(val_label,f'{self.val_path}/{end}.pkl')
        return model

    def pred_by_model(self, model, start, end, param={}):
        date_list = get_date_range(start, end)
        test_feature,test_label = self.load_dataset(self.factor_list,date_list)
        d_test = xgb.DMatrix(test_feature)
        test_label['prediction'] = model.predict(d_test)
        return test_label


period_info_list =get_split_period_info(get_date_range(20141001,20210531),300,5)



def one_wave_run(indicator,source_path,out_base,label_type,preprocess_type):
    base_path = f'{out_base}/XGB_{indicator}_{preprocess_type}_{label_type}/'
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    xgb_trainer = XGBInd(factor_address=f'{source_path}{preprocess_type}_arr/',
                         label_type=label_type,
                         out_base_path=base_path,
                         eval_indicator_file=f'{source_path}eval_res_integration/{preprocess_type}_{label_type}/{indicator}.pkl',
                         factor_num=400)

    model_param = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                              'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                              'subsample': 0.8, 'tree_method': 'gpu_hist'}
    from tqdm import tqdm
    for period in tqdm(period_info_list):
        if os.path.exists(f'{xgb_trainer.res_path}/{period[1]}.pkl'):
            continue
        xgb_trainer.train_by_period_info(period,param=model_param)



    file_list = sorted(os.listdir(f'{base_path}res/'))

    corr_series = {}
    mae_series = {}
    all_res = []

    for period in file_list:
        temp_res = pd.read_pickle(f'{base_path}res/{period}')
        corr_series[int(period[:-4])] = temp_res.corr().values[0,1]
        mae_series[int(period[:-4])] = abs(temp_res['actual_label']-temp_res['prediction']).mean()
        all_res.append(temp_res)

    all_res = pd.concat(all_res)
    daily_ic = all_res.groupby(level=0).apply(lambda x: x.corr().values[0, 1])
    print('daily ic:',daily_ic.mean())
    stat = pd.DataFrame({'corr':corr_series,'mae':mae_series})
    print(indicator,label_type,all_res.corr())
    print(stat.mean())
    print(abs(all_res['actual_label'] - all_res['prediction']).mean())

    eval_res_path = f'{out_base}/eval_res/'
    for each in ['daily_ic','periodically_eval','data']:
        if not os.path.exists(f'{eval_res_path}{each}/'):
            os.makedirs(f'{eval_res_path}{each}/')

    pd.to_pickle(all_res,f'{eval_res_path}data/XGB_{indicator}_{preprocess_type}_{label_type}.pkl')
    pd.to_pickle(daily_ic,f'{eval_res_path}daily_ic/XGB_{indicator}_{preprocess_type}_{label_type}.pkl')
    pd.to_pickle(stat,f'{eval_res_path}periodically_eval/XGB_{indicator}_{preprocess_type}_{label_type}.pkl')
    # eval_res_path = f'{out_base}/result/eval/'

if __name__=='__main__':
    # ind_name = 'ic_c'
    s_path = '/data/group/800442/800319/HFfactor/DailySW2PreNormalized/'
    o_base = '/data/group/800442/800319/MillenniumFalcon/ExpResPreNormalize/'
    # b_path = '/data/group/800442/800319/HFfactor/DailySW2PreNormalized/'
    type_list = list(map(lambda x: x.replace('.pkl', ''), os.listdir(f'{s_path}label/')))
    # l_type = 'lable_group_stk_future_avg_1'
    # pre_type =
    for pre_type in ['zscore', 'mean','std']:
        for l_type in type_list:
            for ind_name in ['ic_c','ic_d','ic_dc']:
                one_wave_run(ind_name,source_path=s_path,out_base=o_base,label_type=l_type,preprocess_type=pre_type)
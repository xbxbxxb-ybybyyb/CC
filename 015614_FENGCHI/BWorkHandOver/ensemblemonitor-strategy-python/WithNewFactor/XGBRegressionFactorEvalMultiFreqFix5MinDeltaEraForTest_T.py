# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import xgboost as xgb
import os, gc, time
from tqdm import tqdm
from dataApi.tradeDate import get_date_range
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
from dataApi.diff_factor_concat import load_mix_data
from StrongStockModel.conf.path_config import root_path
import numpy as np
import configparser
import random
conf = configparser.ConfigParser()
conf.read('/data/group/800442//800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

best_param_clf_xgb = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607,
                          'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100, 'sampling_method': 'gradient_based',
                          'subsample': 0.8, 'tree_method': 'gpu_hist'}
using_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3_cp20210829/available_factor_list.pkl')
available_factor_list = list(map(lambda x: x.replace('.npy', ''), os.listdir('/arch1/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/')))
using_factor_list = sorted(list(set(using_factor_list).intersection(set(available_factor_list))))

# available_factor_5min_list = ['20201203143216179', '20201203145533987', '20201203145957210', '20201203152345492', '20201203153146336', '20201203153606687', '20201203153952494', '20201203154829323', '20201203155303833', '20201203155628630', '20201203155742578', '20201203155807597', '20201203160234999', '20201203161010619', '20201203161134565', '20201203161146895', '20201203162259733', '20201203163136590', '20201203163318573', '20201203163535149', '20201203184422862', '20201203193218297', '20201203193710397', '20201203194119676', '20201203195223567', '20201203200056715', '20201203200701345', '20201203210042750', '20201207191715374', '20201207193230615', '20201207215536291', '20201208124647506', '20201208161343280', '20201208174524370', '20201208224523503', '20201209064126224', '20201209104826801', '20201214135338364', '20201214140507553', '20201215144004966', '20201215144554337', '20201215144817432', '20201215153800784', '20201215205950489', '20201216091601933', '20201216091650406', '20201216092711480', '20201216104121892', '20201216113835933', '20201216125848480', '20201216143618891', '20201216150203933', '20201216190954508', '20201216215537182', '20201217032329526', '20201221213803526', '20201227063056377', 'fix5mins10207', 'fix5mins10349', 'fix5mins10879', 'fix5mins10983', 'fix5mins11086', 'fix5mins11147', 'fix5mins11203', 'fix5mins11288', 'fix5mins11389', 'fix5mins11441', 'fix5mins11533', 'fix5mins11539', 'fix5mins11575', 'fix5mins11713', 'fix5mins11746', 'fix5mins11943', 'fix5mins12027', 'fix5mins12033', 'fix5mins12078', 'fix5mins12093', 'fix5mins12155', 'fix5mins12159', 'fix5mins12213', 'fix5mins12616', 'fix5mins1277', 'fix5mins12907', 'fix5mins12968', 'fix5mins13097', 'fix5mins13159', 'fix5mins13210', 'fix5mins13238', 'fix5mins13258', 'fix5mins13268', 'fix5mins13371', 'fix5mins13412', 'fix5mins13479', 'fix5mins13484', 'fix5mins13551', 'fix5mins13582', 'fix5mins13647', 'fix5mins13724', 'fix5mins13745', 'fix5mins13863', 'fix5mins13880', 'fix5mins13952', 'fix5mins14000', 'fix5mins14008', 'fix5mins14009', 'fix5mins14033', 'fix5mins14071', 'fix5mins14081', 'fix5mins14095', 'fix5mins14100', 'fix5mins14109', 'fix5mins14118', 'fix5mins14137', 'fix5mins14179', 'fix5mins14188', 'fix5mins14204', 'fix5mins14236', 'fix5mins14324', 'fix5mins14356', 'fix5mins14357', 'fix5mins14366', 'fix5mins14385', 'fix5mins14409', 'fix5mins14761', 'fix5mins1516', 'fix5mins1575', 'fix5mins15897', 'fix5mins16321', 'fix5mins17089', 'fix5mins17126', 'fix5mins17192', 'fix5mins17220', 'fix5mins17255', 'fix5mins17258', 'fix5mins17328', 'fix5mins17329', 'fix5mins17344', 'fix5mins17365', 'fix5mins17423', 'fix5mins17451', 'fix5mins17470', 'fix5mins17471', 'fix5mins17484', 'fix5mins17496', 'fix5mins17507', 'fix5mins17524', 'fix5mins17538', 'fix5mins17554', 'fix5mins17561', 'fix5mins17564', 'fix5mins17612', 'fix5mins17619', 'fix5mins17648', 'fix5mins17653', 'fix5mins17669', 'fix5mins17707', 'fix5mins1771', 'fix5mins17712', 'fix5mins17715', 'fix5mins17737', 'fix5mins17769', 'fix5mins17773', 'fix5mins17822', 'fix5mins17883', 'fix5mins17903', 'fix5mins17927', 'fix5mins17958', 'fix5mins17999', 'fix5mins18031', 'fix5mins18036', 'fix5mins18039', 'fix5mins18103', 'fix5mins18224', 'fix5mins18225', 'fix5mins18230', 'fix5mins18252', 'fix5mins18263', 'fix5mins18268', 'fix5mins18421', 'fix5mins18732', 'fix5mins18927', 'fix5mins19047', 'fix5mins19062', 'fix5mins19087', 'fix5mins1915', 'fix5mins19167', 'fix5mins1925', 'fix5mins19368', 'fix5mins19899', 'fix5mins19901', 'fix5mins20230', 'fix5mins2081', 'fix5mins21008', 'fix5mins21039', 'fix5mins21209', 'fix5mins2197', 'fix5mins22031', 'fix5mins22252', 'fix5mins22467', 'fix5mins22616', 'fix5mins22763', 'fix5mins23051', 'fix5mins2319', 'fix5mins23509', 'fix5mins23533', 'fix5mins23648', 'fix5mins23652', 'fix5mins23669', 'fix5mins23712', 'fix5mins23738', 'fix5mins23797', 'fix5mins23800', 'fix5mins23828', 'fix5mins23843', 'fix5mins23858', 'fix5mins23881', 'fix5mins23889', 'fix5mins23904', 'fix5mins23905', 'fix5mins23957', 'fix5mins23960', 'fix5mins23968', 'fix5mins23991', 'fix5mins24006', 'fix5mins24010', 'fix5mins24027', 'fix5mins24043', 'fix5mins24067', 'fix5mins24068', 'fix5mins24086', 'fix5mins24094', 'fix5mins24109', 'fix5mins24111', 'fix5mins24142', 'fix5mins24171', 'fix5mins24178', 'fix5mins24209', 'fix5mins24242', 'fix5mins245', 'fix5mins24560', 'fix5mins24663', 'fix5mins24810', 'fix5mins24911', 'fix5mins24955', 'fix5mins2973', 'fix5mins3075', 'fix5mins3123', 'fix5mins3244', 'fix5mins3950', 'fix5mins4415', 'fix5mins5048', 'fix5mins5068', 'fix5mins5175', 'fix5mins5203', 'fix5mins5249', 'fix5mins5250', 'fix5mins5623', 'fix5mins5696', 'fix5mins5707', 'fix5mins5738', 'fix5mins5782', 'fix5mins5820', 'fix5mins5862', 'fix5mins5887', 'fix5mins5923', 'fix5mins5937', 'fix5mins5942', 'fix5mins6026', 'fix5mins6030', 'fix5mins6087', 'fix5mins6099', 'fix5mins6116', 'fix5mins6123', 'fix5mins6141', 'fix5mins6156', 'fix5mins6172', 'fix5mins6191', 'fix5mins6193', 'fix5mins6209', 'fix5mins6213', 'fix5mins6219', 'fix5mins6220', 'fix5mins6226', 'fix5mins6242', 'fix5mins6251', 'fix5mins6880', 'fix5mins7096', 'fix5mins7120', 'fix5mins7190', 'fix5mins7773', 'fix5mins8277', 'fix5mins8389', 'fix5mins8503', 'fix5mins8576', 'fix5mins8676', 'fix5mins8697', 'fix5mins870', 'fix5mins8785', 'fix5mins8819', 'fix5mins8822', 'fix5mins8824', 'fix5mins8833', 'fix5mins8897', 'fix5mins8907', 'fix5mins8913', 'fix5mins8944', 'fix5mins9002', 'fix5mins9019', 'fix5mins9049', 'fix5mins9090', 'fix5mins9108', 'fix5mins9146', 'fix5mins9157', 'fix5mins9199', 'fix5mins9203', 'fix5mins9227', 'fix5mins9251', 'fix5mins9253', 'fix5mins9255', 'fix5mins9259', 'fix5mins9260', 'fix5mins9814']
# available_factor_5min_list = ['20201203143216179', '20201203145533987', '20201203145957210', '20201203152345492', '20201203153146336', '20201203153606687', '20201203153952494', '20201203154829323', '20201203155303833', '20201203155628630', '20201203155742578', '20201203155807597', '20201203160234999', '20201203161010619', '20201203161134565', '20201203161146895', '20201203162259733', '20201203163136590', '20201203163318573', '20201203163535149', '20201203184422862', '20201203193710397', '20201203195223567', '20201203200056715', '20201203200701345', '20201203210042750', '20201207191715374', '20201207193230615', '20201207215536291', '20201208124647506', '20201208161343280', '20201208174524370', '20201208224523503', '20201209064126224', '20201209104826801', '20201214135338364', '20201214140507553', '20201215144554337', '20201215144817432', '20201215153800784', '20201215205950489', '20201216091601933', '20201216091650406', '20201216092711480', '20201216104121892', '20201216125848480', '20201216143618891', '20201216150203933', '20201216190954508', '20201217032329526', '20201221213803526', '20201227063056377', 'fix5mins10207', 'fix5mins10349', 'fix5mins10879', 'fix5mins10983', 'fix5mins11086', 'fix5mins11147', 'fix5mins11203', 'fix5mins11288', 'fix5mins11389', 'fix5mins11441', 'fix5mins11533', 'fix5mins11539', 'fix5mins11575', 'fix5mins11713', 'fix5mins11746', 'fix5mins12027', 'fix5mins12033', 'fix5mins12078', 'fix5mins12093', 'fix5mins12155', 'fix5mins12159', 'fix5mins12213', 'fix5mins12616', 'fix5mins1277', 'fix5mins12907', 'fix5mins12968', 'fix5mins13097', 'fix5mins13159', 'fix5mins13210', 'fix5mins13238', 'fix5mins13258', 'fix5mins13268', 'fix5mins13371', 'fix5mins13412', 'fix5mins13479', 'fix5mins13484', 'fix5mins13551', 'fix5mins13582', 'fix5mins13647', 'fix5mins13724', 'fix5mins13745', 'fix5mins13863', 'fix5mins13880', 'fix5mins13952', 'fix5mins14000', 'fix5mins14008', 'fix5mins14009', 'fix5mins14033', 'fix5mins14071', 'fix5mins14081', 'fix5mins14095', 'fix5mins14100', 'fix5mins14109', 'fix5mins14118', 'fix5mins14137', 'fix5mins14179', 'fix5mins14188', 'fix5mins14204', 'fix5mins14236', 'fix5mins14324', 'fix5mins14356', 'fix5mins14357', 'fix5mins14366', 'fix5mins14385', 'fix5mins14409', 'fix5mins14761', 'fix5mins1516', 'fix5mins1575', 'fix5mins15897', 'fix5mins16321', 'fix5mins17089', 'fix5mins17126', 'fix5mins17192', 'fix5mins17220', 'fix5mins17255', 'fix5mins17258', 'fix5mins17328', 'fix5mins17329', 'fix5mins17344', 'fix5mins17365', 'fix5mins17423', 'fix5mins17451', 'fix5mins17470', 'fix5mins17471', 'fix5mins17484', 'fix5mins17496', 'fix5mins17507', 'fix5mins17524', 'fix5mins17538', 'fix5mins17554', 'fix5mins17564', 'fix5mins17612', 'fix5mins17619', 'fix5mins17653', 'fix5mins17669', 'fix5mins17707', 'fix5mins1771', 'fix5mins17712', 'fix5mins17715', 'fix5mins17737', 'fix5mins17769', 'fix5mins17773', 'fix5mins17822', 'fix5mins17883', 'fix5mins17903', 'fix5mins17927', 'fix5mins17958', 'fix5mins17999', 'fix5mins18031', 'fix5mins18036', 'fix5mins18039', 'fix5mins18103', 'fix5mins18224', 'fix5mins18225', 'fix5mins18230', 'fix5mins18263', 'fix5mins18268', 'fix5mins18421', 'fix5mins18732', 'fix5mins18927', 'fix5mins19047', 'fix5mins19062', 'fix5mins19087', 'fix5mins1915', 'fix5mins1925', 'fix5mins19368', 'fix5mins19899', 'fix5mins19901', 'fix5mins20230', 'fix5mins2081', 'fix5mins21008', 'fix5mins21039', 'fix5mins21209', 'fix5mins2197', 'fix5mins22031', 'fix5mins22252', 'fix5mins22467', 'fix5mins22616', 'fix5mins22763', 'fix5mins23051', 'fix5mins2319', 'fix5mins23509', 'fix5mins23533', 'fix5mins23648', 'fix5mins23669', 'fix5mins23712', 'fix5mins23738', 'fix5mins23797', 'fix5mins23800', 'fix5mins23828', 'fix5mins23843', 'fix5mins23858', 'fix5mins23881', 'fix5mins23889', 'fix5mins23904', 'fix5mins23905', 'fix5mins23957', 'fix5mins23960', 'fix5mins23968', 'fix5mins23991', 'fix5mins24010', 'fix5mins24027', 'fix5mins24043', 'fix5mins24067', 'fix5mins24068', 'fix5mins24086', 'fix5mins24094', 'fix5mins24109', 'fix5mins24111', 'fix5mins24142', 'fix5mins24171', 'fix5mins24178', 'fix5mins24209', 'fix5mins24242', 'fix5mins245', 'fix5mins24560', 'fix5mins24663', 'fix5mins24810', 'fix5mins24911', 'fix5mins24955', 'fix5mins2973', 'fix5mins3075', 'fix5mins3123', 'fix5mins3244', 'fix5mins3950', 'fix5mins4415', 'fix5mins5048', 'fix5mins5068', 'fix5mins5175', 'fix5mins5203', 'fix5mins5249', 'fix5mins5250', 'fix5mins5623', 'fix5mins5696', 'fix5mins5707', 'fix5mins5738', 'fix5mins5782', 'fix5mins5820', 'fix5mins5862', 'fix5mins5887', 'fix5mins5923', 'fix5mins5937', 'fix5mins5942', 'fix5mins6026', 'fix5mins6030', 'fix5mins6087', 'fix5mins6099', 'fix5mins6116', 'fix5mins6123', 'fix5mins6156', 'fix5mins6172', 'fix5mins6191', 'fix5mins6193', 'fix5mins6209', 'fix5mins6213', 'fix5mins6219', 'fix5mins6220', 'fix5mins6226', 'fix5mins6242', 'fix5mins6251', 'fix5mins6880', 'fix5mins7096', 'fix5mins7120', 'fix5mins7190', 'fix5mins7773', 'fix5mins8277', 'fix5mins8389', 'fix5mins8503', 'fix5mins8576', 'fix5mins8676', 'fix5mins8697', 'fix5mins870', 'fix5mins8785', 'fix5mins8819', 'fix5mins8822', 'fix5mins8824', 'fix5mins8833', 'fix5mins8897', 'fix5mins8907', 'fix5mins8913', 'fix5mins8944', 'fix5mins9002', 'fix5mins9019', 'fix5mins9049', 'fix5mins9090', 'fix5mins9108', 'fix5mins9146', 'fix5mins9157', 'fix5mins9199', 'fix5mins9203', 'fix5mins9227', 'fix5mins9251', 'fix5mins9253', 'fix5mins9255', 'fix5mins9259', 'fix5mins9260', 'fix5mins9814']


def get_fix_factor_evaluation(num, end_index, eval_indicator):
    factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{eval_indicator}.pkl')
    inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(using_factor_list)))
    factor_evaluation = factor_evaluation[inter_col]
    target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index.tolist())))
    if 'ret' in eval_indicator:
        print('ret')
        factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
    elif 'ic' in eval_indicator:
        print('ic')
        factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
    else:
        raise Exception('')
    factor_list = factor_evaluation.index.tolist()[:num]
    return sorted(factor_list)

def get_5min_factor_evaluation(num,end_index,eval_indicator):
    # num = 200
    # end_index=20170506
    # eval_indicator = 'ic_h_d'
    # if os.path.exists(f'/data/group/800319/strategy_local_path3_ForMix/factor_list/{end_index}/XGB_{eval_indicator[-1].upper()}_400_factor_list.pkl'):
    if os.path.exists(f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_{eval_indicator[-1]}_ic_h_{eval_indicator[-1]}_factor_list/{end_index}.pkl'):
        eval_date_list = pd.read_pickle(f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_{eval_indicator[-1]}_ic_h_{eval_indicator[-1]}_factor_list/{end_index}.pkl')[1]#['5min']
        if len(eval_date_list) != num:
            raise Exception('Wrong')
    factor_list = random.sample(available_factor_5min_list,num)
    return sorted(factor_list)

def load_dataset(start_date,end_date,fix_factor_list,min5_factor_list,min5_adress='/arch1/group/800442/800319/MinFactor/FactorFixData/Factor/',fix_address=None):
    # X, y, nolimit, idx_date, idx_code, idx_time = load_mix_data(start_date,end_date, m5_factors=min5_factor_list, m30_factors=fix_factor_list)
    X_5min, y_5min, nolimit_5min, idx_date_5min,idx_code_5min, idx_time_5min = load_fix_data(start_date=start_date,end_date=end_date,factor_list=min5_factor_list,address=min5_adress)
    if fix_address is None:
        X_fix, y_fix, nolimit_fix, idx_date_fix,idx_code_fix, idx_time_fix = load_fix_data(start_date=start_date,end_date=end_date,factor_list=fix_factor_list)
    else:
        X_fix, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix = load_fix_data(start_date=start_date, end_date=end_date, factor_list=fix_factor_list,address=fix_address)
    if X_5min.shape!=X_fix.shape:
        raise Exception('Fix shape is not equal to 5min shape')
    X = np.concatenate((X_fix,X_5min),axis=0)
    if (idx_date_5min!=idx_date_fix).sum()>0 or (idx_time_5min!=idx_time_fix).sum()>0 or (idx_code_5min!=idx_code_fix).sum()>0:
        raise Exception('idx are not match')
    X, y, idx_date, idx_code, idx_time=feature_engineering(X, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
    return pd.DataFrame(X,index=index,columns=fix_factor_list+min5_factor_list),pd.DataFrame({'actual_label':y},index=index)

def fit_model(i,output_path,indicator_fix,indicator_daily):
    train_start,train_end,test_start,test_end = para_list[i][1]
    print(para_list[i][1])
    path_dict = dict(
    res_path=output_path,
    val_path=output_path[:-1] + '_val_pred/',
    model_conf_path = output_path[:-1] + '_model_conf/',
    feature_eval_path = output_path[:-1] + '_feature_eval/',
    feature_path = output_path[:-1] + '_factor_list/'
    )
    for each in path_dict:
        if not os.path.exists(path_dict[each]):
            os.mkdir(path_dict[each])
    if os.path.exists(path_dict['res_path']+'%d.pkl'%train_end):
        print(train_end,'exist')
        # return
    date_list = get_date_range(train_start, train_end)
    val_date_list = [date_list[-i] for i in [3,5,7,9,11]]
    fix_factor_list = get_fix_factor_evaluation(200,train_end,eval_indicator=indicator_fix)
    min5_factor_list = get_5min_factor_evaluation(200,train_end,eval_indicator=indicator_daily)
    pd.to_pickle([fix_factor_list, min5_factor_list], path_dict['feature_path'] + '%d.pkl' % train_end)

    if True:#not os.path.exists(path_dict['model_conf_path']+'%d.json'%train_end):
        # X_train,y_train = load_dataset(dp,date_list[0],date_list[-2],fix_factor_list,min5_factor_list)
        print('train model')
        X_train,y_train =  load_dataset(date_list[0],date_list[-2],fix_factor_list,min5_factor_list)
        date_list = sorted((list(set(date_list) - set(val_date_list))))
        X_val,y_val = X_train.loc[val_date_list],y_train.loc[val_date_list]
        X_train,y_train = X_train.loc[date_list],y_train.loc[date_list]

        d_train = xgb.DMatrix(X_train[:-50000],label=y_train[:-50000].values)
        d_eval = xgb.DMatrix(X_train[-50000:],label=y_train[-50000:].values)
        model = xgb.train(params=best_param_clf_xgb,dtrain=d_train,num_boost_round=best_param_clf_xgb['n_estimators'],evals=[(d_eval,'d_eval')],early_stopping_rounds=15,verbose_eval=False)
        eval_res = pd.DataFrame(
            {each : pd.Series(model.get_score(importance_type=each)) for each in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']}
        )
        eval_res['fscore'] = pd.Series(model.get_fscore())
        pd.to_pickle(eval_res,path_dict['feature_eval_path']+'%d.pkl'%train_end)

        model.save_model(path_dict['model_conf_path']+'%d.json'%train_end)
    else:
        X_val,y_val = load_dataset(date_list[-11],date_list[-2],fix_factor_list,min5_factor_list)

        model = xgb.Booster()
        model.load_model(path_dict['model_conf_path']+'%d.json'%train_end)
    d_val = xgb.DMatrix(X_val)
    y_val['prediction'] = model.predict(d_val)
    pd.to_pickle(y_val,path_dict['val_path']+'%d.pkl'%train_end)
    if test_start==test_end and test_start==train_end:
        X_test,y_test = pd.DataFrame(),pd.DataFrame()
    else:
        X_test, y_test = load_dataset(test_start,test_end,fix_factor_list,min5_factor_list)
        d_test = xgb.DMatrix(X_test)
        y_test['prediction'] = model.predict(d_test)
        print(train_end,y_test.corr())
    pd.to_pickle(y_test,path_dict['res_path']+'%d.pkl'%train_end)
    print(path_dict['res_path']+'%d.pkl'%train_end)
    return True

# while len(os.listdir('/arch1/group/800442/800319/FixlizeDailyFactor/dataShift/'))<936:
#     print(len(os.listdir('/arch1/group/800442/800319/FixlizeDailyFactor/dataShift/')))
#     time.sleep(120)

# factor_list_fix,factor_list_5min = pd.read_pickle('/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_ic_d_ic_h_d_factor_list/20210702.pkl')
# _,_,test_start,test_end = para_list[137][1]
# res = load_dataset(test_start,test_end,factor_list_fix,factor_list_5min,min5_adress='/arch1/group/800442/800319/MinFactor/FactorFixData/Factor/',fix_address=None)

# i=0
import datetime
idx_list = list(range(142))[::-1][:1]
# idx_list = idx_list[len(idx_list)*i//3:len(idx_list)*(i+1)//3]
for idx in tqdm(idx_list):
    fix_indicator, daily_indicator = 'ic_t', 'ic_h_t'
    out_path = f'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiDeltaEraForVal/XGBMultiFreqFix5minNoEnhancedMinuteOnlyHandy_train200_test10_{fix_indicator}_{daily_indicator}/'
    fit_model(idx, out_path, fix_indicator, daily_indicator)
    gc.collect()

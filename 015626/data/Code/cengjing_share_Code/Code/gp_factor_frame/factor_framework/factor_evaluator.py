import os
import shutil
import traceback
import pandas as pd
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
import bottleneck as bk
from xquant.factordata import FactorData
from multiprocessing import Pool
from multifactor.IO import IO
from function_tools import *
from sklearn.linear_model import LinearRegression
import xgboost as xgb
# import shap
import copy
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import gridspec


class FactorEvaluator(object):

    def __init__(self):
        OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

        # self.variety_list = ['IC', 'IH', 'IF']
        # self.multi_variety_list = ['IH_IC', 'IC_IH', 'IF_IC', 'IC_IF', 'IH_IF', 'IF_IH']
        # self.data_type_dict = {'1T': 'minute_pickles',
        #                        'minute_index': 'minute_index_pickles',
        #                        'multi_minute': 'multi_minute_pickles',
        #                        '10s': '10s_pickles',
        #                        'tick': 'temp_pickles'}

        self.__factor_data_path = '{}/data_center/factor_data'.format(OUTER_ROOT_PATH)
        self.__minute_future_path = '/data/user/015615/MarketData/MD/CHINA_FUTURES/MINUTE'
        self.__store_data_path = '/data/user/015615/index_future/data_center/factor_data'
        self.__factor_status_path = '/data/user/015615/index_future/data_center/factor_data/factor_status.pkl'
        self.__factor_longshort_path = '{}/data_center/factor_data/factor_longshort'.format(OUTER_ROOT_PATH)
        self.__evaluation_data_path = '/data/user/016756/Share/factor_evaluation_data'

        self.MAX_CORR = 0.5

    
    def get_trading_days(self, start_date, end_date):
        return sorted(get_trading_days(start_date, end_date))


    def get_factor_value(self, factor_name, variety):
        return pd.read_hdf('{}/minute_raw/{}/{}.h5'.format(self.__factor_data_path, variety, factor_name))


    def get_factor_tsrank(self, factor_name, variety):
        return pd.read_hdf('{}/minute_norm/{}/{}.h5'.format(self.__factor_data_path, variety, factor_name))

    
    def __get_factor_list(self, variety):

        df_factor_status = pd.read_pickle(self.__factor_status_path)
        df_factor_by_variety = df_factor_status.loc[variety]

        return list(df_factor_by_variety.index)

    
    def get_all_factor_names(self, variety):

        factor_status = pd.read_pickle(self.__factor_status_path)
        factor_list = factor_status.loc[factor_status['is_criteria_2']==True].loc[variety].index.values
        
        return factor_list


    def merge_all_tsrank_factor(self, variety, start_date, end_date):

        factor_list = self.get_all_factor_names(variety)
        factor_df_list = []
        for f in factor_list:
            factor_df_list.append(pd.read_hdf('{}/minute_norm/{}/{}.h5'.format(self.__store_data_path, variety, f))[start_date:end_date])
        return pd.concat(factor_df_list, axis=1)


    def calc_tsrank_max_corr_by_df(self, factor_df, variety, start_date, end_date, n = 10):

        df_all = self.merge_all_tsrank_factor(variety, start_date, end_date)
        factor_name = factor_df.columns[0]
        s_corr = abs(df_all.corrwith(factor_df.iloc[:, 0], axis=0)).sort_values(ascending=False)
        if factor_name == s_corr.index[0]:
            s_corr = s_corr.drop(factor_name)
        max_corr = s_corr.iloc[0]
        
        return s_corr[:n]


    def calc_tsrank_max_corr_by_name(self, factor_name, variety, start_date, end_date, n = 10):

        df_all = self.merge_all_tsrank_factor(variety, start_date, end_date)
        factor_df = self.get_factor_tsrank(factor_name, variety)
        s_corr = abs(df_all.corrwith(factor_df.iloc[:, 0], axis=0)).sort_values(ascending=False)
        if factor_name == s_corr.index[0]:
            s_corr = s_corr.drop(factor_name)
        max_corr = s_corr.iloc[0]
        
        return s_corr[:n]
    
    
    def calc_tsrank_max_corr_by_name_list(self, factor_name_list, variety, start_date, end_date):
        df_all = self.merge_all_tsrank_factor(variety, start_date, end_date)
        df_new_factors = pd.concat([self.get_factor_tsrank(factor_name, variety) for factor_name in factor_name_list], axis=1)

        df_total = pd.concat([df_all, df_new_factors], axis=1)
        df_total = df_total.iloc[:, ~df_total.columns.duplicated()]

        max_corr_dict = {}
        df_corr = abs(df_total.corr())

        for i in range(len(factor_name_list)):
            ts_rank_name = factor_name_list[i]
            temp_corr = df_corr.loc[ts_rank_name].sort_values(ascending=False)
            temp_unique_corr = temp_corr.loc[temp_corr.index != ts_rank_name]
            max_corr_dict[ts_rank_name] = {'factor_name': temp_unique_corr.index[0],
                                           'max_corr_value': temp_unique_corr.iloc[0]}
            df_result = pd.DataFrame.from_dict(max_corr_dict).T
            df_result['is_corr_passed'] = df_result['max_corr_value'] < self.MAX_CORR

        return df_result


    def calc_longshort_max_corr_by_name(self, factor_name, variety, start_date, end_date, n = 10):

        all_factor_longshort = pd.read_pickle('{}/factor_longshort_{}.pickle'.format(self.__evaluation_data_path,variety))
        factor_longshort = pd.read_pickle('{}/{}/{}.pickle'.format(self.__factor_longshort_path, variety, factor_name))
        s_corr = abs(all_factor_longshort.corrwith(factor_longshort.iloc[:, 0], axis=0)).sort_values(ascending=False)
        if factor_name == s_corr.index[0]:
            s_corr = s_corr.drop(factor_name) 
        max_corr = s_corr.iloc[0]
        
        return s_corr[:n]
    
    
    def calc_longshort_max_corr_by_name_list(self, factor_name_list, variety, start_date, end_date):
        
        all_factor_longshort = pd.read_pickle('{}/factor_longshort_{}.pickle'.format(self.__evaluation_data_path,variety))
        factor_longshort = pd.concat([pd.read_pickle('{}/{}/{}.pickle'.format(self.__factor_longshort_path, variety, factor_name))for factor_name in factor_name_list], axis=1)

        df_total = pd.concat([all_factor_longshort, factor_longshort], axis=1)
        df_total = df_total.iloc[:, ~df_total.columns.duplicated()]

        max_corr_dict = {}
        df_corr = abs(df_total.corr())

        for i in range(len(factor_name_list)):
            ts_rank_name = factor_name_list[i]
            temp_corr = df_corr.loc[ts_rank_name].sort_values(ascending=False)
            temp_unique_corr = temp_corr.loc[temp_corr.index != ts_rank_name]
            max_corr_dict[ts_rank_name] = {'factor_name': temp_unique_corr.index[0],
                                           'max_corr_value': temp_unique_corr.iloc[0]}
            df_result = pd.DataFrame.from_dict(max_corr_dict).T
            df_result['is_corr_passed'] = df_result['max_corr_value'] < self.MAX_CORR

        return df_result
    
    
    def get_max_corr_passed_df(self, factor_name_list, variety, data_type, start_date, end_date):
        df_max_corr = self.calc_max_corr_by_name_list(factor_name_list, variety, start_date, end_date)
        df_max_corr['max_corr'] = df_max_corr['max_corr_value'] < self.MAX_CORR
        return df_max_corr['max_corr'].to_frame()


    def get_Trading_Twap_by_period(self, variety, start_date, end_date, instrument_type='main'):

        future_data = IO.read_data([start_date, end_date+'235959'],alt='{}/{}_MINUTE.h5'.format(self.__minute_future_path, variety))
        twap = select_data_by_univ(future_data, variety, instrument_type).reset_index().set_index('dt').shift(-1)['twap']

        return twap


    def get_drawdown_num(self, Longshort, threshold = -3):

        drawdown = (Longshort.cumsum()-Longshort.cumsum().expanding().max())
        zero_drawdown = drawdown[drawdown == 0]
        zero_drawdown_date = zero_drawdown.index
        local_max_drawdown_value = []
        local_max_drawdown_date = []

        for i in range(len(zero_drawdown_date)):
            start_date = zero_drawdown_date[i]
            if i == len(zero_drawdown_date) - 1:   
                end_date = Longshort.index[-1]
            else:
                end_date = zero_drawdown_date[i + 1]
            local_max_drawdown_value.append(drawdown[start_date:end_date].min())
            local_max_drawdown_date.append(drawdown[start_date:end_date].argmin())

        local_max_drawdown = pd.Series(local_max_drawdown_value, index = local_max_drawdown_date)
        large_local_max_drawdown = local_max_drawdown[local_max_drawdown < threshold]
        
        return len(large_local_max_drawdown)


    def get_bounce_drawdown_sharpe_ratio(self, Longshort):

        cumulative_return = Longshort.cumsum()
        max_cumulative_return = Longshort.cumsum().expanding().max()
        unique_max_cumulative_return = Longshort.cumsum().expanding().max().unique()

        drawdown = (Longshort.cumsum()-Longshort.cumsum().expanding().max())
        mdd = (Longshort.cumsum()-Longshort.cumsum().expanding().max()).min()

        mdd_date = drawdown.argmin(mdd)
        pre_high_date = max_cumulative_return.index[max_cumulative_return.searchsorted(max_cumulative_return[mdd_date])]

        if mdd_date == Longshort.index[-1]:
            up_down_sharpe_ratio = np.nan

        else:
            if max_cumulative_return[pre_high_date] == max_cumulative_return[-1]:
                next_high_date = cumulative_return[mdd_date:].argmax()
            else:
                next_high_idx = np.where(unique_max_cumulative_return == max_cumulative_return[pre_high_date])[0][0] + 1
                next_high_value = unique_max_cumulative_return[next_high_idx]
                next_high_date = max_cumulative_return.index[max_cumulative_return.searchsorted(next_high_value)]
                
            down_sharpe = Longshort[pre_high_date:mdd_date].mean() / Longshort[pre_high_date:mdd_date].std() if Longshort[pre_high_date:mdd_date].std() != 0 else np.nan 
            up_sharpe = Longshort[mdd_date:next_high_date].mean() / Longshort[mdd_date:next_high_date].std() if Longshort[mdd_date:next_high_date].std() != 0 else np.nan 
            up_down_sharpe_ratio = up_sharpe / abs(down_sharpe) if down_sharpe != 0 else np.nan

        return up_down_sharpe_ratio


    def get_dt(self, date, time):
        year = int(date) // 10000
        month = int(date) % 10000 //100
        day = int(date)% 100
        hour = time // 10000000
        minute = time // 100000 % 100
        s = 0

        return datetime.datetime(year, month, day, hour, minute, 0)


    def convert_datetime_index(self, df):
        date_time = df.reset_index()[['level_0','level_1']]
        df.index = date_time.apply(lambda x: self.get_dt(x.level_0, x.level_1), axis = 1)
        
        return df


    def get_factor_residual_tsrank(self, factor_df, start_date, end_date, tslookback):

        factor_df = factor_df[start_date:end_date]
        signal_df = pd.read_pickle('signals/ridge/signal_5_15_30.pkl')
        signal_df = self.convert_datetime_index(signal_df)
        data = pd.concat([factor_df,signal_df], axis = 1).dropna(how = 'any')
        y = data.iloc[:,[0]]
        x = data.iloc[:,[1]]

        reg = LinearRegression(fit_intercept = False).fit(x, y)
        factor_residual = y - np.dot(x, reg.coef_)
        factor_residual_tsrank = (pd.DataFrame(bk.move_rank(factor_residual, window = tslookback, min_count = int(tslookback / 2), axis=0), 
                               index = factor_residual.index, columns = factor_residual.columns) + 1) / 2
        
        return factor_residual_tsrank


    def compare_factor_and_residual(self, factor_df, variety, start_date, end_date, tslookback):
        
        _,factor_summary = self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date, end_date, show_result = False, save_longshort = False)
        factor_residual = self.get_factor_residual_tsrank(factor_df, start_date, end_date, tslookback)
        _,residual_summary = self.calc_statistic_by_factor_tsrank_df(factor_residual, variety, start_date, end_date, show_result = False, save_longshort = False)
        
        compare_df = pd.concat([factor_summary, residual_summary], axis = 1)
        compare_df['diff'] = factor_summary - residual_summary
        compare_df.columns = ['factor', 'residual', 'diff']

        return compare_df.loc[['LongShortSR','ProfitPerDealDiff (%)']]


    def calc_factor_ts_sensitivity(self, raw_factor_df, variety, start_date, end_date, tslookback, tslookback_list = [1 * 237, 5 * 237, 10 * 237, 20 * 237]):

        for lb in tslookback_list:
            if abs(lb - tslookback) <= 3 * 20:
                tslookback_list.remove(lb)
        tslookback_list = [tslookback] + tslookback_list

        summary_list = []
        for tslookback in tslookback_list:
            factor_tsrank = (pd.DataFrame(bk.move_rank(raw_factor_df, window = tslookback, min_count = int(tslookback / 2), axis=0), 
                       index = raw_factor_df.index, columns = raw_factor_df.columns) + 1) / 2
            _, summary = self.calc_statistic_by_factor_tsrank_df(factor_tsrank, variety, start_date, end_date, show_result = False, save_longshort = False)
            summary_list.append(summary)
        summary_df = pd.concat(summary_list,axis = 1)
        summary_df.columns = tslookback_list

        return summary_df


    def get_close_by_period(self, variety, start_date, end_date, instrument_type='main'):

        future_data = IO.read_data([start_date, end_date+'235959'],alt='{}/{}_MINUTE.h5'.format(self.__minute_future_path, variety))
        close = select_data_by_univ(future_data, variety, instrument_type).reset_index().set_index('dt')['close']

        return close


    def get_operation_time(self, today_factor):
        long_threshold = 0.9
        short_threshold = 0.1
        close_threshold = 0.5
        operation_time_dict = {'OpenLong':[],
                              'OpenShort':[],
                              'InvOpenLong':[],
                              'InvOpenShort':[]
                             }
        current_position = 0

        for i in range(len(today_factor)):

            if i != len(today_factor) - 1:       
                if current_position == 1:
                    if today_factor.iloc[i,0] > close_threshold:
                        pass
                    elif today_factor.iloc[i,0] <= close_threshold:
                        operation_time_dict['InvOpenShort'].append(i)
                        current_position = 0
                elif current_position == -1:
                    if today_factor.iloc[i,0] < close_threshold:
                        pass
                    elif today_factor.iloc[i,0] >= close_threshold:
                        operation_time_dict['InvOpenLong'].append(i)
                        current_position = 0
                else:
                    if today_factor.iloc[i,0] >= long_threshold:
                        operation_time_dict['OpenLong'].append(i)
                        current_position = 1
                    elif today_factor.iloc[i,0] <= short_threshold:
                        operation_time_dict['OpenShort'].append(i)
                        current_position = -1
                    else:
                        pass

            else:
                if current_position == 1:
                    operation_time_dict['InvOpenShort'].append(i)
                    current_position = 0     
                elif current_position == -1:
                    operation_time_dict['InvOpenLong'].append(i)
                    current_position = 0
                else:
                    pass
            
        return operation_time_dict


    def get_factor_trading_plot(self, factor_df, variety, start_date, end_date, longshort_rank_list = [0,1,2]):

        factor_name = factor_df.columns[0]
        factor_longshort = pd.read_pickle('{}/{}/{}.pickle'.format(self.__factor_longshort_path, variety, factor_name))[start_date:end_date]
        factor_longshort_sort = factor_longshort.sort_values(by = factor_name)

        start_date = factor_longshort.index[0]
        end_date = factor_longshort.index[-1]
        close = self.get_close_by_period(variety, start_date, end_date)

        marker_dict = {'OpenLong':'^',
                  'OpenShort':'^',
                  'InvOpenLong':'v',
                  'InvOpenShort':'v'}
        color_dict = {'OpenLong':'red',
                      'OpenShort':'green',
                      'InvOpenLong':'red',
                      'InvOpenShort':'green'}
            
        for i in longshort_rank_list:
            date = factor_longshort_sort.index.values[i]
            today_return = factor_longshort_sort.values.flatten()[i]
            today_close = close[date]
            today_factor = factor_df[date]  
            operation_time_dict = self.get_operation_time(today_factor)
            
            fig, ax = plt.subplots(figsize=(10,5))
            ax.plot(today_factor.values.flatten(), linewidth = 2, label = 'Factor Tsrank')
            ax_2 = ax.twinx()
            ax_2.plot(today_close.values, color = 'grey', alpha = 0.7, label = 'Index Future')
            for k in operation_time_dict.keys():
                if operation_time_dict[k]:
                    plt.scatter(operation_time_dict[k], today_close[operation_time_dict[k]].tolist() ,label = k, marker = marker_dict[k], color = color_dict[k], s = 100)

            ax.legend(loc =(0.85,0.95),fontsize = 8)
            ax.set_ylabel('Signal Tsrank', fontsize = 10)
            ax.set_xlabel('Time',fontsize = 10)
            ax.tick_params(labelsize = 10)
            time_idx = np.arange(0,len(today_factor) - 1,30)
            ax.set_xticklabels(time_idx, rotation = 45, fontsize = 10, va = 'bottom')
            ax.grid(axis = 'y')

            ax_2.legend(loc = (0.85,0.7), fontsize = 8)
            ax_2.set_ylabel('Index Future', fontsize = 10)
            ax_2.tick_params(labelsize = 10)

            plt.xticks(time_idx, today_factor.index[time_idx])
            plt.title(date + ':' + str(round(today_return,2)) + '%', fontsize = 12)
            plt.show()


    def merge_factors_by_name_list(self, variety, start_date, end_date, factor_list = None):

        if factor_list == None:
            factor_list = pd.read_excel('factor_names_{}.xlsx'.format(variety)).values.flatten()

        factor_df_list = []
        for f in factor_list:
            factor_df_list.append(pd.read_hdf('{}/minute_norm/{}/{}.h5'.format(self.__store_data_path, variety, f))[start_date:end_date])
        return pd.concat(factor_df_list, axis=1)


    def compare_factor_equal_weight_model(self, factor_df, variety, start_date, end_date, threshold = 0.95, tslookback = 5 * 237):

        model_factor = self.merge_all_tsrank_factor(variety, start_date, end_date)
        factor_name = factor_df.columns[0]
        if factor_name in model_factor.columns:
            model_factor.drop([factor_name], axis = 1, inplace = True)
        all_factor = pd.concat([model_factor, factor_df], axis = 1).dropna()
        
        _, current_summary = self.Strategy_Simple_Test(all_factor.iloc[:,:-1].mean(axis = 1), variety, start_date, end_date, OpenLong=threshold, OpenShort=1-threshold, show_result = False)
        _, new_summary = self.Strategy_Simple_Test(all_factor.mean(axis = 1), variety, start_date, end_date, OpenLong=threshold, OpenShort=1-threshold, show_result = False)
        
        compare_df = pd.concat([current_summary, new_summary], axis = 1).loc[['LongShortSR','ProfitPerDeal (%)']]
        compare_df.columns = ['current','new']
        compare_df['diff (%)'] = (compare_df['new'] - compare_df['current']) / compare_df['current'] * 100

        return compare_df


    def get_factor_importance_in_xgb(self, factor_df, variety, start_date, end_date, label_period_list = [5,15,30]): 

        model_factor = self.merge_all_tsrank_factor(variety, start_date, end_date)
        factor_name = factor_df.columns[0]
        if factor_name in model_factor.columns:
            model_factor.drop([factor_name], axis = 1, inplace = True)
        all_factor = pd.concat([model_factor, factor_df], axis = 1).dropna()

        twap = self.get_Trading_Twap_by_period(variety, start_date, end_date)
        all_label_list = []
        date_list = [date.strftime('%Y%m%d') for date in np.unique(twap.index.date)]
        for label_period in label_period_list:
            label_list = []
            for date in date_list:
                label_list.append(twap.loc[date].iloc[:-3].pct_change(label_period).shift(-label_period))
            all_label_list.append(pd.concat(label_list).to_frame(name='return_{}'.format(label_period)))
        all_label = pd.concat(all_label_list, axis = 1)
        all_label.insert(0,'date', all_label.reset_index()['dt'].apply(lambda x: x.date().strftime('%Y%m%d')).values)

        shap_values_summary_list = []
        feature_importance_summary_list = []

        for label_period in [5,15,30]:
            shap_values_list = []
            feature_importance_list = []
            
            for seed in [1,2,3,4,5]:
                
                shuffle_date_list = copy.deepcopy(date_list)
                np.random.seed(seed)
                np.random.shuffle(shuffle_date_list)
                data = all_label[['date','return_{}'.format(label_period)]].join(all_factor, how='inner').dropna(axis=0, how='any')

                val_dates = shuffle_date_list[: len(shuffle_date_list) // 5]
                train_dates = list(set(shuffle_date_list) - set(val_dates))
                val_data = data[data['date'].isin(val_dates)]
                train_data = data[data['date'].isin(train_dates)]

                val_r = val_data.iloc[:, 1]
                val_r_mean, val_r_std = val_r.mean(), val_r.std()
                val_data.iloc[:, 1][val_r > (val_r_mean + 3 * val_r_std)] = val_r_mean + 3 * val_r_std
                val_data.iloc[:, 1][val_r < (val_r_mean - 3 * val_r_std)] = val_r_mean - 3 * val_r_std
                train_r = train_data.iloc[:, 1]
                train_r_mean, train_r_std = train_r.mean(), train_r.std()
                train_data.iloc[:, 1][train_r > (train_r_mean + 3 * train_r_std)] = train_r_mean + 3 * train_r_std
                train_data.iloc[:, 1][train_r < (train_r_mean - 3 * train_r_std)] = train_r_mean - 3 * train_r_std

                val_x = val_data.iloc[:, 2:].values
                val_y = val_data.iloc[:, 1].values 
                train_x = train_data.iloc[:, 2:].values
                train_y = train_data.iloc[:, 1].values

                model = xgb.XGBRegressor(tree_method='gpu_hist', gpu_id=0, n_estimators=5000, nthread=10, colsample_bytree=0.6,
                colsample_bynode=0.8, colsample_bylevel=0.8, seed=2020, max_depth=4, learning_rate=0.02)
                model.fit(X=train_x, y=train_y, verbose=False, eval_set=[(train_x, train_y), (val_x, val_y)], eval_metric=['rmse'],
                early_stopping_rounds=20)

                # explainer = shap.TreeExplainer(model)
                # shap_values = explainer.shap_values(train_x, approximate=True)
                # shap_values_list.append(pd.Series(np.nanmean(abs(shap_values), axis = 0), index = train_data.columns[2:]).rank(pct = True))
                feature_importance_list.append(pd.Series(model.feature_importances_, index = train_data.columns[2:]).rank(pct = True))
            
            # shap_values_df = pd.concat(shap_values_list,axis = 1)
            # shap_values_summary_list.append(shap_values_df.loc[factor_name])
            feature_importance_df = pd.concat(feature_importance_list,axis = 1)
            feature_importance_summary_list.append(feature_importance_df.loc[factor_name])

        # shap_values_summary_df = pd.concat(shap_values_summary_list,axis = 1).T
        # shap_values_summary_df.index = ['5min','15min','30min']
        # shap_values_summary_df['mean'] = shap_values_summary_df.mean(axis = 1)
        feature_importance_summary_df = pd.concat(feature_importance_summary_list,axis = 1).T
        feature_importance_summary_df.index = ['5min','15min','30min']
        feature_importance_summary_df['mean'] = feature_importance_summary_df.mean(axis = 1)

        return feature_importance_summary_df #, shap_values_summary_df


    def backtest_factor_by_group(self, mergeinfo, groupid, groupnum):

        mergeinfo['flag']=0 
        mergeinfo.loc[mergeinfo['group'] == groupid,'flag'] = 1
        midpoint = (groupnum+1)/2
        if groupid > midpoint:
            mergeinfo.loc[mergeinfo['group'] <= midpoint, 'flag'] = -1
        elif groupid <= midpoint:
            mergeinfo.loc[mergeinfo['group'] > midpoint, 'flag'] = -1

        DealsRtn = {}
        DealsHoldPeriods = {}
        DealsOpenCost = {}
        DealsProfit = {}       

        for date in [date.strftime('%Y%m%d') for date in np.unique(mergeinfo.index.date)]:
            dailydealsrtn = []
            dailydealsstarttime = []
            dailydealsendtime = []
            dailydealsholdperiods = []

            daily_deal_open_prices = []
            daily_deal_profits = []

            factordaily = mergeinfo.loc[date]
            opentwap = 0
            lastindex = 0

            if factordaily['flag'].values[0] == 1 :
                opentwap = factordaily['twap'].values[0]
                lastindex = 0
                dailydealsstarttime.append(factordaily.index[0])

            for i in range(1,len(factordaily)-1):
                if factordaily['flag'].values[i] == -1 and len(dailydealsstarttime) != len(dailydealsendtime):
                    rtn = factordaily['twap'].values[i]/opentwap-1
                    dailydealsrtn.append(rtn)
                    
                    daily_deal_open_prices.append(opentwap)
                    daily_deal_profits.append(factordaily['twap'].values[i] - opentwap)

                    dailydealsendtime.append(factordaily.index[i])
                    dailydealsholdperiods.append(i-lastindex)

                if factordaily['flag'].values[i] == 1 and len(dailydealsstarttime) == len(dailydealsendtime):
                    opentwap = factordaily['twap'].values[i]
                    dailydealsstarttime.append(factordaily.index[i])
                    lastindex=i

            if len(dailydealsstarttime) == len(dailydealsendtime)+1:
                rtn = factordaily['twap'].values[-1]/opentwap-1
                dailydealsrtn.append(rtn)

                daily_deal_open_prices.append(opentwap)
                daily_deal_profits.append(factordaily['twap'].values[-1] - opentwap)

                dailydealsendtime.append(factordaily.index[-1])
                dailydealsholdperiods.append(237-lastindex)
            
            DealsRtn[date] = dailydealsrtn
            DealsHoldPeriods[date] = dailydealsholdperiods

            DealsOpenCost[date] = daily_deal_open_prices
            DealsProfit[date] = daily_deal_profits

        result = {}

        for date in DealsRtn.keys():
            result[date] = pd.DataFrame([DealsRtn[date],DealsHoldPeriods[date],DealsOpenCost[date],DealsProfit[date]]).transpose()

        result = pd.concat(result)
        result.columns=['rtn', 'holdperiods','opencost','profit']
        
        return result


    def calc_statistic_by_factor_tsrank_df(self, factor_df, variety, start_date, end_date, groupnum=10, ncore=20, show_result = True, save_longshort = True):

        factor_name = factor_df.columns[0]
        df_tsfactor = factor_df[start_date:end_date][[factor_name]]
                
        twap = self.get_Trading_Twap_by_period(variety, start_date, end_date)
        mergeinfo = pd.concat([df_tsfactor, twap], axis=1).dropna()
        mergeinfo['group'] = np.ceil((mergeinfo[factor_name] * groupnum))
        mergeinfo['group'][mergeinfo['group']==0] = 1

        RESULT = {}

        pool = Pool(ncore)
        tasks = []
        for groupid in range(1, groupnum+1):
            tasks.append([pool.apply_async(self.backtest_factor_by_group, args=(mergeinfo, groupid, groupnum)), groupid])
        pool.close()

        for t, groupid in tasks:
            try:
                RESULT[groupid]= t.get()
            except Exception as e:
                print(e, traceback.format_exc())
        pool.join()

        summarydictdf = self.calc_statistic_by_factor_result(RESULT, factor_name, variety, start_date, end_date, show_result, save_longshort, groupnum)

        return RESULT, summarydictdf


    def calc_statistic_by_factor_result(self, RESULT, factor_name, variety, start_date, end_date, show_result = False, save_longshort = False, groupnum=10):

        for i in range(1, len(RESULT) + 1):
            RESULT[i] = RESULT[i].loc[start_date:end_date]

        tmp = pd.concat(RESULT)['rtn'].unstack(0)
        DailyDealNum = (~tmp.isnull()).groupby(level=0).sum().mean()
        AvgHoldPeriods = pd.concat(RESULT).unstack(0)['holdperiods'].groupby(level=0).mean().mean()
        SegementDailyReturn = pd.concat(RESULT).unstack(0)['rtn'].fillna(0).groupby(level=0).sum()*100
        Longshort = (SegementDailyReturn.iloc[:,-1]-SegementDailyReturn.iloc[:,0])
        if save_longshort:
            pd.DataFrame(Longshort, columns = [factor_name]).to_pickle('{}/{}/{}_{}.pickle'.format(self.__factor_longshort_path, variety, factor_name, groupnum))

        ProfitPerDeal = pd.concat(RESULT)['rtn'].unstack(0).mean()*100

        summary = pd.concat([ProfitPerDeal, DailyDealNum, AvgHoldPeriods, SegementDailyReturn.mean()], axis=1)
        summary.columns=['ProfitPerDeal (%)', 'DailyDealNum', 'AvgHoldPeriods',' DailyReturn (%)']
        summary = summary.T
        
        summarydict = {}
        summarydict['LongShortAnualReturn (%)'] = Longshort.mean()*250
        summarydict['LongShortSR'] = Longshort.mean()/Longshort.std()
        summarydict['ProfitPerDealDiff (%)'] = ProfitPerDeal.max() - ProfitPerDeal.min()
        summarydict['MaxProfitGroup'] = ProfitPerDeal[ProfitPerDeal==ProfitPerDeal.max()].index.values[0]
        summarydict['MinProfitGroup'] = ProfitPerDeal[ProfitPerDeal==ProfitPerDeal.min()].index.values[0]
        
        summarydict['MaxDrawdown'] = (Longshort.cumsum()-Longshort.cumsum().expanding().max()).min()
        summarydict['MaxRecoverTime'] = Longshort.cumsum().expanding().max().value_counts().iloc[0]
        summarydict['DrawdownNum'] = self.get_drawdown_num(Longshort)
        summarydict['BounceDrawdownSharpeRatio'] = self.get_bounce_drawdown_sharpe_ratio(Longshort)

        summarydict['LongShortSR_2018'] = Longshort.loc['20180201':'20181231'].mean()/Longshort.loc['20180201':'20181231'].std()
        summarydict['LongShortSR_2019'] = Longshort.loc['20190101':'20191231'].mean()/Longshort.loc['20190101':'20191231'].std()
        summarydict['LongShortSR_2020'] = Longshort.loc['20200101':'20200630'].mean()/Longshort.loc['20200101':'20200630'].std()
        
        summarydict['LongSR'] = SegementDailyReturn.iloc[:,-1].mean() / SegementDailyReturn.iloc[:,-1].std() 
        summarydict['ShortSR'] = -1 * SegementDailyReturn.iloc[:,0].mean() / SegementDailyReturn.iloc[:,0].std() 

        summarydict['LongProfitPerDeal (%)'] = ProfitPerDeal.iloc[-1]
        summarydict['ShortProfitPerDeal (%)'] = -1 * ProfitPerDeal.iloc[0]
        
        summarydict['DailyWinRate'] = (Longshort > 0).mean()
        summarydict['LongDailyWinRate'] = (SegementDailyReturn.iloc[:,-1] > 0).mean()
        summarydict['ShortDailyWinRate'] = (SegementDailyReturn.iloc[:,0] < 0).mean()

        summarydict['TradeWinRate'] = ((RESULT[10]['rtn'] > 0).sum() + (RESULT[1]['rtn'] < 0).sum()) / (RESULT[10].shape[0] + RESULT[1].shape[0])
        summarydict['LongTradeWinRate'] = (RESULT[10]['rtn'] > 0).sum() / RESULT[10].shape[0]
        summarydict['ShortTradeWinRate'] = (RESULT[1]['rtn'] < 0).sum() / RESULT[1].shape[0]

        summarydict['ProfitLossRatio'] = (RESULT[10]['rtn'][RESULT[10]['rtn'] > 0].sum() - RESULT[1]['rtn'][RESULT[1]['rtn'] < 0].sum()) / \
        (RESULT[1]['rtn'][RESULT[1]['rtn'] > 0].sum() - RESULT[10]['rtn'][RESULT[10]['rtn'] < 0].sum())
        summarydict['LongProfitLossRatio'] =  -1 * RESULT[10]['rtn'][RESULT[10]['rtn'] > 0].sum() / RESULT[10]['rtn'][RESULT[10]['rtn'] < 0].sum() 
        summarydict['ShortProfitLossRatio'] = -1 * RESULT[1]['rtn'][RESULT[1]['rtn'] < 0].sum() / RESULT[1]['rtn'][RESULT[1]['rtn'] > 0].sum() 

        summarydict['AvgHoldPeriods'] = summary.loc['AvgHoldPeriods'].iloc[[0,-1]].mean()
        summarydict['ShortAvgHoldPeriods'] = summary.loc['AvgHoldPeriods'].iloc[0]
        summarydict['LongAvgHoldPeriods'] = summary.loc['AvgHoldPeriods'].iloc[-1]

        flag = summarydict['ProfitPerDealDiff (%)'] > 0.04 and \
               summarydict['MaxProfitGroup'] - summarydict['MinProfitGroup'] >= 7 and \
               summarydict['LongShortSR'] >= 0.1
        summarydict['Pass'] = flag

        summarydictdf = pd.DataFrame(summarydict, index=[factor_name]).T
        print_varaible = ['LongShortAnualReturn (%)', 'LongShortSR', 'ProfitPerDealDiff (%)', 'MaxProfitGroup', 'MinProfitGroup', \
                        'MaxDrawdown', 'MaxRecoverTime', 'DrawdownNum', 'BounceDrawdownSharpeRatio', \
                        'LongShortSR_2018', 'LongShortSR_2019', 'LongShortSR_2020', 'LongSR', 'ShortSR', 'Pass']

        if show_result:
            SegementDailyReturn.cumsum().plot(title='Daily Profit Segment Curve')
            plt.show()
            ProfitPerDeal.plot(kind='bar', title='Profit Per Deal Segment Curve')
            plt.show()
            print(summary)
            Longshort.cumsum().plot(title='Long Short Curve')
            plt.show()
            print(summarydictdf.loc[print_varaible])

        return summarydictdf


    def calc_statistic_by_factor_name(self, factor_name, variety, start_date, end_date, groupnum=10):

        factor_df = self.get_factor_tsrank(factor_name, variety)
        return self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date, end_date, groupnum)


    def Strategy_Simple_Test(self, prediction, variety, start_date, end_date, tslookback=5, OpenLong=0.95, OpenShort=0.05, CloseLong=0.5, CloseShort=0.5, fee=0.0004, show_result = True):

        tradingprice = self.get_Trading_Twap_by_period(variety, start_date, end_date)
        mergeinfo = pd.concat([prediction, tradingprice],axis=1).dropna()
        mergeinfo.columns=['prediction', 'tradeprice']
        mergeinfo['tsrank'] = (bk.move_rank(mergeinfo['prediction'].values, 237*tslookback)+1)/2
        DealsRtn = {}
        DealsStartTime = {}
        DealsEndTime = {}
        DealsHoldPeriods = {}

        date_list = [date.strftime('%Y%m%d') for date in np.unique(mergeinfo.index.date)]
        for date in date_list[tslookback+1:]:
            dailydealsrtn = []
            dailydealsstarttime = []
            dailydealsendtime = []
            dailydealsholdperiods = []

            factordaily = mergeinfo.loc[date]
            opentwap = 0
            lastindex = 0

            if factordaily['tsrank'].values[0] >= OpenLong :
                opentwap = factordaily['tradeprice'].values[0]
                lastindex = 0
                dailydealsstarttime.append(factordaily.index[0])

            for i in range(1,len(factordaily)-1):
                if factordaily['tsrank'].values[i] < CloseLong and factordaily['tsrank'].values[i-1] >= CloseLong and len(dailydealsstarttime) != len(dailydealsendtime) :
                    rtn = factordaily['tradeprice'].values[i]/opentwap-1 -fee
                    dailydealsrtn.append(rtn)
                    dailydealsendtime.append(factordaily.index[i])
                    dailydealsholdperiods.append(i-lastindex)

                if factordaily['tsrank'].values[i-1] < OpenLong and factordaily['tsrank'].values[i] >= OpenLong and len(dailydealsstarttime) == len(dailydealsendtime) :
                    opentwap = factordaily['tradeprice'].values[i]
                    dailydealsstarttime.append(factordaily.index[i])
                    lastindex=i

            if len(dailydealsstarttime) == len(dailydealsendtime)+1:
                rtn = factordaily['tradeprice'].values[-1] / opentwap - 1 - fee
                dailydealsrtn.append(rtn)
                dailydealsendtime.append(factordaily.index[-1])
                dailydealsholdperiods.append(237-lastindex)

            DealsRtn[date] = dailydealsrtn
            DealsStartTime[date] = dailydealsstarttime
            DealsEndTime[date] = dailydealsendtime
            DealsHoldPeriods[date] = dailydealsholdperiods

        result_long = {}
        for date in DealsRtn.keys():
            tmp = pd.DataFrame([DealsRtn[date], DealsStartTime[date], DealsEndTime[date], DealsHoldPeriods[date]]).transpose()
            result_long[date] = tmp

        result_long = pd.concat(result_long)
        result_long.columns=['rtn', 'starttime', 'endtime', 'holdperiods']
        result_long[['rtn','holdperiods']] = result_long[['rtn','holdperiods']].astype(float)


        DealsRtn = {}
        DealsStartTime = {}
        DealsEndTime = {}
        DealsHoldPeriods = {}

        for date in date_list[tslookback+1:]:
            dailydealsrtn = []
            dailydealsstarttime = []
            dailydealsendtime = []
            dailydealsholdperiods = []

            factordaily = mergeinfo.loc[date]
            opentwap = 0
            lastindex = 0

            if factordaily['tsrank'].values[0] <= OpenShort :
                opentwap = factordaily['tradeprice'].values[0]
                lastindex = 0
                dailydealsstarttime.append(factordaily.index[0])

            for i in range(1,len(factordaily)-1):
                if factordaily['tsrank'].values[i] > CloseShort and factordaily['tsrank'].values[i-1] <= CloseShort and len(dailydealsstarttime) != len(dailydealsendtime) :
                    rtn = factordaily['tradeprice'].values[i]/opentwap-1+fee
                    dailydealsrtn.append(rtn)
                    dailydealsendtime.append(factordaily.index[i])
                    dailydealsholdperiods.append(i-lastindex)

                if factordaily['tsrank'].values[i-1] > OpenShort and factordaily['tsrank'].values[i] <= OpenShort and len(dailydealsstarttime) == len(dailydealsendtime) :
                    opentwap = factordaily['tradeprice'].values[i]
                    dailydealsstarttime.append(factordaily.index[i])
                    lastindex=i

            if len(dailydealsstarttime) == len(dailydealsendtime) + 1:
                rtn = factordaily['tradeprice'].values[-1] / opentwap - 1 + fee
                dailydealsrtn.append(rtn)
                dailydealsendtime.append(factordaily.index[-1])
                dailydealsholdperiods.append(237-lastindex)

            DealsRtn[date] = dailydealsrtn
            DealsStartTime[date] = dailydealsstarttime
            DealsEndTime[date] = dailydealsendtime
            DealsHoldPeriods[date] = dailydealsholdperiods

        result_short = {}
        for date in DealsRtn.keys():
            tmp = pd.DataFrame([DealsRtn[date], DealsStartTime[date], DealsEndTime[date], DealsHoldPeriods[date]]).T
            result_short[date] = tmp

        result_short = pd.concat(result_short)
        result_short.columns=['rtn', 'starttime', 'endtime', 'holdperiods']
        result_short[['rtn','holdperiods']] = result_short[['rtn','holdperiods']].astype(float)

        RESULT={}
        RESULT['long'] = result_long
        RESULT['short'] = result_short

        tmp = pd.concat(RESULT)['rtn'].unstack(0)
        DailyDealNum = (~tmp.isnull()).groupby(level=0).sum().mean()
        AvgHoldPeriods = pd.concat(RESULT).unstack(0)['holdperiods'].groupby(level=0).mean().mean()
        SegementDailyReturn = pd.concat(RESULT).unstack(0)['rtn'].fillna(0).groupby(level=0).sum()*100
        Longshort = (SegementDailyReturn['long']-SegementDailyReturn['short'])
        ProfitPerDeal = pd.concat(RESULT)['rtn'].unstack(0).mean()*100

        summary = pd.concat([ProfitPerDeal ,DailyDealNum,AvgHoldPeriods,SegementDailyReturn.mean()],axis=1)
        summary.columns=['ProfitPerDeal (%)', 'DailyDealNum', 'AvgHoldPeriods', 'DailyReturn (%)']
        summary = summary.T

        AutoCorr_1min = mergeinfo['tsrank'].corr(mergeinfo['tsrank'].shift(1))
        AutoCorr_5min = mergeinfo['tsrank'].corr(mergeinfo['tsrank'].shift(5))

        mergeinfo['future_rtn30min'] = pd.concat([mergeinfo['tradeprice'].loc[date].pct_change(30).shift(-30) for date in date_list])
        corr_30min_daily = mergeinfo.dropna()['tsrank'].rolling(237*tslookback).corr(mergeinfo.dropna()['future_rtn30min']).groupby(level=0).mean()
        
        summarydict = {}
        summarydict['LongShortAnualReturn (%)'] =  Longshort.mean()*250
        summarydict['LongShortSR'] = Longshort.mean()/Longshort.std()
        summarydict['ProfitPerDeal (%)'] = (ProfitPerDeal['long'] - ProfitPerDeal['short']) / 2
        summarydict['LongShortMDD'] = (Longshort.cumsum()-Longshort.cumsum().expanding().max()).min()
        summarydict['LongShortWinningRate (%)'] = len(Longshort[Longshort>=0])/len(Longshort) *100
        summarydict['AutoCorr_1Min(ts)'] = AutoCorr_1min
        summarydict['AutoCorr_5Min(ts)'] = AutoCorr_5min
        summarydict['IC_30Min']  = mergeinfo['prediction'].corr(mergeinfo['future_rtn30min'])
        summarydict['IC_30Min(ts)']  = mergeinfo['tsrank'].corr(mergeinfo['future_rtn30min'])
        summarydict['BacktestPeroids'] = len(date_list[tslookback+1:])
        summarydictdf = pd.DataFrame(summarydict, index=['prediction']).T
        
        if show_result:
            SegementDailyReturn.cumsum().plot(title='Daily Profit Segment Curve')
            plt.show()
            ProfitPerDeal.plot(kind='bar', title='Profit Per Deal Segment Curve')
            plt.show()
            print(summary)
            Longshort.cumsum().plot(title='Long Short Curve')
            plt.show()
            corr_30min_daily.cumsum().plot(title='Tsrank 30-Minute Correlation (Cumulative)')
            plt.show()
            print(summarydictdf)

        return RESULT, summarydictdf

    
    def calc_sharpe_perdeal_for_tsfactor_list(self, factor_list, variety, start_date, end_date, groupnum=10):
        res_df = pd.DataFrame(np.nan, index=factor_list, columns=['sharpe', 'perdeal_diff'])
        for f in factor_list:
            factor_df = pd.read_hdf('{}/minute_norm/{}/{}.h5'.format(self.__store_data_path, variety, f))
            _, sharpe, perdeal_diff = self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date, end_date, groupnum)
            res_df.loc[f] = [sharpe, perdeal_diff]
        return res_df


    def get_factor_report(self, factor_df, raw_factor_df, tslookback, author, variety, start_date, end_date, start_date_histSample, end_date_histSample):

        factor_name = factor_df.columns[0]
        with PdfPages('FactorReport_{}_{}_{}.pdf'.format(factor_name, author, variety)) as pdf:
            
            width = 20
            height = 20
            
            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(3, 1, height_ratios = [2,2,1]) 
            
            RESULT, summarydictdf = self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date, end_date, show_result = False)

            tmp = pd.concat(RESULT)['rtn'].unstack(0)
            DailyDealNum = (~tmp.isnull()).groupby(level=0).sum().mean()
            AvgHoldPeriods = pd.concat(RESULT).unstack(0)['holdperiods'].groupby(level=0).mean().mean()
            SegementDailyReturn = pd.concat(RESULT).unstack(0)['rtn'].fillna(0).groupby(level=0).sum()*100
            Longshort = (SegementDailyReturn.iloc[:,-1]-SegementDailyReturn.iloc[:,0])
            pd.DataFrame(Longshort, columns = [factor_name]).to_pickle('{}/{}/{}.pickle'.format(self.__factor_longshort_path, variety, factor_name))
            ProfitPerDeal = pd.concat(RESULT)['rtn'].unstack(0).mean()*100
            
            ax = plt.subplot(grid[0])
            for i in range(len(RESULT)):
                SegementDailyReturn.iloc[:,i].cumsum().plot(label = i + 1)
            plt.legend(fontsize = 15)
            plt.xticks(rotation = 45, fontsize = 12, va = 'bottom')
            plt.yticks(fontsize = 12)
            plt.xlabel('Date', fontsize = 15)
            plt.ylabel('Profit(%)', fontsize = 15)
            plt.title('Daily Profit Segment Curve', fontsize = 20)
            
            ax = plt.subplot(grid[1])
            ProfitPerDeal.plot(kind='bar')
            plt.xticks(fontsize = 12)
            plt.yticks(fontsize = 12)
            plt.xlabel('Segment', fontsize = 15)
            plt.ylabel('Profit Per Deal(%)', fontsize = 15)
            plt.title('Profit Per Deal Segment Curve', fontsize = 20)
            
            summary = pd.concat([ProfitPerDeal, DailyDealNum, AvgHoldPeriods, SegementDailyReturn.mean()], axis=1)
            summary.columns=['ProfitPerDeal (%)', 'DailyDealNum', 'AvgHoldPeriods',' DailyReturn (%)']
            summary = summary.round(4).T 
            ax = plt.subplot(grid[2])
            ax.axis('off')
            table = ax.table(cellText = summary.values, rowLabels = summary.index, 
                             colLabels = summary.columns, bbox = [0.1,0.2,0.9,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * summary.shape[0], colColours = ['skyblue'] * summary.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'Segment Performance'
            ax.text(0.45, 0.24, txt, transform = page.transFigure, size = 20)
            
            txt = 'Factor Report: {}_{}_{}'.format(factor_name, author, variety)
            ax.text(0.25, 0.92, txt, transform = page.transFigure, size = 28)
            
            plt.show()
            pdf.savefig(page)
            plt.close()

            
            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(2, 2) 
            
            ax = plt.subplot(grid[0,:])
            Longshort.cumsum().plot()
            plt.xticks(rotation = 45, fontsize = 12)
            plt.yticks(fontsize = 12)
            plt.xlabel('Date', fontsize = 15)
            plt.ylabel('Profit(%)', fontsize = 15)
            plt.title('Long Short Curve', fontsize = 20)

            float_variable = list(set(summarydictdf.index) - set(['MaxProfitGroup','MinProfitGroup','MaxRecoverTime','DrawdownNum','Pass']))
            summarydictdf.loc[float_variable] = summarydictdf.loc[float_variable].astype(float).round(4)
            longshort_performance = summarydictdf.loc[['LongShortAnualReturn (%)','LongShortSR','ProfitPerDealDiff (%)','MaxProfitGroup','MinProfitGroup','Pass']]
            drawdown_recover = summarydictdf.loc[['MaxDrawdown','MaxRecoverTime','DrawdownNum', 'BounceDrawdownSharpeRatio']]
            longshort_performance.columns = ['LongShort Performance']
            drawdown_recover.columns = ['MaxDrawdown & Recover']
            
            ax = plt.subplot(grid[1,0])
            ax.axis('off')
            table = ax.table(cellText = longshort_performance.values, rowLabels = longshort_performance.index, 
                             colLabels = longshort_performance.columns, bbox = [0.35,0,0.5,0.7], cellLoc = 'center',
                             rowColours = ['skyblue'] * longshort_performance.shape[0], colColours = ['skyblue'] * longshort_performance.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            
            ax = plt.subplot(grid[1,1])
            ax.axis('off')
            table = ax.table(cellText = drawdown_recover.values, rowLabels = drawdown_recover.index, 
                             colLabels = drawdown_recover.columns, bbox = [0.45,0.1,0.5,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * drawdown_recover.shape[0], colColours = ['skyblue'] * drawdown_recover.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            
            txt = 'LongShort Performance'
            ax.text(0.42, 0.4, txt, transform = page.transFigure, size = 20)
            
            plt.show()
            pdf.savefig(page)
            plt.close()
            
                
            ## page ##
            
            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(3, 2)
            
            color_list = ['steelblue','darkorange','green']
            ax = plt.subplot(grid[0,0])
            summarydictdf.loc[['DailyWinRate','LongDailyWinRate','ShortDailyWinRate']].squeeze().plot(kind = 'bar', rot = 0, fontsize = 12, color = color_list)
            plt.xticks([0,1,2],['total','long','short'])
            plt.title('Daily Win Rate', fontsize = 15)
            
            ax = plt.subplot(grid[0,1])
            summarydictdf.loc[['TradeWinRate','LongTradeWinRate','ShortTradeWinRate']].squeeze().plot(kind = 'bar', rot = 0, fontsize = 12, color = color_list)
            plt.xticks([0,1,2],['total','long','short'])
            plt.title('Trade Win Rate', fontsize = 15)
            
            ax = plt.subplot(grid[1,0])
            summarydictdf.loc[['ProfitLossRatio','LongProfitLossRatio','ShortProfitLossRatio']].squeeze().plot(kind = 'bar', rot = 0, fontsize = 12, color = color_list)
            plt.xticks([0,1,2],['total','long','short'])
            plt.title('Profit Loss Ratio', fontsize = 15)
            
            ax = plt.subplot(grid[1,1])
            summarydictdf.loc[['ProfitPerDealDiff (%)','LongProfitPerDeal (%)','ShortProfitPerDeal (%)']].squeeze().plot(kind = 'bar', rot = 0, fontsize = 12, color = color_list)
            plt.xticks([0,1,2],['total','long','short'])
            plt.title('Profit Per Deal (%)', fontsize = 15)
            
            ax = plt.subplot(grid[2,0])
            summarydictdf.loc[['LongShortSR','LongSR','ShortSR']].squeeze().plot(kind = 'bar', rot = 0, fontsize = 12, color = color_list)
            plt.xticks([0,1,2],['total','long','short'])
            plt.title('Sharpe', fontsize = 15)
            
            ax = plt.subplot(grid[2,1])
            summarydictdf.loc[['LongShortSR_2018','LongShortSR_2019','LongShortSR_2020']].squeeze().plot(kind = 'bar', rot = 0, fontsize = 12, color = color_list)
            plt.xticks([0,1,2],['2018','2019','2020'])
            plt.title('Sharpe in Years', fontsize = 15)
            
            plt.show()
            pdf.savefig(page)
            plt.close()
            
            
            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(2, 1) 
            
            tsrank_corr = self.calc_tsrank_max_corr_by_df(factor_df, variety, start_date, end_date)
            tsrank_corr = pd.DataFrame(tsrank_corr, columns = ['max corr']).astype(float).round(4)
            ax = plt.subplot(grid[0])
            ax.axis('off')
            table = ax.table(cellText = tsrank_corr.values, rowLabels = tsrank_corr.index, 
                             colLabels = tsrank_corr.columns, bbox = [0.4,0.3,0.5,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * tsrank_corr.shape[0], colColours = ['skyblue'] * tsrank_corr.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            
            txt = 'Factor Tsrank Correlation'
            ax.text(0.42, 0.88, txt, transform = page.transFigure, size = 20)
            
            longshort_corr = self.calc_longshort_max_corr_by_name(factor_name, variety, start_date, end_date)
            longshort_corr = pd.DataFrame(longshort_corr, columns = ['max corr']).astype(float).round(4)
            ax = plt.subplot(grid[1])
            ax.axis('off')
            table = ax.table(cellText = longshort_corr.values, rowLabels = longshort_corr.index, 
                             colLabels = longshort_corr.columns, bbox = [0.4,0.3,0.5,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * longshort_corr.shape[0], colColours = ['skyblue'] * longshort_corr.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            
            txt = 'Factor LongShort Correlation'
            ax.text(0.42, 0.48, txt, transform = page.transFigure, size = 20)
            
            plt.show()
            pdf.savefig(page)
            plt.close()
            
            
            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(3, 1, height_ratios = [2,2,1]) 
            
            RESULT, summarydictdf = self.calc_statistic_by_factor_tsrank_df(factor_df, variety, start_date_histSample, end_date_histSample, show_result = False, save_longshort = False)

            tmp = pd.concat(RESULT)['rtn'].unstack(0)
            DailyDealNum = (~tmp.isnull()).groupby(level=0).sum().mean()
            AvgHoldPeriods = pd.concat(RESULT).unstack(0)['holdperiods'].groupby(level=0).mean().mean()
            SegementDailyReturn = pd.concat(RESULT).unstack(0)['rtn'].fillna(0).groupby(level=0).sum()*100
            Longshort = (SegementDailyReturn.iloc[:,-1]-SegementDailyReturn.iloc[:,0])
            ProfitPerDeal = pd.concat(RESULT)['rtn'].unstack(0).mean()*100
            
            ax = plt.subplot(grid[0])
            for i in range(len(RESULT)):
                SegementDailyReturn.iloc[:,i].cumsum().plot(label = i + 1)
            plt.legend(fontsize = 15)
            plt.xticks(rotation = 45, fontsize = 12, va = 'bottom')
            plt.yticks(fontsize = 12)
            plt.xlabel('Date', fontsize = 15)
            plt.ylabel('Profit(%)', fontsize = 15)
            plt.title('Daily Profit Segment Curve', fontsize = 20)
            
            ax = plt.subplot(grid[1])
            ProfitPerDeal.plot(kind='bar')
            plt.xticks(fontsize = 12)
            plt.yticks(fontsize = 12)
            plt.xlabel('Segment', fontsize = 15)
            plt.ylabel('Profit Per Deal(%)', fontsize = 15)
            plt.title('Profit Per Deal Segment Curve', fontsize = 20)
            
            summary = pd.concat([ProfitPerDeal, DailyDealNum, AvgHoldPeriods, SegementDailyReturn.mean()], axis=1)
            summary.columns=['ProfitPerDeal (%)', 'DailyDealNum', 'AvgHoldPeriods',' DailyReturn (%)']
            summary = summary.round(4).T 
            ax = plt.subplot(grid[2])
            ax.axis('off')
            table = ax.table(cellText = summary.values, rowLabels = summary.index, 
                             colLabels = summary.columns, bbox = [0.1,0.2,0.9,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * summary.shape[0], colColours = ['skyblue'] * summary.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'Segment Performance'
            ax.text(0.45, 0.24, txt, transform = page.transFigure, size = 20)
            
            txt = 'History Sample Performance'
            ax.text(0.4, 0.92, txt, transform = page.transFigure, size = 24)
            
            plt.show()
            pdf.savefig(page)
            plt.close()
            
                
            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(2, 2) 
            
            ax = plt.subplot(grid[0,:])
            Longshort.cumsum().plot()
            plt.xticks(rotation = 45, fontsize = 12)
            plt.yticks(fontsize = 12)
            plt.xlabel('Date', fontsize = 15)
            plt.ylabel('Profit(%)', fontsize = 15)
            plt.title('Long Short Curve', fontsize = 20)

            float_variable = list(set(summarydictdf.index) - set(['MaxProfitGroup','MinProfitGroup','MaxRecoverTime','DrawdownNum','Pass']))
            summarydictdf.loc[float_variable] = summarydictdf.loc[float_variable].astype(float).round(4)
            longshort_performance = summarydictdf.loc[['LongShortAnualReturn (%)','LongShortSR','ProfitPerDealDiff (%)','MaxProfitGroup','MinProfitGroup','Pass']]
            drawdown_recover = summarydictdf.loc[['MaxDrawdown','MaxRecoverTime','DrawdownNum', 'BounceDrawdownSharpeRatio']]
            longshort_performance.columns = ['LongShort Performance']
            drawdown_recover.columns = ['MaxDrawdown & Recover']
            
            ax = plt.subplot(grid[1,0])
            ax.axis('off')
            table = ax.table(cellText = longshort_performance.values, rowLabels = longshort_performance.index, 
                             colLabels = longshort_performance.columns, bbox = [0.35,0,0.5,0.7], cellLoc = 'center',
                             rowColours = ['skyblue'] * longshort_performance.shape[0], colColours = ['skyblue'] * longshort_performance.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            
            ax = plt.subplot(grid[1,1])
            ax.axis('off')
            table = ax.table(cellText = drawdown_recover.values, rowLabels = drawdown_recover.index, 
                             colLabels = drawdown_recover.columns, bbox = [0.45,0.1,0.5,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * drawdown_recover.shape[0], colColours = ['skyblue'] * drawdown_recover.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            
            txt = 'LongShort Performance'
            ax.text(0.42, 0.4, txt, transform = page.transFigure, size = 20)
            
            plt.show()
            pdf.savefig(page)
            plt.close()
                        
            
            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(3, 1)
            
            sensitivity_summary = self.calc_factor_ts_sensitivity(raw_factor_df, variety, start_date, end_date, tslookback)
            float_variable = list(set(sensitivity_summary.index) - set(['MaxProfitGroup','MinProfitGroup','MaxRecoverTime','DrawdownNum','Pass']))
            sensitivity_summary.loc[float_variable] = sensitivity_summary.loc[float_variable].astype(float).round(4)
            longshort_performance = sensitivity_summary.loc[['LongShortAnualReturn (%)','LongShortSR','ProfitPerDealDiff (%)','MaxProfitGroup','MinProfitGroup','Pass']]
            drawdown_recover = sensitivity_summary.loc[['MaxDrawdown','MaxRecoverTime','DrawdownNum', 'BounceDrawdownSharpeRatio']]
            sharpe_consistency = sensitivity_summary.loc[['LongShortSR_2018','LongShortSR_2019','LongShortSR_2020','LongSR','ShortSR']]
            
            ax = plt.subplot(grid[0])
            ax.axis('off')
            table = ax.table(cellText = longshort_performance.values, rowLabels = longshort_performance.index, 
                             colLabels = longshort_performance.columns, bbox = [0.3,0.2,0.5,0.7], cellLoc = 'center',
                             rowColours = ['skyblue'] * longshort_performance.shape[0], colColours = ['skyblue'] * longshort_performance.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'LongShort Performance'
            ax.text(0.41, 0.87, txt, transform = page.transFigure, size = 20)
            
            ax = plt.subplot(grid[1])
            ax.axis('off')
            table = ax.table(cellText = drawdown_recover.values, rowLabels = drawdown_recover.index, 
                             colLabels = drawdown_recover.columns, bbox = [0.3,0.2,0.5,0.5], cellLoc = 'center',
                             rowColours = ['skyblue'] * drawdown_recover.shape[0], colColours = ['skyblue'] * drawdown_recover.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'MaxDrawdown & Recover'
            ax.text(0.41, 0.56, txt, transform = page.transFigure, size = 20)
            
            ax = plt.subplot(grid[2])
            ax.axis('off')
            table = ax.table(cellText = sharpe_consistency.values, rowLabels = sharpe_consistency.index, 
                             colLabels = sharpe_consistency.columns, bbox = [0.3,0.2,0.5,0.6], cellLoc = 'center',
                             rowColours = ['skyblue'] * sharpe_consistency.shape[0], colColours = ['skyblue'] * sharpe_consistency.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'Sharpe Consistency'
            ax.text(0.41, 0.32, txt, transform = page.transFigure, size = 20)
            txt = 'Tsrank(min) Sensitivity Test'
            ax.text(0.38, 0.92, txt, transform = page.transFigure, size = 24)

            plt.show()
            pdf.savefig(page)
            plt.close()


            ## page ##

            page = plt.figure(figsize=(width,height))
            grid = gridspec.GridSpec(3, 1)

            compare_summary = self.compare_factor_equal_weight_model(factor_df, variety, start_date, end_date)
            compare_summary = compare_summary.astype(float).round(4)
            ax = plt.subplot(grid[0])
            ax.axis('off')
            table = ax.table(cellText = compare_summary.values, rowLabels = compare_summary.index, 
                             colLabels = compare_summary.columns, bbox = [0.35,0.2,0.4,0.4], cellLoc = 'center',
                             rowColours = ['skyblue'] * compare_summary.shape[0], colColours = ['skyblue'] * compare_summary.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'Compare Factor Equal Weight Model in Sample'
            ax.text(0.35, 0.81, txt, transform = page.transFigure, size = 20)
            txt = 'Model Analysis'
            ax.text(0.44, 0.92, txt, transform = page.transFigure, size = 24)
            
            hist_compare_summary = self.compare_factor_equal_weight_model(factor_df, variety, start_date_histSample, end_date_histSample)
            hist_compare_summary = hist_compare_summary.astype(float).round(4)
            ax = plt.subplot(grid[1])
            ax.axis('off')
            table = ax.table(cellText = hist_compare_summary.values, rowLabels = hist_compare_summary.index, 
                             colLabels = hist_compare_summary.columns, bbox = [0.35,0.2,0.4,0.4], cellLoc = 'center',
                             rowColours = ['skyblue'] * hist_compare_summary.shape[0], colColours = ['skyblue'] * hist_compare_summary.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'Compare Factor Equal Weight Model in History Sample'
            ax.text(0.35, 0.54, txt, transform = page.transFigure, size = 20)

            feature_importance_df = self.get_factor_importance_in_xgb(factor_df, variety, start_date, end_date)
            feature_importance_df = feature_importance_df.round(4)
            ax = plt.subplot(grid[2])
            ax.axis('off')
            table = ax.table(cellText = feature_importance_df.values, rowLabels = feature_importance_df.index, 
                             colLabels = feature_importance_df.columns, bbox = [0.2,0.2,0.6,0.5], cellLoc = 'center',
                             rowColours = ['skyblue'] * feature_importance_df.shape[0], colColours = ['skyblue'] * feature_importance_df.shape[1])
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            txt = 'XGBoost Feauture Importance Summary'
            ax.text(0.38, 0.3, txt, transform = page.transFigure, size = 20)
            
            plt.show()
            pdf.savefig(page)
            plt.close()
            
            
            ## page ##

            page, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(width,height))
            ax_list = [ax1, ax2, ax3]
            
            longshort_rank_list = [0,1,2]
            factor_name = factor_df.columns[0]
            factor_longshort = pd.read_pickle('{}/{}/{}.pickle'.format(self.__factor_longshort_path, variety, factor_name))[start_date:end_date]
            factor_longshort_sort = factor_longshort.sort_values(by = factor_name)

            start_date = factor_longshort.index[0]
            end_date = factor_longshort.index[-1]

            close = self.get_close_by_period(variety, start_date, end_date)

            marker_dict = {'OpenLong':'^',
                      'OpenShort':'^',
                      'InvOpenLong':'v',
                      'InvOpenShort':'v'}
            color_dict = {'OpenLong':'red',
                          'OpenShort':'green',
                          'InvOpenLong':'red',
                          'InvOpenShort':'green'}

            for i in longshort_rank_list:
                date = factor_longshort_sort.index.values[i]
                today_return = factor_longshort_sort.values.flatten()[i]
                today_close = close[date]
                today_factor = factor_df[date] 
                
                operation_time_dict = self.get_operation_time(today_factor)

                ax = ax_list[i]
                ax.plot(today_factor.values.flatten(), linewidth = 2, label = 'Factor Tsrank')
                ax_2 = ax.twinx()
                ax_2.plot(today_close.values, color = 'grey', alpha = 0.7, label = 'Index Future')
                for k in operation_time_dict.keys():
                    if operation_time_dict[k]:
                        plt.scatter(operation_time_dict[k], today_close[operation_time_dict[k]].tolist() ,label = k, marker = marker_dict[k], color = color_dict[k], s = 100)

                ax.legend(loc =(0.85,0.9),fontsize = 15)
                ax.set_ylabel('Signal Tsrank', fontsize = 15)
                ax.set_xlabel('Time',fontsize = 15)
                ax.tick_params(labelsize = 12)
                time_idx = np.arange(0,len(today_factor) - 1,30)
                ax.set_xticklabels(time_idx, rotation = 45, fontsize = 12, va = 'bottom')
                ax.grid(axis = 'y')

                ax_2.legend(loc = (0.85,0.55), fontsize = 15)
                ax_2.set_ylabel('Index Future', fontsize = 15)
                ax_2.tick_params(labelsize = 12)

                plt.xticks(time_idx, today_factor.index[time_idx])
                plt.title(date + ':' + str(round(today_return,2)) + '%', fontsize = 15)
                
                
            txt = 'Worst 3 Day Factor Detail'
            plt.text(0.42, 0.9, txt, transform = page.transFigure, size = 20)
                
            plt.show()
            pdf.savefig(page)
            plt.close()

# coding: utf-8

# In[ ]:
import pandas as pd
import numpy as np

class calc_score:
    def __init__(self, label_and_style_df):
        self.return_type = 'label_v2o10d1'
        self.style_list = ['saturn_free_turn', 'saturn_t930_T_o2pre']
        self.label_list = ['value','class']
        df = label_and_style_df.rename(columns = {self.return_type:'value'})
        df['month'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y-%m')[2:]))
        df['year'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y')))
        df['class'] = df['value'] > 0
        self.basic_df = df[['value', 'class', 'month', 'year']+self.style_list]
        self.result_dic = {}
        self.factor_name = None
        
    def get_corr_month(self):
        corr_month_df = pd.DataFrame()
        groupby_month_data = self.basic_df.groupby('month')
        corr_month_df['count'] = groupby_month_data.count()['factor']
        for label in self.label_list:
            corr_month_df[label] = groupby_month_data.apply(lambda x: x['factor'].corr(x[label], method='spearman'))
        self.max_num_one_month = max(
            [groupby_month_data.count()['factor'].max()] + [groupby_month_data.count()[label].max() for label in self.label_list])
        return corr_month_df
    
    def get_corr_sta(self, corr_month):
        sta_df = pd.DataFrame(index=self.label_list)
        sta_df['corr_tot'] = [self.basic_df['factor'].corr(self.basic_df[label], method='spearman') for label in self.label_list]
        sta_df['corr_month_mean'] = [corr_month[label].mean() for label in self.label_list]
        sta_df['corr_month_std'] = [corr_month[label].std() for label in self.label_list]
        sta_df['corr_month_mean_std'] = sta_df['corr_month_mean'] / sta_df['corr_month_std']
        return sta_df.T
    
    def get_double_sort(self, sort_factor_list, data=None, sort_factor_group_num=5, factor_group_num=10, return_data=False):
        result_dic = {}
        for sort_factor in sort_factor_list:
            data = self.basic_df.copy() if (data is None) else data
            data['sort_factor_group'], data['factor_group'] = np.nan, np.nan
            num_each_sort_factor_group = len(data) // sort_factor_group_num
            sort_factor_group_list = []
            for i in range(sort_factor_group_num):
                if i==0:
                    sort_factor_group_list += [i] * (len(data) - (sort_factor_group_num-1) * num_each_sort_factor_group)
                else:
                    sort_factor_group_list += [i] * num_each_sort_factor_group
            data = data.sort_values(by=sort_factor)
            data['sort_factor_group'] = sort_factor_group_list

            after_data = pd.DataFrame()
            for i in range(sort_factor_group_num):
                group_factor_data = data[data['sort_factor_group'] == i].copy()
                num_each_group = len(group_factor_data) // factor_group_num
                group_list = []
                for j in range(factor_group_num):
                    if j ==0:
                        group_list += [j] * (len(group_factor_data) - (factor_group_num - 1) * num_each_group)
                    else:
                        group_list += [j] * num_each_group
                group_factor_data = group_factor_data.sort_values(by='factor')
                group_factor_data['factor_group'] = group_list
                after_data = after_data.append(group_factor_data)
            tmp_result = pd.DataFrame()
            for i in range(sort_factor_group_num):
                for j in range(factor_group_num):
                    tmp_result[(i, j)] = after_data[(after_data['sort_factor_group'] == i) & (after_data['factor_group'] == j)].mean()[self.label_list]
            tmp_result = tmp_result.T.reset_index()
            tmp_result['%s_group'%(sort_factor)] = tmp_result['index'].apply(lambda x: x[0])
            tmp_result['factor_group'] = tmp_result['index'].apply(lambda x: x[1])
            tmp_result = tmp_result.set_index(['%s_group'%(sort_factor), 'factor_group']).drop(['index'], axis=1)
            if return_data:
                result_dic[sort_factor] = after_data.groupby('factor_group').mean()[self.label_list]
            else:
                result_dic[sort_factor] = tmp_result
        return result_dic
    
    def check_score(self, double_group_df, month_df, dir, label_test=['value','class']):
        def cal_reverse_sum(rate_arr):
            index1 = np.argmax(rate_arr)
            index2 = np.argmin(rate_arr)
            if index1 < index2:  # 反向转换为从小到大排序
                rate_arr = np.flipud(rate_arr)
            rate_arr_diff = np.diff(rate_arr)
            return np.abs(np.sum(rate_arr_diff[rate_arr_diff < 0]))

        diff_dic = {'value':{'reverse':[0.6, 0.5], 'diff':[1, 1.5]},
                    'class':{'reverse':[0.6, 0.5], 'diff':[0.13, 0.18]}}
        stability_dic = {'value':[0.05, 0.1],
                         'class':[0.05, 0.1]}
        diff_score = pd.Series([6,3,0], index=['high', 'mid', 'low'])
        s_s = 20 / len(month_df)
        stability_score = pd.Series([s_s, s_s/2, 0, -s_s/2, -s_s], index=['high', 'mid', 'low', 'reverse_mid', 'reverse_high'])

        for label in label_test:
            month_df[label] = month_df[label] * dir[label]
        diff_res_df = pd.DataFrame()
        stability_df = pd.DataFrame(index=month_df.index)
        for label in label_test:
            diff, reverse = [], []
            for i in range(5):
                rate_arr = double_group_df[label].unstack().iloc[i].values
                diff.append(max(rate_arr) - min(rate_arr))
                reverse.append(cal_reverse_sum(rate_arr))
            diff_res_df['%s_diff'%(label)], diff_res_df['%s_reverse'%(label)] = diff, reverse
            diff_res_df['%s_high_reverse'%(label)], diff_res_df['%s_mid_reverse'%(label)] = diff_res_df['%s_diff'%(label)] * diff_dic[label]['reverse'][1], diff_res_df['%s_diff'%(label)] * diff_dic[label]['reverse'][0]
            diff_res_df['%s_standard'%(label)] = 1
            diff_res_df.loc[((diff_res_df['%s_diff'%(label)] > diff_dic[label]['diff'][0]) & (diff_res_df['%s_reverse'%(label)] < diff_res_df['%s_mid_reverse'%(label)])), '%s_standard'%(label)] = 2
            diff_res_df.loc[((diff_res_df['%s_diff'%(label)] > diff_dic[label]['diff'][1]) & (diff_res_df['%s_reverse'%(label)] < diff_res_df['%s_mid_reverse'%(label)])), '%s_standard'%(label)] = 3
            diff_res_df['%s_standard'%(label)] = diff_res_df['%s_standard'%(label)].replace({1:'low', 2:'mid', 3:'high'})

            stability_df['%s_standard'%(label)] = np.nan
            stability_df.loc[month_df[label] >= stability_dic[label][1], '%s_standard'%(label)] = 'high'
            stability_df.loc[(month_df[label] >= stability_dic[label][0]) & (month_df[label] < stability_dic[label][1]), '%s_standard'%(label)] = 'mid'
            stability_df.loc[(month_df[label] > -stability_dic[label][0]) & (month_df[label] < stability_dic[label][0]), '%s_standard' % (label)] = 'low'
            stability_df.loc[(month_df[label] <= -stability_dic[label][0]) & (month_df[label] > -stability_dic[label][1]), '%s_standard' % (label)] = 'reverse_mid'
            stability_df.loc[month_df[label] <= -stability_dic[label][1], '%s_standard' % (label)] = 'reverse_high'
        stability_df['count'] = 1
        sta_df = pd.DataFrame(index=['high', 'mid', 'low', 'reverse_mid', 'reverse_high', 'score'])
        for label in label_test:
            sta_df['%s_diff_score'%(label)] = diff_res_df.groupby('%s_standard'%(label)).count()['%s_diff'%(label)]
            sta_df.loc['score', '%s_diff_score' % (label)] = (sta_df['%s_diff_score'%(label)] * diff_score).sum()
            sta_df['%s_stability_score' % (label)] = stability_df.groupby('%s_standard' % (label)).count()['count']
            sta_df['%s_stability_score' % (label)] = sta_df['%s_stability_score' % (label)].fillna(0)
            sta_df.loc['score', '%s_stability_score' % (label)] = (sta_df['%s_stability_score' % (label)] * stability_score).sum()
        sta_df['tot_score'] = np.nan
        sta_df.loc['score', 'tot_score'] = sta_df.loc['score'].sum()
        return sta_df

    def calc_total_score(self, factor_df):
        self.factor_name = factor_df.columns[0]
        self.basic_df['factor'] = factor_df[self.factor_name]
        self.result_dic['corr_month'] = self.get_corr_month()
        self.result_dic['corr_sta'] = self.get_corr_sta(self.result_dic['corr_month'])
        self.result_dic['double_group_sort'] = self.get_double_sort(sort_factor_list=self.style_list)
        self.result_dic['check_score_res'] = self.check_score(self.result_dic['double_group_sort']['saturn_t930_T_o2pre'].copy(), self.result_dic['corr_month'].copy(), np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
        return self.result_dic['check_score_res'].loc['score', 'tot_score']
    
def calc_qcor(tau, label, factor):
    psi = tau - (factor - factor.quantile(tau) < 0)
    qcov = np.mean(psi * (label - np.mean(label)))
    return qcov / (np.sqrt((tau-tau**2)) * np.std(label))

def calc_xi(label, factor):
    n = len(factor)
    PI = factor.rank(method = 'first')
    fr = label.rank(method = 'max') / n
    gr = label.rank(ascending = False, method = 'max') / n
    fr = fr.iloc[PI.argsort()]
    A1 = (fr.diff().abs().sum()) / (2*n)
    CU = (gr*(1-gr)).mean()
    xi = 1- A1 / CU
    return xi


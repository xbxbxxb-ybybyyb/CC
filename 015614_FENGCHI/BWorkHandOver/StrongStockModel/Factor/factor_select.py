import numpy as np
import pandas as pd
import pickle
import os


def load_pickle(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
    return data


def corr_filter(limit, sample, metrics):
    metrics = np.array(metrics)
    sample = np.abs(np.corrcoef(sample))

    rank = (- metrics).argsort(axis=-1)
    corr = sample[rank[:, None], rank[None, :]]
    corr_triu = np.tril_indices(corr.shape[0])
    corr[corr_triu] = 0.

    corr_pool = corr.max(axis=0) < limit
    _corr_pool_num1 = 0
    _corr_pool_num2 = corr_pool.sum()
    while _corr_pool_num2 > _corr_pool_num1:
        _corr_pool_num1 = _corr_pool_num2
        corr[corr[corr_pool].max(axis=0) >= limit] = 0
        corr_pool = corr.max(axis=0) < limit
        _corr_pool_num2 = corr_pool.sum()

    return rank[corr_pool]


def summary_success(father_dict=None):
    default_father_dict = dict(
        str_eval='3 * ic_all_t + ic_all_dtc + ic_all_c + ic_all_dt',
        str_query='date_invalid_num < 99 & ' \
                  '0.03 < dtc_all_sign < 0.07 & ' \
                  'dtc_all_ret + t_dc_all_ret + tc_d_all_ret + t_c_d_all_ret > 0.003',
        len_pre=20000,
        corr_limit=0.7,
    )

    if father_dict:
        default_father_dict.update(father_dict)

    while True:

        level0 = '/data/group/800319/junkBigFactorPool/level0_unfinished/fail/'
        factors = os.listdir(level0)

        name = []
        program_code = []
        date_invalid_num = []
        dtc_all_sign = []
        ic_all_dtc = []
        ic_all_dt = []
        ic_all_c = []
        ic_all_d = []
        ic_all_t = []
        dtc_all_ret = []
        t_dc_all_ret = []
        tc_d_all_ret = []
        t_c_d_all_ret = []
        program_manual = []

        for factor in factors:
            dic = load_pickle(level0 + factor)
            if not dic['program_complex']:
                name.append(factor)
                program_code.append(dic['program_code'])
                date_invalid_num.append(dic['date_invalid_num'])
                dtc_all_sign.append(dic['dtc_all_sign'])
                ic_all_dtc.append(dic['ic_all_dtc'])
                ic_all_dt.append(dic['ic_all_dt'])
                ic_all_c.append(dic['ic_all_c'])
                ic_all_d.append(dic['ic_all_d'])
                ic_all_t.append(dic['ic_all_t'])
                dtc_all_ret.append(dic['dtc_all_ret'])
                t_dc_all_ret.append(dic['t_dc_all_ret'])
                tc_d_all_ret.append(dic['tc_d_all_ret'])
                t_c_d_all_ret.append(dic['t_c_d_all_ret'])
                program_manual.append(dic['program_manual'] if 'program_manual' in dic else None)

        df = pd.DataFrame({
            'name': name,
            'program_code': program_code,
            'program_manual': program_manual,
            'date_invalid_num': date_invalid_num,
            'dtc_all_sign': dtc_all_sign,
            'ic_all_dtc': ic_all_dtc,
            'ic_all_dt': ic_all_dt,
            'ic_all_c': ic_all_c,
            'ic_all_d': ic_all_d,
            'ic_all_t': ic_all_t,
            'dtc_all_ret': dtc_all_ret,
            't_dc_all_ret': t_dc_all_ret,
            'tc_d_all_ret': tc_d_all_ret,
            't_c_d_all_ret': t_c_d_all_ret,
        })

        df = df.drop_duplicates(['program_code'])

        df.eval('score = %s' % default_father_dict['str_eval'], inplace=True)
        df.sort_values('score', ascending=False, inplace=True)
        df = df.query(default_father_dict['str_query'])
        df = df.head(default_father_dict['len_pre'])

        ic_all_dt_every_code = []
        for factor in df['name']:
            dic = load_pickle(level0 + factor)
            ic_all_dt_every_code.append(dic['ic_all_dt_every_code'])
        ic_all_dt_every_code = np.asanyarray(ic_all_dt_every_code)

        df = df.iloc[corr_filter(default_father_dict['corr_limit'], ic_all_dt_every_code, df['score'])]
        return df


def get_selected_feature(indicator):
    # father_dict_all = dict(
    #         str_eval=indicator,
    #         str_query='date_invalid_num < 99 & ' \
    #                   '0.03 < dtc_all_sign < 0.07 & ' \
    #                   'dtc_all_ret + t_dc_all_ret + tc_d_all_ret + t_c_d_all_ret > 0.003',
    #         len_pre=2000,
    #         corr_limit=0.7,
    #     )
    indicator = 'abs(%s)' % indicator
    father_dict_manual = dict(
        str_eval=indicator,
        str_query='date_invalid_num < 99 & ' \
                  '0.03 < dtc_all_sign < 0.07 & ' \
                  'dtc_all_ret + t_dc_all_ret + tc_d_all_ret + t_c_d_all_ret > 0.003 & program_manual==True',
        len_pre=2000,
        corr_limit=0.7,
    )

    father_dict_algo = dict(
        str_eval=indicator,
        str_query='date_invalid_num < 99 & ' \
                  '0.03 < dtc_all_sign < 0.07 & ' \
                  'dtc_all_ret + t_dc_all_ret + tc_d_all_ret + t_c_d_all_ret > 0.003 & program_manual==False',
        len_pre=2000,
        corr_limit=0.7,
    )
    # df_all = summary_success(father_dict=father_dict_all)
    df_manual = summary_success(father_dict=father_dict_manual)
    df_algo = summary_success(father_dict=father_dict_algo)
    union_list = list(set(df_algo['name']).union(set(df_manual['name'])))

    dict_merge = dict(
        str_eval=indicator,
        str_query='date_invalid_num < 99 & ' \
                  '0.03 < dtc_all_sign < 0.07 & ' \
                  'dtc_all_ret + t_dc_all_ret + tc_d_all_ret + t_c_d_all_ret > 0.003 & name in ' + str(union_list),
        len_pre=2000,
        corr_limit=0.7,
    )

    df_merge = summary_success(father_dict=dict_merge)

    selected_factor = dict(
        pure_algo=df_algo[df_algo['name'].isin(list(set(df_merge['name']).intersection(set(df_algo['name']))))].sort_values('score', ascending=False)['name'].tolist()[:100],
        pure_manual=df_manual[df_manual['name'].isin(list(set(df_merge['name']).intersection(set(df_manual['name']))))].sort_values('score', ascending=False)['name'].tolist()[
                    :100],
    )
    selected_factor['mix'] = selected_factor['pure_algo'][:50] + selected_factor['pure_manual'][:50]
    selected_factor['all'] = selected_factor['pure_manual'] + selected_factor['pure_algo']
    return selected_factor, df_algo, df_manual, df_merge


factor_selection_path = '/data/group/800319/FactorSelection/'

res_dict = {}
union_set = set()
for ind in ['ic_all_d', 'ic_all_c', 'ic_all_t']:
    res_dict[ind] = get_selected_feature(ind)
    pd.to_pickle(res_dict[ind], factor_selection_path + 'strategy001/%s.pkl' % ind)
    union_set = union_set.union(set(res_dict[ind][0]['all']))
    print(ind)

pd.to_pickle(list(union_set), '/data/group/800319/FactorSelection/strategy001/calc_factor.pkl')

from xquant.xqutils.helper import link

lm = link.LinkMessage()
lm.sendMessage("因子筛选完成!" + ' /data/group/800319/FactorSelection/strategy001/calc_factor.pkl')
lm.sendMessage(str(list(union_set)))
# "Info: 铃客消息发送成功！"

import pandas as pd

selected_factor, df_algo, df_manual, df_merge = pd.read_pickle('/data/group/800319/FactorSelection/strategy001/ic_all_d.pkl')

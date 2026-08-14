import sys
sys.path.append('/data/group/800442/800319')
from dataApi.tradeDate import *
from dataApi.getData import *
from dataApi.stockList import *
from LimitUpPredStrategy.TickDataPrepare2 import TickDataPrepare,open_ticks,trade_ticks,trade_items
from LimitUpPredStrategy.Factor.FactorTest import FactorTest
import pandas as pd
import numpy as np
import random
import os
import bottleneck
from gplearn import genetic
from gplearn.functions import make_function
from gplearn.genetic import SymbolicTransformer, SymbolicRegressor
from gplearn.fitness import make_fitness
from datetime import datetime
import requests
import json
root_path = '/data/group/800442/800319/'
proj_root_path = root_path + 'Afengchi/LimitUpPredStrategy/'
proj_root_path2 = root_path + 'LimitUpStrategy/'

factor_path = root_path + 'ZTfactors/'
limit_pool_file = root_path + 'LimitTickData2/HighFreqData/LimitPool.npy'

label_path = proj_root_path + 'label/'
samples_path = proj_root_path + 'samples/'

# 股票池
filterd_tick_pool_file_path = proj_root_path2 + 'FilteredTick.pkl'
strategy_pool_file_path = proj_root_path2 + 'StrategyPool.h5'

def send_message(users, msg):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)
def send_file(users, file):
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.7.124.15:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']

    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)
self = FactorTest(start_date=20140101,
                      backtest_start_date=20140701, end_date=20191231,
                      stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl')

def _abss(x):
    return np.abs(x)

# def _sign(x):
#     return np.sign(x)

def _sqrt(x):
    return np.sqrt(np.abs(x)) * np.sign(x)

def _square(x):
    return x ** 2

def _cube(x):
    return x ** 3

def _neg(x):
    return -x

def _exp(x):
    return np.exp(x) - 1

def _sigmoid(x):
    return 1 / (1 + np.exp(-x))

# def _ds_cumsum(x):
#     return np.nancumsum(x,axis=0)
#
# def _ds_mean(x):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     return bottleneck.move_mean(x, d3, axis=0)
#
# def _ds_median(x):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     return bottleneck.move_median(x, d3, axis=0)
#
# def _ds_min(x):
#     d = [3,5,10,15,20]
#     d4 = random.choice(d)
#     return bottleneck.move_min(x, d4, axis=0)
#
# def _ds_max(x):
#     d = [3,5,10,15,20]
#     d4 = random.choice(d)
#     return bottleneck.move_max(x, d4, axis=0)
#
# def _ds_argmax(x):
#     d = [3,5,10,15,20]
#     d4 = random.choice(d)
#     return bottleneck.move_argmax(x, d4, axis=0) / (d4 - 1)
#
# def _ds_argmin(x, d4):
#     d = [3,5,10,15,20]
#     d4 = random.choice(d)
#     return bottleneck.move_argmin(x, d4, axis=0) / (d4 - 1)
#
# def _ds_rank(x):
#     d = [3,5,10,15,20]
#     d4 = random.choice(d)
#     return (bottleneck.move_rank(x, d4, axis=0) + 1) / 2
#
# def _ds_std(x):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     return bottleneck.move_std(x, d3, axis=0)
#
# def _ds_skew(x):
#     d = [1,2,3,5,10,15,20]
#     d3 = random.choice(d)
#     d3 = 3 if d3 < 3 else d3
#     x = x - bottleneck.move_mean(x, d3, axis=0)
#     const = (d3 - 1) ** (1 / 2) * d3 ** (1 / 6) / (d3 - 2)
#     skew = const * bottleneck.move_sum(x ** 3, d3, axis=0) / (
#         bottleneck.move_sum(x ** 2, d3, axis=0)) ** 1.5
#     return skew
#
# def _ds_kurt(x):
#     d = [1,2,3,4,5,10,15,20]
#     d4 = random.choice(d)
#     d4 = 4 if d4 < 4 else d4
#     x = x - bottleneck.move_mean(x, d4, axis=0)
#     const1 = (d4 + 1) * d4 * (d4 - 1) / (d4 - 2) / (d4 - 3)
#     const2 = 3 * (d4 - 1) ** 2 / (d4 - 2) / (d4 - 3)
#     kurt = const1 * bottleneck.move_sum(x ** 4, d4, axis=0) / (
#         bottleneck.move_sum(x ** 2, d4, axis=0)) ** 2 - const2
#     return kurt
#
# def _ts_cumsum(x):
#     return np.nancumsum(x, axis=0)
#
# def _ts_cummax(x):
#     return np.maximum.accumulate(x, axis=0)
#
# def _ts_cummin(x):
#     return np.minimum.accumulate(x, axis=0)
#
# def _add2(x, y, w):
#     return w * x + (1 - w) * y
#
# def _ds_corr2(x, y):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     cx = bottleneck.move_mean(x, d3, axis=0)
#     cy = bottleneck.move_mean(y, d3, axis=0)
#     cx2 = bottleneck.move_mean(x ** 2, d3, axis=0)
#     cy2 = bottleneck.move_mean(y ** 2, d3, axis=0)
#     cxy = bottleneck.move_mean(x * y, d3, axis=0)
#     return (d3 * cxy - cx * cy) / np.sqrt((d3 * cx2 - cx ** 2) * (d3 * cy2 - cy ** 2))
#
# def _ds_beta2(x, y):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     cx = bottleneck.move_mean(x, d3, axis=0)
#     cy = bottleneck.move_mean(y, d3, axis=0)
#     cx2 = bottleneck.move_mean(x ** 2, d3, axis=0)
#     cxy = bottleneck.move_mean(x * y, d3, axis=0)
#     return (d3 * cxy - cx * cy) / (d3 * cx2 - cx ** 2)
#
# def _ds_resid2(x, y):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     beta = _ds_beta2(x, y, d3)
#     alpha = _ds_mean(y, d3) - _ds_mean(x, d3) * beta
#     return y - alpha - x * beta
#
# def _ds_intercept2(x, y):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     return _ds_mean(y, d3) - _ds_mean(x, d3) * _ds_beta2(x, y, d3)
#
# def _ds_alpha2(x, y):
#     d = [3,5,10,15,20]
#     d3 = random.choice(d)
#     return y - x * _ds_beta2(x, y, d3)

# def _relu(x):
#     return np.where(x > 0, x, 0)

def _max2(x, y):
    return np.fmax(x, y)

def _min2(x, y):
    return np.fmin(x, y)

def _deviation2(x, y):
    return np.where(x + y != 0, (x - y) / (x + y), 0)

# def _sign_mul2(x, y):
#     return _sign(x) * y

def _mul2(x, y):
    return x * y

def _sum2(x, y):
    return x + y

def _sub2(x, y):
    return x - y

def _abs_sub2(x, y):
    return _abss(_sub2(x, y))

def _percent2(x, y):
    return (x - y) / _abss(y)

def _pn_condition2(x, y):
    return np.where(x > 0, y, -y)

# def _zero_condition2(x, y):
#     return np.where(x > 0, y, 0)


abss = make_function(function=_abss, name='abss', arity=1)
#sign = make_function(function=_sign, name='sign', arity=1)
sqrt = make_function(function=_sqrt, name='sqrt', arity=1)
cube = make_function(function=_cube, name='cube', arity=1)
neg = make_function(function=_neg, name='neg', arity=1)
exp = make_function(function=_exp, name='exp', arity=1)
sigmoid = make_function(function=_sigmoid, name='sigmoid', arity=1)
# ds_cumsum = make_function(function=_ds_cumsum, name='ds_cumsum', arity=1)
# ds_mean = make_function(function=_ds_mean, name='ds_mean', arity=1)
# ds_median = make_function(function=_ds_median, name='ds_median', arity=1)
# ds_min = make_function(function=_ds_min, name='ds_min', arity=1)
# ds_max = make_function(function=_ds_max, name='ds_max', arity=1)
# ds_argmax = make_function(function=_ds_argmax, name='ds_argmax', arity=1)
# ds_argmin = make_function(function=_ds_argmin, name='ds_argmin', arity=1)
# ds_rank = make_function(function=_ds_rank, name='ds_rank', arity=1)
# ds_std = make_function(function=_ds_std, name='ds_std', arity=1)
# ds_skew = make_function(function=_ds_skew, name='ds_skew', arity=1)
# ds_kurt = make_function(function=_ds_kurt, name='ds_kurt', arity=1)
# ts_cumsum = make_function(function=_ts_cumsum, name='ts_cumsum', arity=1)
# ts_cummax = make_function(function=_ts_cummax, name='ts_cummax', arity=1)
# ts_cummin = make_function(function=_ts_cummin, name='ts_cummin', arity=1)
# add2 = make_function(function=_add2, name='add2', arity=1)
# ds_corr2 = make_function(function=_ds_corr2, name='ds_corr2', arity=2)
# ds_beta2 = make_function(function=_ds_beta2, name='ds_beta2', arity=2)
# ds_resid2 = make_function(function=_ds_resid2, name='ds_resid2', arity=2)
# ds_intercept2 = make_function(function=_ds_intercept2, name='ds_intercept2', arity=2)
# ds_alpha2 = make_function(function=_ds_alpha2, name='ds_alpha2', arity=2)
#relu = make_function(function=_relu, name='relu', arity=1)
max2 = make_function(function=_max2, name='max2', arity=2)
min2 = make_function(function=_min2, name='min2', arity=2)
deviation2 = make_function(function=_deviation2, name='deviation2', arity=2)
#sign_mul2 = make_function(function=_sign_mul2, name='sign_mul2', arity=2)
mul2 = make_function(function=_mul2, name='mul2', arity=2)
sum2 = make_function(function=_sum2, name='sum2', arity=2)
sub2 = make_function(function=_sub2, name='sub2', arity=2)
abs_sub2 = make_function(function=_abs_sub2, name='abs_sub2', arity=2)
percent2 = make_function(function=_percent2, name='percent2', arity=2)
pn_condition2 = make_function(function=_pn_condition2, name='pn_condition2', arity=2)
#zero_condition2 = make_function(function=_zero_condition2, name='zero_condition2', arity=2)

function_set = [abss, sqrt, cube, neg, exp, sigmoid,max2,min2,deviation2,mul2,sum2,sub2,abs_sub2,percent2,
                pn_condition2]


all_factors = pd.read_pickle(samples_path+'original.pkl')
fields = all_factors.columns.tolist()
label = pd.read_pickle(label_path + 'reg_次日开盘溢价' + '.pkl')
label = label.reindex(index=all_factors.index)
X_dict = {}
for i in range(0,len(fields)):
    X_dict['X'+str(i)] = fields[i]
n = 300
m = 1
dp = TickDataPrepare() # 实例化类
def read_basic_factor(name):
    return dp.get_data_by_date_list(item=name,  # Tick字段名, 支持的字段见tick_items列表，
                             # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                             start_date=20140101,
                             end_date=20210228,
                             date_list=None,  # 若传列表则忽略start_date和end_date参数
                             start_tick=91500,  # 默认为91500
                             end_tick=150000,  # 默认为150000
                             tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                             return_idx=True  # True返回DataFrame, False返回2darray
                             )
factor_wrong = {}
factor_success = {}
factor_untest = {}
LimitPool = read_basic_factor('LimitPool')
stock_pool_stack = LimitPool[LimitPool].stack()
number = 1
success_n = 0
for i in range(n):
    result = pd.DataFrame()
    for j in range(m):
        population_size = 3000
        generations = 6
        random_state=None
        est_gp = SymbolicTransformer(
                                    function_set=function_set,
                                    generations=generations,
                                    metric='spearman',#'spearman'秩相关系数
                                    population_size=population_size,
                                    tournament_size=40,
                                    random_state=random_state,
                                    verbose=2,
                                    parsimony_coefficient=0.0001,
                                    p_crossover = 0.4,
                                    p_subtree_mutation = 0.01,
                                    p_hoist_mutation = 0,
                                    p_point_mutation = 0.01,
                                    p_point_replace = 0.4,
                                    n_jobs = 16
                                 )
        est_gp.fit(all_factors,label)
        best_programs = est_gp._best_programs
        best_programs_dict = {}
        for p in best_programs:
            factor_name = 'alpha_' + str(best_programs.index(p) + 1)
            p_str = str(p)
            p_node = p.program
            p_node = [x for x in p_node if type(x) is int]
            p_node.sort(reverse=True)
            for aaaaa in p_node:
                old = 'X'+str(aaaaa)
                p_str = p_str.replace(old,X_dict[old])
            best_programs_dict[factor_name] = {'fitness': p.fitness_, 'expression':p_str, 'depth': p.depth_,
                                                   'length': p.length_}

        best_programs_dict = pd.DataFrame(best_programs_dict).T
        best_programs_dict = best_programs_dict.sort_values(by='fitness').drop_duplicates(['expression'])
        best_programs_dict = best_programs_dict[best_programs_dict['length']<=18]
        result = pd.concat([result, best_programs_dict])
    timenow = datetime.today()
    today = timenow.year*10000+timenow.month*100+timenow.day
    result.to_excel('/data/user/015630/factors/ZTfactors/factorexcel/挖掘因子%s_%s.xlsx'%(today,i))
    #send_file(['015630'],'/data/user/015630/factors/ZTfactors/factorexcel/挖掘因子%s_%s.xlsx'%(today,i))

    num = len(result)
    result_ = result.reset_index()

    # 以上条件不变时，因子回测可多次连续进行

    for k in range(1,num+1):
        try:
            expression = result_.at[k-1,'expression']
            print(k, expression)
            factor_list = []
            for it in trade_items:
                if it in expression:
                    factor_list.append(it)
            for name in factor_list:
                exec('%s = read_basic_factor(\'%s\')' % (name, name))
                exec('%s = %s[LimitPool].stack()' % (name, name))
                exec('%s = %s.reindex(stock_pool_stack.index)' % (name, name))
            exec('factor = %s'%expression)
            exec('factor = pd.Series(factor,index=stock_pool_stack.index)')
            length = 1697874
            if len(factor)==length:
                path = '/data/group/800442/800319/ZTfactors/Untested/zxfalgo_%s_%s.pkl' % (today, number)
                exec('factor.to_pickle(\'%s\')'% path)
                factor_untest['zxfalgo_%s_%s.pkl'%(today,number)] = expression
                ft = self.factor_test('zxfalgo_%s_%s' % (today, number),expression,success_n)
                if ft is True:
                    send_message(['015630'],'第%s个表达式%s成功'%(number,expression))
                    factor_success['zxfalgo_%s_%s.pkl'%(today,number)] = expression
                    success_n = success_n+1
                number+=1
            else:
                factor_wrong[number]=expression
                print(number,expression,'something wrong happened in the expression,length must equal to %s'%length)
        except:
            print('生成%s表达式错误'% expression)

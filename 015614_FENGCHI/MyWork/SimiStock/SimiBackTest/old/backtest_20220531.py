# coding: utf-8

import numpy as np
import pandas as pd
from SimiStock.SimiBackTest.FunctionApi import *
from SimiStock.dataApi import getData, stockList, indName
import datetime, time
from tqdm import tqdm
from multiprocessing import Pool
from sklearn.linear_model import Lasso, LassoCV
from sklearn.metrics import r2_score  # R square
from sklearn.decomposition import PCA  # 降维
from scipy.optimize import minimize, leastsq  # 优化算法
from cvxopt import matrix, solvers  # 优化算法

solvers.options['show_progress'] = False
# 函数1：多进程启动
def multiprocess(kernal_num, func, iterable, *args):
    pool = Pool(kernal_num)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // kernal_num
    remainder = len(iterable) % kernal_num
    iter_start = 0
    for j in range(kernal_num):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder = remainder - 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args)
        iter_start = iter_end
    pool.close()
    pool.join()
    print('多进程结束')
    return pool_apply_async
# 函数2：计算多空组合的跟踪误差
def cal_trade_result(df):
    trade = (1 + df).cumprod()
    error = abs((trade-1).iloc[-10:-1]).mean()
    #error = (trade-1).iloc[-1]
    if type(trade) == pd.core.frame.DataFrame:
        maxerror = pd.concat([trade.max() - 1,1 - trade.min()],axis=0).max(level=0)
    else:
        maxerror = max(trade.max() - 1, 1 - trade.min())  # get_maxdown(first_history_trade)
    return error, maxerror
def cal_history_trade_result(df):
    trade = df.cumsum()
    error = abs((trade).iloc[-10:-1]).mean()
    #error = (trade-1).iloc[-1]
    if type(trade) == pd.core.frame.DataFrame:
        maxerror = pd.concat([trade.max() - 1,1 - trade.min()],axis=0).max(level=0)
    else:
        maxerror = abs(trade).max()  # get_maxdown(first_history_trade)
    return error, maxerror
def cal_future_trade_result(df):
    trade = df.cumsum()
    error = trade.iloc[-10:-1].mean()
    if type(trade) == pd.core.frame.DataFrame:
        maxerror = pd.concat([trade.max() - 1,1 - trade.min()],axis=0).max(level=0)
    else:
        maxerror = abs(trade).max()  # get_maxdown(first_history_trade)
    return error, maxerror

# 进行主成分分解
def cal_PCA(data_df):
    if len(data_df.columns) == 1:
        pca_para = pd.DataFrame(1, index=data_df.columns, columns=data_df.columns)

        return pca_para, data_df
    else:
        pca = PCA(n_components=0.95)
        pca.fit(data_df)
        pca_para = pd.DataFrame(pca.components_, index=['feature' + str(i) for i in range(0, pca.n_components_)],
                                columns=data_df.columns)
        pca_data = pca_para.dot(data_df.T).T
        return pca_para, pca_data
# OLS法：误差函数
def error(p, x, y):
    return (p * x).sum(axis=1) - y  # x、y都是列表，故返回值也是个列表
# OLS法：累计版每日累计跟踪误差（即保证绝对一致性：该公式比较完美）
def error1(p, x, y):
    # return  (((p * x).sum(axis=1) - y)+1).cumprod()-1  # x、y都是列表，故返回值也是个列表
    return (abs((p * x).sum(axis=1) - y) + abs((((p * x).sum(axis=1) - y) + 1).cumprod() - 1)) / 2
# 特定周期的重复数量
def cal_trade_time(df, days=20):
    begin_date, over_date = df['date'].min(), df['date'].max()
    date_list = get_date_list(begin_date, over_date)
    code_count = pd.DataFrame(columns=['num'])
    for i in range(0, len(date_list), days):
        first_date = date_list[i]
        last_date = date_list[min(i + days, len(date_list) - 1)]
        code_count.loc[first_date, 'num'] = len(set(df[df['date'] >= first_date][df['date'] < last_date]['code']))

    return code_count['num'].sum()
# 时间窗口
def get_trade_days(date,trade_days,delay,type):
    if type == 'history':
        if delay>0:
            return get_date_list(20130101,date)[-trade_days-delay:-delay]
        else:
            return get_date_list(20130101, date)[-trade_days - delay:]
    if type == 'future':
        now_date = int(datetime.datetime.now().strftime('%Y%m%d'))  # 获取今天日期
        return get_date_list(date,now_date)[delay:trade_days+delay]

# 权重配置优化
class WeightedConfiguration(object):
    def __init__(self, start_date, end_date, before_days=120, after_days=120,
                 read_path='/data/group/800442/800319/Afengchi/SimiStock/hedge_txTest/',
                 save_path='/data/group/800442/800319/Afengchi/SimiStock/OptimalResult/'):
        self.start_date, self.end_date = get_date_list(start_date, end_date)[0], get_date_list(start_date, end_date)[-1]
        date_list = get_date_list(start_date, end_date)
        self.date_list = date_list
        self.before_days, self.after_days = before_days, after_days
        self.read_path, self.save_path = read_path, save_path
        # 个股日频数据
        stock_pool = stockList.clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=60, least_normal_days=0,
                                                no_pause=True,
                                                least_recover_days=1, no_pause_limit=0.5, no_pause_stats_days=120)

        pre_close = getData.get_daily_1factor('pre_close')
        # open = getData.get_daily_1factor('open_badj')
        # close = getData.get_daily_1factor('close_badj')
        # high = getData.get_daily_1factor('high_badj')
        # low = getData.get_daily_1factor('low_badj')
        pct_chg = getData.get_daily_1factor('pct_chg')[stock_pool]

        # self.open, self.close, self.high, self.low = open, close, high, low
        self.pre_close, self.pct_chg = pre_close, pct_chg
    ########################### 一些可选参数的优化 #################################

    ########################### 优化第一步：基于稳定性对相关标的进行筛选 #############################
    def stock_select(self, dict_data):
        date, Original_code, similarity_list, corr_list = dict_data['date'], dict_data['stk_id'], \
                                                          dict_data['hedge_list'], dict_data['hedge_value']
        # 先对于所有的个股，判断其相关系数的稳定性：即只关注稳定
        pass

    ########################### 优化第二步：进行权重配置 ############################################
    # 优化方法1：曲线拟合算法：最小二乘法-由于自变量之间存在多重共线性，所以单纯使用OLS回归会造成误差增加得情况
    # 不同的组合：（1）损失函数使用error还是sumerror （2）是否先进行主成分分析 （3）是否配平   （4）训练周期
    def CurveFitting_LeastSquares(self, dict_data, func='error', pca=False, same_weight=False, before_days=120):
        # 1、先把基础数据拿出来
        date, Original_code, similarity_list = dict_data['date'], dict_data['stk_id'], dict_data['hedge_list']

        # 筛选条件1：测试周期before_weight：会剔除停牌的日期
        trade_range = get_trade_days(date, trade_days=before_days, delay=1, type='history')
        trade_days = list(self.pct_chg.loc[trade_range, Original_code].dropna().index)  # 交易日期
        # 筛选条件2：使用的函数：目前只有两个，日收益率误差，累计收益率误差的平方和
        if func == 'error':  # 即使用误差的平方和
            def cal_error(p, paras):
                x, y = paras[0],paras[1]
                return (((p * x).sum(axis=1) - y)**2).sum()
        elif func == 'sumerror':
            def cal_error(p, x, y):
                return ((((p * x).sum(axis=1) - y+1).cumprod()-1)**2).sum()
        # 筛选条件3：是否使用正则化
        cons = ()
        y = self.pct_chg.loc[trade_days, Original_code] / 100  # 获取原始原始股票的日均收益率（原始样本）
        if pca == True:
            pca_para, x = cal_PCA(self.pct_chg.loc[trade_days, similarity_list].fillna(0) / 100)
            # 筛选条件4：是否限定权重多空比例必须相同
            if same_weight == True:
                def total_weight(w):
                    return (w * pca_para.T).sum(axis=1).sum() - 1
                def long_only(w):
                    return (w * pca_para.T).sum(axis=1)

                cons = ({'type': 'eq', 'fun': total_weight}, {'type': 'ineq', 'fun': long_only})
        else:
            x = self.pct_chg.loc[trade_days, similarity_list].fillna(0) / 100
            # 筛选条件4：是否限定权重多空比例必须相同
            if same_weight == True:
                def total_weight(w):
                    return w.sum() - 1
                def long_only(w):
                    return w

                cons = ({'type': 'eq', 'fun': total_weight},{ 'type': 'ineq', 'fun': long_only})
        # 开始计算结果
        w0 = [1 / len(x.columns) for i in x.columns]
        res = minimize(cal_error, w0, args=[x, y], method='SLSQP', constraints=cons)['x']
        para = -pd.Series(res, index=x.columns)
        para = round(para,4)[round(para,4)!=0]

        if pca == True:
            para = (para * pca_para.T).sum(axis=1)

        return para

    def Adjusted_Curve(self,dict_data, func='error', pca=False, same_weight=False, before_days=120):
        # 1、先把基础数据拿出来
        date, Original_code, similarity_list = dict_data['date'], dict_data['stk_id'], dict_data['hedge_list']
        # 获取测试周期before_weight：会剔除停牌的日期
        trade_range = get_trade_days(date, trade_days=before_days, delay=1, type='history')
        trade_days = list(self.pct_chg.loc[trade_range, Original_code].dropna().index)  # 交易日期
        y = self.pct_chg.loc[trade_days, Original_code] / 100  # y，大宗标的取值
        x = self.pct_chg.loc[trade_days, similarity_list] / 100  # y，大宗标的取值
        # 开始进行循环筛选
        useful_code = []
        adjusted_R2 = 0
        test_code = similarity_list.copy()
        # 先确定使用多少个股
        while len(test_code)>0:
            test_result = pd.DataFrame(index=test_code, columns=['adjusted_R2'])
            for i in test_code:
                step_code = list(set(useful_code).union([i]))
                test_dict_data = {'date':date,'stk_id':similarity_list,'hedge_list':step_code}
                para = self.CurveFitting_LeastSquares(test_dict_data, func, pca, same_weight, before_days)
                y_predict = (para * x).sum(axis=1)
                test_y = pd.Series(0,index=y_predict.index)
                R2 = r2_score(test_y, y_predict)
                new_adjusted_R2 = 1 - ((1 - R2) * (len(y) - 1)) / (len(y) - len(step_code) - 1)
                test_result.loc[i, 'adjusted_R2'] = new_adjusted_R2

                choice_code = test_result.sort_values(by='adjusted_R2', ascending=False).index[0]
                if adjusted_R2 < test_result['adjusted_R2'].max():
                    useful_code.append(choice_code)
                    adjusted_R2 = test_result['adjusted_R2'].max()
                    test_code.remove(choice_code)
                else:
                    break

            # 再确定权重
            if len(useful_code) > 0:
                test_dict_data = {'date': date, 'stk_id': similarity_list, 'hedge_list': useful_code}
                para = self.CurveFitting_LeastSquares(test_dict_data, func, pca, same_weight, before_days)
            else:
                para = pd.Series(index=useful_code)

        return para

    # 优化算法2：资产配置算法：均值-方差模型
    def AssetAllocation_MeanVariance(self, dict_data, func='error', pca=False, same_weight=False, before_days=120):
        # 1、先把基础数据拿出来
        date, Original_code, similarity_list = dict_data['date'], dict_data['stk_id'], dict_data['hedge_list']

        # 筛选条件1：测试周期before_weight：会剔除停牌的日期
        trade_range = get_trade_days(date, trade_days=before_days, delay=1, type='history')
        trade_days = list(self.pct_chg.loc[trade_range, Original_code].dropna().index)  # 交易日期

        # 筛选条件2：是否使用正则化
        y = self.pct_chg.loc[trade_days, Original_code] / 100  # 获取原始原始股票的日均收益率（原始样本）
        x = self.pct_chg.loc[trade_days, similarity_list].fillna(0) / 100
        if pca == True:
            pca_para, x = cal_PCA(self.pct_chg.loc[trade_days, similarity_list].fillna(0) / 100)
        # 筛选条件3：使用每日收益误差，还是使用累计跟踪误差
        if func == 'sumerror':
            x = x.cumsum()
            y = y.cumsum()
        # 开始计算：求解二次规划问题
        pct_data = pd.concat([x, y], axis=1)
        means, covs = pct_data.mean(), pct_data.cov()
        code_list = pct_data.columns.to_list()
        # 用二次规划求解：用QP算法：min 1/2 * (x * P * x^T) + (q^T * x)
        P, q = matrix(np.array(2 * covs)), matrix(np.zeros(len(code_list)))
        # 筛选条件4：是否进行多空等权配置
        if same_weight == True:
            if pca == True:
                # 定义约束条件1——Gx≤h：x*E(r)≥0即除了大宗个股外，其余所有个股均要≤0
                G = pca_para.copy()
                G.loc[Original_code, Original_code] = 0
                G = G.fillna(0)
                h = pd.Series(0.0, index=pca_para.columns)
                h.loc[Original_code]=0
                G, h = matrix(np.array(G).T), matrix(h)
                # 定义约束条件2——Ax=b：大宗个股权重为1，其余个股权重为-1
                A = pd.DataFrame(1.0, index=pca_para.columns,columns=['weight'])
                A.loc[Original_code,Original_code]=1
                A = A.fillna(0)

                A_ =pca_para.copy()
                A_.loc[Original_code, Original_code] = 1
                A_ = A_.fillna(0)
                A = A.T.dot(A_.T)
                A, b = matrix(np.array(A)), matrix([-1.0, 1.0])

            else:
                # 定义约束条件1——Gx≤h：x*E(r)≥0即除了大宗个股外，其余所有个股均要≤0
                G = pd.DataFrame(np.identity(len(code_list)), index=code_list, columns=code_list)
                G.loc[Original_code, Original_code] = 0
                h = pd.Series(0.0, index=code_list)
                G, h = matrix(np.array(G)), matrix(h)
                # 定义约束条件2——Ax=b：大宗个股权重为1，其余个股权重为-1
                A, A_ = pd.Series(1.0, index=code_list), pd.Series(0.0, index=code_list)
                A__ = pd.concat([A, A_], axis=1)
                A__.loc[Original_code, 0] = 0
                A__.loc[Original_code, 1] = 1
                A, b = matrix(np.array(A__).T), matrix([-1.0, 1.0])

            sol = solvers.qp(P, q, G=G, h=h, A=A, b=b)
        else:
            A = pd.Series(0.0, index=code_list)
            A.loc[Original_code] = 1
            A, b = matrix(A).T, matrix(1.0)
            sol = solvers.qp(P, q, A=A, b=b)

        if pca == True:
            para = pd.Series(sol['x'], index=code_list).loc[pca_para.index]
            para = (para * pca_para.T).sum(axis=1)
        else:
            para = pd.Series(sol['x'], index=code_list).loc[similarity_list]
        para = round(para, 4)[abs(round(para, 4))>=0.01]

        return para

    def Adjusted_MeanVar(self,dict_data, func='error', pca=False, same_weight=False, before_days=120):
        # 1、先把基础数据拿出来
        date, Original_code, similarity_list = dict_data['date'], dict_data['stk_id'], dict_data['hedge_list']

        # 筛选条件1：测试周期before_weight：会剔除停牌的日期
        trade_range = get_trade_days(date, trade_days=before_days, delay=1, type='history')
        trade_days = list(self.pct_chg.loc[trade_range, Original_code].dropna().index)  # 交易日期
        y = self.pct_chg.loc[trade_days, Original_code] / 100  # 获取原始原始股票的日均收益率（原始样本）
        x = self.pct_chg.loc[trade_days, similarity_list].fillna(0) / 100
        pct_data = pd.concat([x, y], axis=1)
        means, covs = pct_data.mean(), pct_data.cov()
        if func == 'sumerror':
            x = x.cumsum()
            y = y.cumsum()
        # 开始进入循环
        useful_code = []
        error_R2 = np.inf
        # 先确定使用多少个股
        test_code = similarity_list.copy()
        while len(test_code) > 0:
            test_result = pd.DataFrame(index=test_code, columns=['error2'])
            for i in test_code:
                step_code = list(set(useful_code).union([i]))
                test_dict_data = {'date': date, 'stk_id': similarity_list, 'hedge_list': step_code}
                para = self.AssetAllocation_MeanVariance(test_dict_data,func,pca,same_weight,before_days)
                test_result.loc[i, 'error2'] = para.dot(covs.loc[step_code,step_code]).dot(para)

            choice_code = test_result.sort_values(by='error2', ascending=True).index[0]
            if error_R2 > test_result['error2'].min():
                error_R2 = test_result['error2'].min()
                useful_code.append(choice_code)
                test_code.remove(choice_code)
            else:
                break

        # 再确定权重
        if len(useful_code) > 0:
            test_dict_data = {'date': date, 'stk_id': similarity_list, 'hedge_list': useful_code}
            para = self.AssetAllocation_MeanVariance(test_dict_data,func,pca,same_weight,before_days)
        else:
            para = pd.Series(index=useful_code)

        return para

    '''
    # 优化算法3：风险平价模型（基础方法不适用）
    # 优化算法3：在使得sharpe比率相等时，最小化方差；这个必须在多只个股时才能使用（其中使用风险平价模型）
    # 不同的组合：先sharpe比率相等后，直接使得均值相同，还是使用风险评价模型求配置
    def AssetAllocation_RiskParity(self, pct_df, Original_code):
        # （1）计算组合风险方差
        def cal_portfolio_var(w, var):
            return (w * matrix(np.array(var)) * w.T)[0, 0]
        # (2）计算单个资产的风险贡献度
        def cal_risk_contribution(w, var):
            sigma = np.sqrt(cal_portfolio_var(w, var))  # 标准差，即分母
            MRC = matrix(np.array(var)) * w.T
            TRC = np.multiply(MRC, w.T) / sigma
            return TRC
        # （3）计算组合风险
        def risk_budget_objective(w, paras):
            # paras为参数，该参数包括方差var，目标风险贡献度risk_contribution=[0.25,0.25,0.25,0.25]
            w = matrix(w).T
            var = paras[0]  # 获取协方差
            risk = paras[1]  # 获取目标风险贡献度
            sigma = np.sqrt(cal_portfolio_var(w, var))  # 即投资组合的标准差
            risk_target = np.asmatrix(np.multiply(risk, sigma))  # 这是真正的目标风险值
            TRC = cal_risk_contribution(w, var)
            risk_parity = sum(np.square(TRC - risk_target.T))[0, 0]

            return risk_parity
        # 数据规整
        code_list = list(pct_df.columns)
        var = pct_df.cov()  # 计算协方差
        # 优化开始：最优化
        # （1）优化参数：权重加总为1，各项参数均＞0
        def total_weight_constraint(w):
            return w[code_list.index(Original_code)] - 1

        def long_only_constraint(w):
            return w

        # （2)运行参数：
        # type：设定为'eq'表示等式约束, 设定为'ineq',表示不等式约束
        # fun：设定约束表达式，仅输入表达式左边，默认为左边小于或等于0
        cons = ({'type': 'eq', 'fun': total_weight_constraint}, {'type': 'ineq', 'fun': long_only_constraint})
        w0, risk = [1 / len(code_list) for i in code_list], [1 / len(code_list) for i in code_list]
        res = minimize(risk_budget_objective, w0, args=[var, risk], method='SLSQP', constraints=cons)['x']
        riskparity_res = pd.Series(res, index=code_list)

        return riskparity_res

    def optimization_samesharpe(self, dict_data,before_days=120, ways='mean'):
        # 先处理数据
        date, Original_code, similarity_list = dict_data['date'], dict_data['stk_id'], dict_data['hedge_list']
        trade_range = get_trade_days(date, trade_days=before_days, delay=1, type='history')
        trade_days = list(self.pct_chg.loc[trade_range, Original_code].dropna().index)  # 交易日期
        # 计算大宗个股的sharpe比率
        bigdeal_pct = self.pct_chg.loc[trade_days, Original_code] / 100  # 大宗个股的每日收益率
        sharpe = bigdeal_pct.mean() / bigdeal_pct.std()
        similarity_pct = self.pct_chg.loc[trade_days, similarity_list].fillna(0) / 100  # 计划对冲个股的每日收益率
        code_list = list(similarity_pct.columns)

        # 先定义最优化部分：即最小化跟踪误差
        # （1）优化目标：确保组合的跟踪误差的方法最小
        def risk_budget_objective(w, args):
            # paras为参数，该参数包括投资组合的单日收益；大宗个股的单日收益
            similarity_pct = args[0]  # 获取计划对冲个股的每日收益率
            bigdeal_pct = args[1]  # 获取大宗个股的每日收益率
            # 计算误差的方差
            risk_error = (((matrix(w) * similarity_pct).sum(axis=1) - bigdeal_pct) ** 2).sum()

            return risk_error

        # （2）约束条件：使得组合的sharpe与大宗的shapre相等
        def equal_sharpe(w):
            combine_pct = (matrix(w) * similarity_pct).sum(axis=1)
            return abs(combine_pct.mean() / combine_pct.std() - sharpe)

        def para_bigger(w):
            return max(abs(w)) - 0.1

        # def para_max(w):
        #    return 2-max(abs(w))
        # type：设定为'eq'表示等式约束, 设定为'ineq',表示不等式约束
        # fun：设定约束表达式，仅输入表达式左边，默认为左边≥0
        cons = ({'type': 'eq', 'fun': equal_sharpe}, {'type': 'ineq', 'fun': para_bigger})
        # {'type': 'ineq', 'fun': para_max})
        # cons = {'fun': equal_sharpe,'type': 'eq'}#,'fun': para_bigger, 'type': 'ineq'}
        options = {'maxiter': 500, 'maxfun': 1500000}
        bnds = [(-2, 2) for i in code_list]
        # 开始初始化并进行求解
        w0 = [1 / len(code_list) for i in code_list]
        solve_result = minimize(risk_budget_objective, w0, args=[similarity_pct, bigdeal_pct], method='SLSQP',
                                bounds=bnds, constraints=cons, options=options)
        res = solve_result['x']
        while solve_result['success'] == False:
            if max(abs(solve_result['x'])) > 10:
                w0 = solve_result['x'] / max(abs(solve_result['x']))
                solve_result = minimize(risk_budget_objective, w0, args=[similarity_pct, bigdeal_pct], method='SLSQP',
                                        bounds=bnds, constraints=cons, options=options)
                res = solve_result['x']
            else:
                break

        # 最后得到的结果是，sharpe相同时的组合权重res。在获取该权重后，有两个选项：
        # 选项1：直接根据收益率配平
        if ways == 'mean':
            para = res * bigdeal_pct.mean() / (matrix(res) * similarity_pct).sum(axis=1).mean()
        # 方案二：在保证投资品夏普率相等时，再进行风险平价
        else:
            pct_df = pd.concat([(matrix(res) * similarity_pct).sum(axis=1), bigdeal_pct], axis=1)
            pct_df.columns = ['combine', Original_code]
            riskparity_res = self.AssetAllocation_RiskParity(pct_df, Original_code)
            para = res * riskparity_res.loc['combine']
        # 注：这两个结果理论上保持一致，均为res*大宗均值/组合均值，即1*大宗均值 = x * 组合均值，x= 大宗均值/组合均值
        return -pd.Series(para, index=code_list)

    def Adjusted_RiskParity(self, dict_data, corr_pd):
        # 先处理数据
        date, Original_code, similarity_list = dict_data['date'], dict_data['stk_id'], dict_data['hedge_list']
        trade_range = get_trade_days(date, trade_days=self.before_days, delay=1, type='history')
        trade_days = list(self.pct_chg.loc[trade_range, Original_code].dropna().index)  # 交易日期
        # 计算大宗个股的sharpe比率
        bigdeal_pct = self.pct_chg.loc[trade_days, Original_code] / 100  # 大宗个股的每日收益率
        sharpe = bigdeal_pct.mean() / bigdeal_pct.std()
        # 这个由于一开始就至少需要2个对冲个股，所以需要分成两步：
        # 第一步，先两两一组，选出来sharpe比率最小的
        test_result = pd.DataFrame(columns=['code1', 'code2', 'sharpe_error',
                                            'history_error', 'history_maxerror', 'future_error', 'future_maxerror'])
        index = 0
        for i in list(corr_pd.index):
            for j in list(corr_pd.index):
                if i != j:
                    code_list = [i, j]
                    similarity_pct = self.pct_chg.loc[trade_days, code_list].fillna(0) / 100  # 计划对冲个股的每日收益率

                    # 先定义最优化部分：即最小化跟踪误差
                    # （1）优化目标：确保组合的跟踪误差的方法最小
                    def risk_budget_objective(w, args):
                        # paras为参数，该参数包括投资组合的单日收益；大宗个股的单日收益
                        similarity_pct = args[0]  # 获取计划对冲个股的每日收益率
                        bigdeal_pct = args[1]  # 获取大宗个股的每日收益率
                        # 计算误差的方差
                        risk_error = (((matrix(w) * similarity_pct).sum(axis=1) - bigdeal_pct) ** 2).sum()

                        return risk_error

                    # （2）约束条件：使得组合的sharpe与大宗的shapre相等
                    def equal_sharpe(w):
                        combine_pct = (matrix(w) * similarity_pct).sum(axis=1)
                        return abs(combine_pct.mean() / combine_pct.std() - sharpe)

                    def para_bigger(w):
                        return max(abs(w)) - 0.1

                    cons = ({'type': 'eq', 'fun': equal_sharpe}, {'type': 'ineq', 'fun': para_bigger})
                    options = {'maxiter': 500, 'maxfun': 1500000, 'disp': False}
                    bnds = [(-2, 2) for i in code_list]
                    # 开始初始化并进行求解
                    w0 = [1 / len(code_list) for i in code_list]
                    try:
                        solve_result = minimize(risk_budget_objective, w0, args=[similarity_pct, bigdeal_pct],
                                                method='SLSQP',
                                                bounds=bnds, constraints=cons, options=options)
                    except:
                        continue
                    res = solve_result['x']
                    while solve_result['success'] == False:
                        if max(abs(solve_result['x'])) > 10:
                            w0 = solve_result['x'] / max(abs(solve_result['x']))
                            solve_result = minimize(risk_budget_objective, w0, args=[similarity_pct, bigdeal_pct],
                                                    method='SLSQP',
                                                    bounds=bnds, constraints=cons, options=options)
                            res = solve_result['x']
                        else:
                            break

                    pct_df = pd.concat([(matrix(res) * similarity_pct).sum(axis=1), bigdeal_pct], axis=1)
                    pct_df.columns = ['combine', Original_code]
                    riskparity_res = self.AssetAllocation_RiskParity(pct_df, Original_code)
                    para = res * riskparity_res.loc['combine']

                    sharpe_error = equal_sharpe(res)
                    test_result.loc[index, ['code1', 'code2', 'sharpe_error']] = i, j, sharpe_error

                    trade = self.Result_Test(date, Original_code, pd.Series(-para, index=code_list), test_name=i)
                    test_result.loc[index, ['history_error', 'history_maxerror', 'future_error', 'future_maxerror']] = \
                        trade.loc[['history_error', 'history_maxerror', 'future_error', 'future_maxerror'], i]
                    index += 1
        # 如果都比较差，就按照最终结果；如果都比较好，就按照误差来选
        test_result = test_result.sort_values(by='sharpe_error')
        test_smallerror = test_result[test_result['sharpe_error'] <= 1e-3]
        if len(test_smallerror) > 0:
            useful_code = list(test_smallerror.sort_values(by='history_maxerror').iloc[0][['code1', 'code2']])
            adjusted_sharpe = 1e-3
            adjusted_error = test_smallerror.iloc[0]['history_maxerror']
        else:
            useful_code = list(test_result.iloc[0][['code1', 'code2']])
            adjusted_sharpe = test_result.iloc[0]['sharpe_error']
            adjusted_error = test_result.iloc[0]['history_maxerror']

        # 第二步：再计算test_code，即需要填充的个股
        test_code = set(corr_pd.index).difference(useful_code)
        test_code = list(corr_pd.loc[test_code].sort_values(ascending=False).index)
        while len(test_code) > 0:
            test_result = pd.DataFrame(index=test_code, columns=['sharpe_error', 'history_error', 'history_maxerror',
                                                                 'future_error', 'future_maxerror'])
            for i in test_code:
                step_code = list(set(useful_code).union([i]))
                similarity_pct = self.pct_chg.loc[trade_days, step_code].fillna(0) / 100  # 计划对冲个股的每日收益率

                # 先定义最优化部分：即最小化跟踪误差
                # （1）优化目标：确保组合的跟踪误差的方法最小
                def risk_budget_objective(w, args):
                    # paras为参数，该参数包括投资组合的单日收益；大宗个股的单日收益
                    similarity_pct = args[0]  # 获取计划对冲个股的每日收益率
                    bigdeal_pct = args[1]  # 获取大宗个股的每日收益率
                    # 计算误差的方差
                    risk_error = (((matrix(w) * similarity_pct).sum(axis=1) - bigdeal_pct) ** 2).sum()

                    return risk_error

                # （2）约束条件：使得组合的sharpe与大宗的shapre相等
                def equal_sharpe(w):
                    combine_pct = (matrix(w) * similarity_pct).sum(axis=1)
                    return abs(combine_pct.mean() / combine_pct.std() - sharpe)

                def para_bigger(w):
                    return max(abs(w)) - 0.1

                cons = ({'type': 'eq', 'fun': equal_sharpe}, {'type': 'ineq', 'fun': para_bigger})
                options = {'maxiter': 500, 'maxfun': 1500000}
                bnds = [(-2, 2) for i in step_code]
                # 开始初始化并进行求解
                w0 = [1 / len(step_code) for i in step_code]
                try:
                    solve_result = minimize(risk_budget_objective, w0, args=[similarity_pct, bigdeal_pct],
                                            method='SLSQP',
                                            bounds=bnds, constraints=cons, options=options)
                except:
                    continue
                res = solve_result['x']
                while solve_result['success'] == False:
                    if max(abs(solve_result['x'])) > 10:
                        w0 = solve_result['x'] / max(abs(solve_result['x']))
                        solve_result = minimize(risk_budget_objective, w0, args=[similarity_pct, bigdeal_pct],
                                                method='SLSQP',
                                                bounds=bnds, constraints=cons, options=options)
                        res = solve_result['x']
                    else:
                        break

                pct_df = pd.concat([(matrix(res) * similarity_pct).sum(axis=1), bigdeal_pct], axis=1)
                pct_df.columns = ['combine', Original_code]
                riskparity_res = self.AssetAllocation_RiskParity(pct_df, Original_code)
                para = res * riskparity_res.loc['combine']

                sharpe_error = equal_sharpe(res)
                test_result.loc[i, 'sharpe_error'] = sharpe_error

                trade = self.Result_Test(date, Original_code, pd.Series(-para, index=step_code), test_name=i)
                test_result.loc[i, ['history_error', 'history_maxerror', 'future_error', 'future_maxerror']] = \
                    trade.loc[['history_error', 'history_maxerror', 'future_error', 'future_maxerror'], i]

            # 如果都比较差，就按照最终结果；如果都比较好，就按照误差来选
            test_result = test_result.sort_values(by='sharpe_error')
            test_smallerror = test_result[test_result['sharpe_error'] <= 1e-3]
            if len(test_smallerror) > 0:
                choice_code = test_smallerror.sort_values(by='history_maxerror').index[0]
                if test_smallerror['history_maxerror'].min() < adjusted_error:
                    adjusted_sharpe = 1e-3
                    adjusted_error = test_smallerror['history_maxerror'].min()
                    useful_code.append(choice_code)
                    test_code.remove(choice_code)
                else:
                    break
            else:
                choice_code = test_result.sort_values(by='sharpe_error').index[0]
                if test_result['sharpe_error'].min() < adjusted_error:
                    adjusted_sharpe = test_result['sharpe_error'].min()
                    adjusted_error = test_result.loc[choice_code, 'history_maxerror']
                    useful_code.append(choice_code)
                    test_code.remove(choice_code)
                else:
                    break

        # 最后：都选好了，再输出最后确定的权重
        dict_data1 = {'date': date, 'stk_id': Original_code, 'discount': dict_data['discount'],
                      'hedge_list': useful_code}

        return self.optimization_samesharpe(dict_data1, 'riskparity')
    '''
    ########################### 优化第三步：风险评价指标 ############################################
    # 方法1：直接使用历史的跟踪误差作为未来跟踪误差的估计
    # 方法2：使用VaR法：①用历史模拟法进行历史评估，②方差-协方差法
    # 方法3：使用CVaR：评估满足VaR的预计亏损
    def Risk_Estimation(self, history_trade, profit, c=0.95, mode=['real','var']):
        # 置信度c:90%，95%，99%
        # 方法model：历史实际累计误差，历史模拟法误差，时间加权历史模拟法，方差-协方差法
        # 时间周期date：120
        # real：使用历史的实际跟踪误差
        prob_error_list = []
        trade = history_trade.cumsum()
        for mode_i in mode:
            # real：使用历史的实际最大跟踪误差
            if mode_i == 'real':
                prob_error = abs(trade).sort_values().iloc[int(round(len(trade) * c, 0)):].mean()
                if abs(abs(trade.iloc[-1]))>0.1:
                    prob_error = min(abs(trade.iloc[-1]), prob_error)
            # trade_real：使用历史的实际跟踪误差
            if mode_i == 'trade_real':
                prob_error = abs(trade).sort_values().iloc[int(round(len(trade) * c, 0)):].mean()
                prob_error = min(abs(trade.iloc[-10:-1]).mean(), prob_error)
            # history：使用历史模拟法的跟踪误差
            elif mode_i == 'history':
                prob_error = history_trade.sort_values(ascending=False).iloc[int(round(len(history_trade) * c, 0)):].min()
                prob_error = prob_error * np.sqrt(self.after_days)
            # time_history：使用时间加权历史模拟法的跟踪误差
            elif mode_i == 'time_history':
                sigma = np.log(2) * 2 / len(history_trade)
                alpha = pd.Series([np.exp(-i * sigma) for i in range(len(history_trade), 0, -1)],index=history_trade.index).round(3)

                pro_list = pd.concat([alpha / alpha.sum(), history_trade], axis=1).sort_values(by=1)
                prob_error = pro_list.loc[:pro_list[0].cumsum()[pro_list[0].cumsum() >= 1 - c].index[0]]

                prob_error = (prob_error[0] * prob_error[1]).sum() / (prob_error[0].sum())
                prob_error = prob_error * np.sqrt(self.after_days)
            # VaR：使用均值方差法计算
            elif mode_i == 'var':
                # 单尾检验
                Z_score = {0.99: 2.33, 0.97: 1.96, 0.95: 1.645, 0.9: 1.29}
                z = Z_score[c]
                trade_mean, trade_std = history_trade.mean(), history_trade.std()
                prob_error = trade_mean * self.after_days - z * trade_std * np.sqrt(self.after_days)

            prob_error_list.append(abs(prob_error))

        self.need_profit = min(prob_error_list)+0.05
        if min(prob_error_list) + 0.05 <= profit:
            return True
        else:
            return False

    ########################### 优化完毕：结果展示 #######################################################
    # 参数1：即如果评估未来或者历史的每日收益
    def trade_excess_gain(self,Original_code,para,trade_days,way='net'):
        # 确定对冲个股
        similarity_list = list(para.index)
        # 注意：此时得到的结果为，在不同方法下，实际得到的每日收益额（相对于初始金额的收益率）
        # 方法1：最简单的净值法
        if way == 'net':
            net_trade = (self.pct_chg.loc[trade_days,Original_code] + (para * self.pct_chg.loc[trade_days,similarity_list].fillna(0)).sum(axis=1))/100  # 加权
            net_gain = net_trade * (1+net_trade).cumprod().shift(1).fillna(1)

        # 方法2：考虑规模效应，使用多头配平的净值法
        elif way == 'long_net':
            long_net_trade = (self.pct_chg.loc[trade_days,Original_code] + (para * self.pct_chg.loc[trade_days,similarity_list].fillna(0)).sum(axis=1)) /100  # 加权
            net_gain = long_net_trade * (self.pct_chg.loc[trade_days,Original_code]/100+1).cumprod().shift(1).fillna(1)

        # 方法3：完全不配平，直接使用第一日的权重评估
        elif way == 'first_net':
            long_value = (1 + self.pct_chg.loc[trade_days, Original_code] / 100).cumprod()-1
            short_value = (1+(para * self.pct_chg.loc[trade_days,similarity_list].fillna(0)).sum(axis=1)/100).cumprod()-1
            lsvalue = long_value + short_value
            net_gain = lsvalue.diff(1)
            net_gain.iloc[0] = lsvalue.iloc[0]

        elif way == 'situation_net':
            # 当累计多空偏离达到10%时，重新配平：
            change_date_list = [trade_days[0]]
            difference_combine = (1 + self.pct_chg.loc[trade_days, Original_code] / 100).cumprod() - (1 + (para * self.pct_chg.loc[trade_days, similarity_list].fillna(0)).sum(axis=1) / 100).cumprod()
            difference_combine = difference_combine[abs(difference_combine)>=0.1]
            while len(difference_combine)>0:
                change_date = difference_combine.index[0]
                change_date_list.append(change_date)
                # 开始从当前开始：
                another_trade_date = trade_days[trade_days.index(change_date)+1:]
                difference_combine = (1 + self.pct_chg.loc[another_trade_date, Original_code] / 100).cumprod() - (1 + (para * self.pct_chg.loc[another_trade_date, similarity_list].fillna(0)).sum(axis=1) / 100).cumprod()
                difference_combine = difference_combine[abs(difference_combine) >= 0.1]
            change_date_list.append(trade_days[-1])
            # 开始按照这个来调整：
            net_gain = pd.Series()
            for i in range(0,len(change_date_list)-1):
                start_date,end_date = change_date_list[i], change_date_list[i+1]
                long_value = (1 + self.pct_chg.loc[start_date:end_date, Original_code] / 100).cumprod() - 1
                short_value = (1 + (para * self.pct_chg.loc[start_date:end_date, similarity_list].fillna(0)).sum(axis=1) / 100).cumprod() - 1
                lsvalue = long_value + short_value
                trade_gain = lsvalue.diff(1)
                trade_gain.iloc[0] = lsvalue.iloc[0]
                net_gain = pd.concat([net_gain, trade_gain])
            net_gain = net_gain[~net_gain.index.duplicated(keep='first')]


        return net_gain
    # 输出3个历史结果：历史相关系数，历史最大跟踪误差，未来到期误差
    # 输出3个未来结果：未来相关系数，未来最大跟踪误差，未来到期误差
    def Result_Test(self, date, Original_code, para, way, test_name, profit, mode=['real', 'var']):
        # 确定时间窗口
        before_days = get_trade_days(date, trade_days=self.before_days, delay=1, type='history')
        after_days = get_trade_days(date, trade_days=self.after_days + 5, delay=1, type='future')

        before_trade_days = list(self.pct_chg.loc[before_days, Original_code].dropna().index)
        after_trade_days = list(self.pct_chg.loc[after_days, Original_code].dropna().index)

        similarity_list = list(para.index)
        # 确定组合的权重，并进行拟合
        history_trade = self.trade_excess_gain(Original_code,para, before_trade_days, way)
        future_trade = self.trade_excess_gain(Original_code, para, after_trade_days, way)

        # 输出3个历史结果：历史相关系数，历史到期误差，历史最大跟踪误差
        weighted_history_corr = (-para * self.pct_chg.loc[before_trade_days, similarity_list]).sum(axis=1).corr(self.pct_chg.loc[before_trade_days, Original_code])
        weighted_history_error, weighted_history_maxerror = cal_history_trade_result(history_trade)
        # 输出3个未来结果：未来相关系数，未来到期误差，未来最大跟踪误差
        weighted_future_corr = (-para * self.pct_chg.loc[after_trade_days, similarity_list]).sum(axis=1).corr(self.pct_chg.loc[after_trade_days, Original_code])
        weighted_future_error, weighted_future_maxerror = cal_future_trade_result(future_trade)

        Result = pd.DataFrame(index=['history_corr', 'history_error', 'history_maxerror', 'future_corr', 'future_error','future_maxerror', ], columns=[test_name])
        Result[test_name] = weighted_history_corr, weighted_history_error, weighted_history_maxerror, \
                            weighted_future_corr, weighted_future_error, weighted_future_maxerror

        Result = Result.apply(lambda x: x.apply(lambda y: round(y, 4) if np.isnan(y) == False else np.nan))
        Result.loc['if_trade', test_name] = self.Risk_Estimation(history_trade.loc[before_trade_days],profit, mode=mode)

        return Result
    # 输出历史样本
    def cal_history_result(self, history_data, func, pca, same_weight, before_days,way,mode, num_list=[2, 3, 4, 5, 6, 7, 8, 9]):
        # 读取样本数据
        trade_date = history_data['date']
        Original_code, similarity_list = history_data['stk_id'], history_data['hedge_list']
        profit = 1 - history_data['discount']
        # 确定时间窗口：历史时间区间是成交日的前一天，未来时间区间是成交日的后一天
        ############################# 评估历史不同方案，确定的结果 #############################################
        all_result = dict()
        if len(similarity_list) < min(num_list):
            return None

        for num in num_list:
            if len(similarity_list) >= num:
                # 1、等权配置结果
                para1 = pd.Series(-1 / num, index=similarity_list[:num])
                name1 = str(num) + '_average'
                all_result[name1] = self.Result_Test(trade_date, Original_code, para1, way, name1, profit, mode=mode)
                # 2、加权配置结果
                history_data_change = {'date': trade_date, 'stk_id': Original_code,
                                       'discount': history_data['discount'], 'hedge_list': similarity_list[:num]}
                # 第一种方案：多元线性回归
                fit_weighted1 = self.CurveFitting_LeastSquares(history_data_change, func=func, pca=pca, same_weight=same_weight, before_days=before_days)
                fit_name1 = str(num) + '_curve'
                all_result[fit_name1] = self.Result_Test(date=trade_date, Original_code=Original_code, para=fit_weighted1, way=way, test_name=fit_name1, profit=profit)
                # 第二种：均值-方差法
                try:
                    fit_weighted2 = self.AssetAllocation_MeanVariance(history_data_change, func=func, pca=pca, same_weight=same_weight, before_days=before_days)
                    fit_name2 = str(num) + '_meanvar'
                    all_result[fit_name2] = self.Result_Test(date=trade_date, Original_code=Original_code, para=fit_weighted2, way=way, test_name=fit_name2, profit=profit)
                except:
                    print(str(Original_code) + '在' + str(trade_date) + '日无解,数量为' + str(num))
                # 第三种：风险平价模型
                # if len(similarity_list) >= 2:
                #    fit_weighted3 = self.optimization_samesharpe(history_data_change, model2)
                #    fit_name3 = str(num) + '_riskparity'
                #    all_result[fit_name3] = self.Result_Test(trade_date, Original_code, fit_weighted3, fit_name3, profit, mode=mode)

        # 组合一下
        history_result = pd.DataFrame()
        for one_result in all_result.keys():
            history_result = pd.concat([history_result, all_result[one_result]], axis=1)

        history_result.loc['trade_date'] = trade_date
        history_result.loc['code'] = Original_code
        history_result.loc['discount'] = profit

        return history_result
    # 输出未来样本
    def cal_future_result(self,future_dict,future_model_list,Original_code,choice,func, pca, same_weight,before_days):
        # choice表明前N个个股不能用
        date = future_dict['start_date']
        similarity_list = future_dict['hedge_list'][choice:]
        # 均值结果
        future_newpara = pd.DataFrame(index= similarity_list,columns=future_model_list)
        for funture_model in future_model_list:
            num,model_type = funture_model.split('_')
            code_list = similarity_list[:int(num)]
            future_dict_data = dict({'date': date, 'stk_id': Original_code, 'hedge_list': similarity_list[:int(num)]})
            if model_type == 'average':
                para = pd.Series(-1 / len(code_list), index=code_list)
            elif model_type == 'curve':
                para = self.CurveFitting_LeastSquares(future_dict_data, func=func, pca=pca, same_weight=same_weight, before_days=before_days)
            elif model_type == 'meanvar':
                try:
                    para = self.AssetAllocation_MeanVariance(future_dict_data, func=func, pca=pca, same_weight=same_weight,before_days=before_days)
                except:
                    para = pd.Series()
                    print(str(Original_code) + '在' + str(date) + '日无解')
            #elif model_type == 'riskparity':
            #    para = self.optimization_samesharpe(future_dict_data, before_days,model2)

            future_newpara[funture_model] = para

        return future_newpara
    ############################################# 针对方法周期的评估 ###############################################################
    # 第一种评估方法：即使用不同周期的数据来拟合（30，60,90,,120,150,180,210,240），对未来结果的影响
    def Test_Difference_Time(self,factor, func, pca, same_weight, before_days, way, mode, num_list,
                                choice,if_ind='银行'):
        '''
        Data_Result = pd.DataFrame()
        for dict_data in tqdm(factor):
            date, Original_code, discount = dict_data['date'], dict_data['stk_id'], 1 - dict_data['discount']
            # 先评估历史的结果，历史的跟踪误差，与从历史的角度看能否参与
            history_hedge_list = dict_data['hedge_list'][0]['hedge_list'][choice:]
            if len(history_hedge_list) > 1:  # 如果能用的股票数量太少，不参与
                # 获取历史测试的样本数据
                history_data = {'stk_id': Original_code, 'date': date, 'discount': dict_data['discount'],
                                'hedge_list': history_hedge_list}
                history_result = self.cal_history_result(history_data, func, pca, model1, mode, before_weight=train_days)

                Data_Result = pd.concat([Data_Result, history_result.unstack()], axis=1)

        Data_Result = Data_Result.T.reset_index().drop('index', axis=1)
        '''
        Data_Result = pd.DataFrame()
        ret_dict = multiprocess(24, self.RolDays_Test, factor, func, pca, same_weight, before_days, way, mode, num_list,
                                choice)
        for k in ret_dict:
            Data_Result = pd.concat([Data_Result, ret_dict[k].get()], axis=1)

        Data_Result = Data_Result.T.reset_index().drop('index', axis=1)

        # 特定行业
        if type(if_ind)==str:
            use_model = list(Data_Result.columns.levels[0])
            use_model.remove('index')
            # 确定一共有多少个行业
            SW1 = getData.get_daily_1factor('SW1')
            code_ind = Data_Result[use_model[0]][['code', 'trade_date']]
            code_ind['ind'] = pd.Series(code_ind.index).apply(lambda x: indName.sw_level1[SW1.loc[code_ind.loc[x, 'trade_date'], code_ind.loc[x, 'code']]] if np.isnan(code_ind.loc[x, 'trade_date']) == False else np.nan)

            ind_result = Data_Result.loc[code_ind['ind'][code_ind['ind'] == if_ind].index]
            if len(ind_result)>0:
                # 进行结果统计：
                ind_all, ind_buy = self.GetTradeResult(ind_result)
                # （1）分年度
                ind_year_all, ind_year_buy = self.Get_Difference_Year(ind_result)

                # 数据保存：年度数据
                year_all_statistic_data = pd.DataFrame()
                year_buy_statistic_data = pd.DataFrame()
                for year in ind_year_all.keys():
                    alldata = ind_year_all[year].copy()
                    alldata['year'] = year
                    alldata = alldata.reset_index().set_index(['year', 'index'])

                    year_all_statistic_data = pd.concat([year_all_statistic_data, alldata])

                    buydata = ind_year_buy[year].copy()
                    buydata['year'] = year
                    buydata = buydata.reset_index().set_index(['year', 'index'])

                    year_buy_statistic_data = pd.concat([year_buy_statistic_data, alldata])

                writer = pd.ExcelWriter(self.save_path + factor_name + '训练周期' + str(before_days) +if_ind+ '.xlsx')
                ind_all.to_excel(writer, sheet_name='整体统计结果')
                ind_buy.to_excel(writer, sheet_name='交易统计结果')
                year_all_statistic_data.to_excel(writer, sheet_name='年度整体结果')
                year_buy_statistic_data.to_excel(writer, sheet_name='年度交易结果')

                ind_result.to_excel(writer, sheet_name='单笔结果')
                writer.save()
                send_file(self.save_path + factor_name + '训练周期' + str(before_days) + if_ind +'.xlsx')

                return None

        # 全部行业
        # 进行结果统计：
        all_statistic_data,buy_statistic_data = self.GetTradeResult(Data_Result)
        # （1）分年度
        year_alldata, year_buydata = self.Get_Difference_Year(Data_Result)
        # （2）分行业
        # ind_alldata, ind_buydata = self.Get_Difference_Industry(Data_Result)
        # 数据保存：年度数据
        year_all_statistic_data = pd.DataFrame()
        year_buy_statistic_data = pd.DataFrame()
        for year in year_alldata.keys():
            alldata = year_alldata[year].copy()
            alldata['year'] = year
            alldata = alldata.reset_index().set_index(['year','index'])

            year_all_statistic_data = pd.concat([year_all_statistic_data,alldata])

            buydata = year_buydata[year].copy()
            buydata['year'] = year
            buydata = buydata.reset_index().set_index(['year', 'index'])

            year_buy_statistic_data = pd.concat([year_buy_statistic_data, buydata])

        # 数据保存行业数据
        '''
        ind_all_statistic_data = pd.DataFrame()
        ind_buy_statistic_data = pd.DataFrame()
        for ind in ind_alldata.keys():
            alldata = ind_alldata[ind].copy()
            alldata['ind'] = ind
            alldata = alldata.reset_index().set_index(['ind', 'index'])

            ind_all_statistic_data = pd.concat([ind_all_statistic_data,alldata])

            buydata = ind_buydata[ind].copy()
            buydata['ind'] = ind
            buydata = buydata.reset_index().set_index(['ind', 'index'])

            ind_buy_statistic_data = pd.concat([ind_buy_statistic_data, buydata])
        '''

        writer = pd.ExcelWriter(self.save_path + factor_name + '训练周期' + str(before_days) + '.xlsx')
        all_statistic_data.to_excel(writer, sheet_name='整体统计结果')
        buy_statistic_data.to_excel(writer, sheet_name='交易统计结果')
        year_all_statistic_data.to_excel(writer, sheet_name='年度整体结果')
        year_buy_statistic_data.to_excel(writer, sheet_name='年度交易结果')
        #ind_all_statistic_data.to_excel(writer, sheet_name='行业整体结果')
        #ind_buy_statistic_data.to_excel(writer, sheet_name='行业交易结果')
        Data_Result.to_excel(writer, sheet_name='单笔结果')
        writer.save()
        send_file(self.save_path + factor_name + '训练周期' + str(before_days) + '.xlsx')

    # 第二种评估方法：即我未来从不变换个股，但我每隔N日变换一次权重（固定10日），不同周期数据拟合下结果的差异（10,20,30,40,60,90,120，150,180）
    def Test_Difference_Range(self,factor,future_weight=120,rol_days=10,train_days=120):
        # 先计算历史的结果
        Data_Result = pd.DataFrame()
        for dict_data in tqdm(factor):
            date, Original_code, discount = dict_data['date'], dict_data['stk_id'], 1 - dict_data['discount']
            # 先评估历史的结果，历史的跟踪误差，与从历史的角度看能否参与
            history_hedge_list = dict_data['hedge_list'][0]['hedge_list'][choice:]
            if len(history_hedge_list) > 0:  # 如果能用的股票数量太少，不参与
                # 获取历史测试的样本数据
                history_data = {'stk_id': Original_code, 'date': date, 'discount': dict_data['discount'],
                                'hedge_list': history_hedge_list}
                history_result = self.cal_history_result(history_data, func, pca, same_weight, before_days,way,mode, num_list)
                # 在评估未来情况
                future_model_list = history_result.columns  # 历史测算有多少参数
                future_trade = pd.DataFrame(columns=history_result.columns)
                # 第一步：先划分周期
                time_list=[]
                date_range = get_trade_days(date, trade_days=self.after_days+1, delay=0, type='future')
                for i in range(rol_days-1,len(date_range),rol_days):
                    time_list.append(dict({'start_date':date_range[i-rol_days+1],'end_date':date_range[i+1],'hedge_list':history_hedge_list}))
                # 开始进行循环评估：
                for future_dict in time_list:
                    start_date, end_date = future_dict['start_date'], future_dict['end_date']
                    # 直接进行替换
                    future_newpara = self.cal_future_result(future_dict,future_model_list,Original_code,choice,func, pca, same_weight,before_days)
                    # 然后计算这一轮的跟踪结果
                    trade_days = self.pct_chg.loc[start_date:end_date, Original_code].iloc[1:].dropna().index.to_list()
                    future_weighted_trade = pd.DataFrame(index=trade_days, columns=future_model_list)
                    for use_type in future_model_list:
                        future_weighted_trade[use_type] = self.pct_chg.loc[trade_days, Original_code] + (
                                future_newpara[use_type].fillna(0) * self.pct_chg.loc[trade_days, future_newpara.index].fillna(0)).sum(axis=1)

                    future_trade = pd.concat([future_trade, future_weighted_trade])
                # 评估未来的跟踪误差
                weighted_future_error, weighted_future_maxerror = cal_future_trade_result(future_trade / 100)

                history_result.loc['rol_future_error'] = round(weighted_future_error, 4)
                history_result.loc['rol_future_maxerror'] = round(weighted_future_maxerror, 4)

                Data_Result = pd.concat([Data_Result, history_result.unstack()], axis=1)

        # 再做统计数据结果
        Data_Result = Data_Result.T.reset_index().drop('index', axis=1)
        use_model = list(Data_Result.columns.levels[0])
        use_model.remove('index')

        all_statistic_data = pd.DataFrame(index=['num', 'history_error', 'history_maxerror', 'future_error', 'future_maxerror',
                   'rol_future_error', 'rol_future_maxerror'], columns=use_model)
        buy_statistic_data = pd.DataFrame(index=['num', 'history_error', 'history_maxerror', 'future_error', 'future_maxerror',
                   'rol_future_error', 'rol_future_maxerror'], columns=use_model)

        for single_use in use_model:
            # 先统计全部样本
            model_result = Data_Result[single_use].dropna(how='all')
            all_statistic_data.loc['num', single_use] = len(model_result)
            all_statistic_data.loc[['history_error', 'history_maxerror', 'future_error', 'future_maxerror'], single_use] = \
                abs(model_result[['history_error', 'history_maxerror', 'future_error', 'future_maxerror']].astype(float)).quantile(0.5).round(4)
            all_statistic_data.loc[['rol_future_error', 'rol_future_maxerror'], single_use] = \
                abs(model_result[['rol_future_error', 'rol_future_maxerror']].astype(float)).quantile(0.5).round(4)

            # 再统计买入样本
            canbuy_result = model_result[model_result['if_trade'] == True]

            buy_statistic_data.loc['num', single_use] = len(canbuy_result)
            buy_statistic_data.loc[['history_error', 'history_maxerror', 'future_error', 'future_maxerror'], single_use] = \
                abs(canbuy_result[['history_error', 'history_maxerror', 'future_error', 'future_maxerror']].astype(float)).quantile(0.5).round(4)
            buy_statistic_data.loc[['rol_future_error', 'rol_future_maxerror'], single_use] = \
                abs(canbuy_result[['rol_future_error', 'rol_future_maxerror']].astype(float)).quantile(0.5).round(4)
            # 开始统计收益
            canbuy_result['profit'] = canbuy_result['rol_future_error'] + canbuy_result['discount'] - 0.05
            buy_statistic_data.loc['ls_profit', single_use] = round(canbuy_result['rol_future_error'].median(), 4)

            buy_statistic_data.loc['10%profit', single_use] = round(canbuy_result['profit'].quantile(0.1), 4)
            buy_statistic_data.loc['30%profit', single_use] = round(canbuy_result['profit'].quantile(0.3), 4)
            buy_statistic_data.loc['50%profit', single_use] = round(canbuy_result['profit'].quantile(0.5), 4)
            buy_statistic_data.loc['70%profit', single_use] = round(canbuy_result['profit'].quantile(0.7), 4)
            buy_statistic_data.loc['90%profit', single_use] = round(canbuy_result['profit'].quantile(0.9), 4)
            buy_statistic_data.loc['win_rate', single_use] = round(
                (canbuy_result['profit'] > 0).sum() / len(canbuy_result['profit']), 4)
            buy_statistic_data.loc['wl_rate', single_use] = round(
                -canbuy_result['profit'][canbuy_result['profit'] > 0].mean() / canbuy_result['profit'][
                    canbuy_result['profit'] < 0].mean(), 2)

        writer = pd.ExcelWriter(self.save_path + factor_name + '未来拟合周期' + str(future_weight) + '.xlsx')
        all_statistic_data.to_excel(writer, sheet_name='整体统计结果')
        buy_statistic_data.to_excel(writer, sheet_name='交易统计结果')
        Data_Result.to_excel(writer, sheet_name='单笔结果')
        writer.save()
        send_file(self.save_path + factor_name + '未来拟合周期' + str(future_weight) + '.xlsx')

    ########################################## 对于单只个股，优化多次的结果展示 #######################################################
    # 一共4个结果：相关性第一的个股结果，前三名等权结果，等权个股结果，自身结果
    # 输出3个历史结果：历史相关系数，历史最大跟踪误差，未来到期误差
    # 输出3个未来结果：未来相关系数，未来最大跟踪误差，未来到期误差
    # 输出1个风险价值：VaR
    def Days_Test(self,dict_data,func, pca, same_weight,before_days,way,mode,num_list=[2, 3, 4, 5, 6, 7, 8, 9],choice=0):
        date, Original_code, discount = dict_data['date'], dict_data['stk_id'], 1-dict_data['discount']
        # 先评估历史的结果，历史的跟踪误差，与从历史的角度看能否参与
        history_hedge_list = dict_data['hedge_list'][0]['hedge_list'][choice:]

        if len(history_hedge_list)< 1 :  # 如果能用的股票数量太少，不参与
            return None
        # 获取历史测试的样本数据
        history_data = {'stk_id':Original_code, 'date': date, 'discount': dict_data['discount'],'hedge_list': history_hedge_list}
        history_result = self.cal_history_result(history_data, func, pca, same_weight, before_days,way,mode, num_list=num_list)

        # 再评估滚动计算的未来结果
        rol_days = dict_data['param']['history_future_len'][1]
        if rol_days == 120: # 如果就是120日，则不需要滚动，直接出结果
            return history_result
        else:
            future_model_list = history_result.columns # 历史测算有多少参数
            future_dict_list = dict_data['hedge_list']
            future_trade,future_para = pd.DataFrame(columns=history_result.columns), pd.DataFrame(columns=history_result.columns)
            # 开始进行循环评估：
            for future_dict in future_dict_list:
                future_hedge_list = future_dict['hedge_list']
                start_date, end_date = future_dict['start_date'], future_dict['end_date']
                # 如果本次的对冲标的为空值，那么保留上一次的对冲标的
                if len(future_hedge_list) == 0:
                    trade_days = self.pct_chg.loc[start_date:end_date, Original_code].iloc[1:].dropna().index.to_list()
                    future_weighted_trade = pd.DataFrame(index=trade_days, columns=future_model_list)
                    for use_type in future_model_list:
                        future_weighted_trade[use_type] = self.pct_chg.loc[trade_days, Original_code] + (future_para[use_type].fillna(0) * self.pct_chg.loc[trade_days, future_para.index].fillna(0)).sum(axis=1)
                # 如果本次的对冲标不为空值，则：
                # （1）本次的包含了上次，且数量至少≥规定的数量（比如是3只个股对冲，那规定数量就是3）不变
                # （2）但如果上次的包含了本次的（就是数量变少了），变
                # 有两种情况，本次的包含了上次，不变；但如果上次的包含了本次的（就是数量变少了），那么可以不变，也可以变）
                else:
                    future_newpara = self.cal_future_result(future_dict,future_model_list,Original_code,choice,func, pca, same_weight,before_days)
                    # 判断到底哪些参数需要调整
                    need_change = pd.Series(index =future_model_list)
                    for use_type in future_model_list:
                        flag = [code in future_hedge_list for code in future_para[use_type].dropna().index]  # 里面是True，False
                        flag = 0 if len(future_para) == 0 else min(flag)  # flag=0表示需要更换（初始化，或者是存在标的不在新入选的个股当中）
                        if (flag == 1) & (len(future_para) == 3):  # 首先是有参数，如果没有参数肯定是第一次;flag=1表明本次的选出的结果包含在在上次的结果中；不用变
                            need_change.loc[use_type] = False
                        else:
                            need_change.loc[use_type] = True
                    # 把需要更换的参数换成当前的，不需要更换的保留
                    need_change_way = ((need_change==True) & (future_newpara.isna().sum()<len(future_newpara)))
                    need_change_way = need_change_way[need_change_way==True].index.to_list()
                    no_change_way = list(set(future_model_list).difference(need_change_way))

                    next_para = pd.DataFrame(index=set(future_newpara.index).union(future_para.index),columns=future_model_list)
                    next_para[need_change_way] = future_newpara[need_change_way]
                    next_para[no_change_way] = future_para[no_change_way]
                    future_para = next_para.dropna(how='all')
                    # 然后计算这一轮的跟踪结果
                    trade_days = self.pct_chg.loc[start_date:end_date, Original_code].iloc[1:].dropna().index.to_list()
                    future_weighted_trade = pd.DataFrame(index=trade_days,columns=future_model_list)
                    for use_type in future_model_list:
                        future_weighted_trade[use_type] = self.pct_chg.loc[trade_days, Original_code] + (future_para[use_type].fillna(0) * self.pct_chg.loc[trade_days, future_para.index].fillna(0)).sum(axis=1)

                future_trade = pd.concat([future_trade,future_weighted_trade])

        # 评估未来的跟踪误差
        weighted_future_error, weighted_future_maxerror = cal_future_trade_result(future_trade/ 100)

        history_result.loc['rol_future_error'] = round(weighted_future_error,4)
        history_result.loc['rol_future_maxerror'] = round(weighted_future_maxerror,4)

        return history_result

    def RolDays_Test(self,factor_data,func, pca, same_weight,before_days,way,mode,num_list,choice):
        result_list = pd.DataFrame()
        pbar = tqdm(range(len(factor_data)))
        for idx in pbar:
            dict_data = factor_data[idx]
            pbar.set_description('并行生成中|%s|%s' % (dict_data['stk_id'], dict_data['date']))
            ret = self.Days_Test(dict_data,func, pca, same_weight,before_days,way,mode,num_list,choice)
            if type(ret) == pd.core.frame.DataFrame:
                result_list = pd.concat([result_list, ret.unstack()], axis=1)
        return result_list

    def Rol_AllResult(self,factor_name, choice=0, func='error', pca=False, same_weight='False',before_days=120,way='net', mode=['real','var'],
                      num_list=[2, 3, 4, 5, 6, 7, 8, 9],run='multi', save_name=''):
        # 第一步：读取数据，和对应的标的
        factor = pd.read_pickle(self.read_path + factor_name + '.pkl')
        if run == 'single':  # 单进程
            Data_Result = pd.DataFrame()
            for dict_data in tqdm(factor):
                all_result = self.Days_Test(dict_data,func, pca, same_weight,before_days,way,mode,num_list,choice)
                if type(all_result) == pd.core.frame.DataFrame:
                    Data_Result = pd.concat([Data_Result, all_result.unstack()], axis=1)

            Data_Result = Data_Result.T.reset_index().drop('index',axis=1)

        else:  # 多进程
            Data_Result = pd.DataFrame()
            ret_dict = multiprocess(24, self.RolDays_Test,factor,func, pca, same_weight,before_days,way,mode,num_list,choice)
            for k in ret_dict:
                Data_Result = pd.concat([Data_Result, ret_dict[k].get()], axis=1)

            Data_Result = Data_Result.T.reset_index().drop('index', axis=1)

        # 开始进行结果统计
        all_statistic_data, buy_statistic_data = self.GetTradeResult(Data_Result)

        writer = pd.ExcelWriter(self.save_path + factor_name + save_name + '.xlsx')
        all_statistic_data.to_excel(writer, sheet_name='整体统计结果')
        buy_statistic_data.to_excel(writer, sheet_name='交易统计结果')
        Data_Result.to_excel(writer, sheet_name='单笔结果')
        writer.save()
        send_file(self.save_path + factor_name + save_name + '.xlsx')

        return all_statistic_data, buy_statistic_data




            # 针对单一结果的可行性分析

    ##################### 评估指标 ############################
    # 给定样本，获取结果
    def GetTradeResult(self,Data_Result):
        # 开始进行结果统计
        use_model = list(Data_Result.columns.levels[0])
        use_model.remove('index')

        all_statistic_data = pd.DataFrame(index=['num', 'history_corr','history_error', 'history_maxerror', 'future_corr', 'future_error', 'future_maxerror'], columns=use_model)
        buy_statistic_data = pd.DataFrame(index=['num', 'history_corr','history_error', 'history_maxerror', 'future_corr', 'future_error', 'future_maxerror'], columns=use_model)
        for single_use in use_model:
            ####################################### 先统计全部样本 ############################################
            model_result = Data_Result[single_use].dropna(how='all')
            # 汇总跟踪结果
            all_statistic_data.loc['num', single_use] = len(model_result)
            all_statistic_data.loc[['history_corr', 'history_error', 'history_maxerror', 'future_corr', 'future_error','future_maxerror'], single_use] = \
                abs(model_result[['history_corr', 'history_error', 'history_maxerror', 'future_corr', 'future_error','future_maxerror']].astype(float)).quantile(0.5).round(4)
            if 'rol_future_error' in model_result.columns:
                all_statistic_data.loc[['rol_future_error', 'rol_future_maxerror'], single_use] = \
                    abs(model_result[['rol_future_error', 'rol_future_maxerror']].astype(float)).quantile(0.5).round(4)
                # 开始统计收益：profit为实际收益,ls_profit为多空收益
                model_result['profit'] = model_result['rol_future_error'] + model_result['discount'] - 0.05
                model_result['ls_profit'] = model_result['rol_future_error'].copy()
            else:
                model_result['profit'] = model_result['future_error'] + model_result['discount'] - 0.05
                model_result['ls_profit'] = model_result['future_error'].copy()

            all_statistic_data.loc['10%ls_profit', single_use] = round(model_result['ls_profit'].quantile(0.1), 4)
            all_statistic_data.loc['30%ls_profit', single_use] = round(model_result['ls_profit'].quantile(0.3), 4)
            all_statistic_data.loc['50%ls_profit', single_use] = round(model_result['ls_profit'].quantile(0.5), 4)
            all_statistic_data.loc['70%ls_profit', single_use] = round(model_result['ls_profit'].quantile(0.7), 4)
            all_statistic_data.loc['90%ls_profit', single_use] = round(model_result['ls_profit'].quantile(0.9), 4)
            all_statistic_data.loc['ls_win_rate', single_use] = round((model_result['ls_profit'] > 0).sum() / len(model_result['ls_profit']), 4)
            all_statistic_data.loc['ls_wl_rate', single_use] = round(-model_result['ls_profit'][model_result['ls_profit'] > 0].mean() / model_result['ls_profit'][model_result['ls_profit'] < 0].mean(), 2)

            all_statistic_data.loc['10%profit', single_use] = round(model_result['profit'].quantile(0.1), 4)
            all_statistic_data.loc['30%profit', single_use] = round(model_result['profit'].quantile(0.3), 4)
            all_statistic_data.loc['50%profit', single_use] = round(model_result['profit'].quantile(0.5), 4)
            all_statistic_data.loc['70%profit', single_use] = round(model_result['profit'].quantile(0.7), 4)
            all_statistic_data.loc['90%profit', single_use] = round(model_result['profit'].quantile(0.9), 4)
            all_statistic_data.loc['win_rate', single_use] = round((model_result['profit'] > 0).sum() / len(model_result['profit']), 4)
            all_statistic_data.loc['wl_rate', single_use] = round(-model_result['profit'][model_result['profit'] > 0].mean() / model_result['profit'][model_result['profit'] < 0].mean(), 2)

            ####################################### 再统计叠加折扣后的收益结果 ############################################
            canbuy_result = model_result[model_result['if_trade'] == True]

            # 汇总跟踪结果
            buy_statistic_data.loc['num', single_use] = len(canbuy_result)
            buy_statistic_data.loc[['history_corr', 'history_error', 'history_maxerror', 'future_corr', 'future_error',
                                    'future_maxerror'], single_use] = \
                abs(canbuy_result[['history_corr', 'history_error', 'history_maxerror', 'future_corr', 'future_error',
                                  'future_maxerror']].astype(float)).quantile(0.5).round(4)
            if 'rol_future_error' in canbuy_result.columns:
                buy_statistic_data.loc[['rol_future_error', 'rol_future_maxerror'], single_use] = \
                    abs(canbuy_result[['rol_future_error', 'rol_future_maxerror']].astype(float)).quantile(0.5).round(4)
                # 开始统计收益：profit为实际收益,ls_profit为多空收益
                canbuy_result['profit'] = canbuy_result['rol_future_error'] + canbuy_result['discount'] - 0.05
                canbuy_result['ls_profit'] = canbuy_result['rol_future_error'].copy()
            else:
                canbuy_result['profit'] = canbuy_result['future_error'] + canbuy_result['discount'] - 0.05
                canbuy_result['ls_profit'] = canbuy_result['future_error'].copy()

            buy_statistic_data.loc['10%ls_profit', single_use] = round(canbuy_result['ls_profit'].quantile(0.1), 4)
            buy_statistic_data.loc['30%ls_profit', single_use] = round(canbuy_result['ls_profit'].quantile(0.3), 4)
            buy_statistic_data.loc['50%ls_profit', single_use] = round(canbuy_result['ls_profit'].quantile(0.5), 4)
            buy_statistic_data.loc['70%ls_profit', single_use] = round(canbuy_result['ls_profit'].quantile(0.7), 4)
            buy_statistic_data.loc['90%ls_profit', single_use] = round(canbuy_result['ls_profit'].quantile(0.9), 4)
            buy_statistic_data.loc['ls_win_rate', single_use] = round((canbuy_result['ls_profit'] > 0).sum() / len(canbuy_result['ls_profit']), 4)
            buy_statistic_data.loc['ls_wl_rate', single_use] = round(-canbuy_result['ls_profit'][canbuy_result['ls_profit'] > 0].mean() / canbuy_result['ls_profit'][canbuy_result['ls_profit'] < 0].mean(), 2)

            buy_statistic_data.loc['10%profit', single_use] = round(canbuy_result['profit'].quantile(0.1), 4)
            buy_statistic_data.loc['30%profit', single_use] = round(canbuy_result['profit'].quantile(0.3), 4)
            buy_statistic_data.loc['50%profit', single_use] = round(canbuy_result['profit'].quantile(0.5), 4)
            buy_statistic_data.loc['70%profit', single_use] = round(canbuy_result['profit'].quantile(0.7), 4)
            buy_statistic_data.loc['90%profit', single_use] = round(canbuy_result['profit'].quantile(0.9), 4)
            buy_statistic_data.loc['win_rate', single_use] = round((canbuy_result['profit'] > 0).sum() / len(canbuy_result['profit']), 4)
            buy_statistic_data.loc['wl_rate', single_use] = round( -canbuy_result['profit'][canbuy_result['profit'] > 0].mean() / canbuy_result['profit'][canbuy_result['profit'] < 0].mean(), 2)

        return all_statistic_data,buy_statistic_data
    # 按照不同年份划分
    def Get_Difference_Year(self,Data_Result):
        use_model = list(Data_Result.columns.levels[0])
        use_model.remove('index')
        # 确定一共有多少年
        year_list = (Data_Result[use_model[0]]['trade_date']//10000).drop_duplicates().dropna().to_list()
        # 分年度测算
        all_data = dict()
        buy_data = dict()
        for year in year_list:
            year_result = Data_Result.loc[(Data_Result[use_model[0]]['trade_date'] // 10000)[(Data_Result[use_model[0]]['trade_date'] // 10000)==year].index]
            year_all_data,year_buy_data = self.GetTradeResult(year_result)
            all_data[year] = year_all_data
            buy_data[year] = year_buy_data

        return all_data,buy_data

    def Get_Difference_Industry(self,Data_Result,if_year=False):
        use_model = list(Data_Result.columns.levels[0])
        use_model.remove('index')
        # 确定一共有多少个行业
        SW1 = getData.get_daily_1factor('SW1')

        code_ind = Data_Result[use_model[0]][['code','trade_date']]
        code_ind['ind'] = pd.Series(code_ind.index).apply(
        lambda x: indName.sw_level1[SW1.loc[code_ind.loc[x, 'trade_date'], code_ind.loc[x, 'code']]] if np.isnan(code_ind.loc[x, 'trade_date'])==False else np.nan)

        ind_list = code_ind['ind'].dropna().drop_duplicates().to_list()

        all_data = dict()
        buy_data = dict()
        for ind in ind_list:
            ind_result = Data_Result.loc[code_ind['ind'][code_ind['ind']==ind].index]
            if if_year == False:
                ind_all_data, ind_buy_data = self.GetTradeResult(ind_result)
                all_data[ind] = ind_all_data
                buy_data[ind] = ind_buy_data
            else:
                self.Get_Difference_Year(ind_result)
                all_data[ind] = ind_all_data
                buy_data[ind] = ind_buy_data

        return all_data,buy_data

    ########################################## 对于给到的个股和列表，计算其需要的折扣 #######################################################
    # 只考虑是否参与，并不关心未来情况：
    def TradeOrNot(self,prepare_date,func,pca, same_weight,before_days=120,mode=['trade_real', 'var'],if_new=False):
        # 先输出申万一级行业
        SW_ind = getData.get_daily_1factor('SW1')

        trade_result = pd.DataFrame(columns=['code', 'date', 'hedge_list', 'profit', 'weight','single_amt','all_amt'])
        i = 0
        trade_range = get_trade_days(prepare_date, trade_days=120, delay=0, type='history')
        s = FactorData()
        trade_date = s.get_factor_value('WIND_AShareCalendar', factors=['TRADE_DAYS']).sort_values(by='TRADE_DAYS').drop_duplicates().astype(int)
        date = trade_date['TRADE_DAYS'][trade_date['TRADE_DAYS'] > prepare_date].iloc[0] # 假设的成交日期
        # 目前分为三组：第一组，样本阈值80%-100%，对冲阈值80%-100%，用前3个对冲
        factor_date = trade_date['TRADE_DAYS'][trade_date['TRADE_DAYS'] > prepare_date].iloc[1]
        factor_name = '新版本_7_(0.8, 1)_(0.8, 1)_(120, 120)_95_'+str(factor_date)+'_'+str(factor_date)+'_part1_result'
        if os.path.exists(factor_name)==True:
            factor_80 = pd.read_pickle(self.read_path + factor_name + '.pkl')
            for dict_data in tqdm(factor_80):
                Original_code, similarity_list = dict_data['stk_id'], dict_data['hedge_list'][0]['hedge_list']
                if len(similarity_list)<2:
                    continue
                code_trade_range = self.pct_chg.loc[trade_range,Original_code].dropna().index.to_list()
                # 开始用历史数据拟合结果
                cal_dict_data = dict({'date': date, 'stk_id': Original_code, 'hedge_list': similarity_list[:3]})
                profit_need = []
                para1 = self.CurveFitting_LeastSquares(cal_dict_data, func, pca, same_weight, before_days)
                weighted_trade = (self.pct_chg.loc[code_trade_range, Original_code] + (
                            para1 * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)) / 100  # 加权
                if_trade = self.Risk_Estimation(weighted_trade, profit=0.05, c=0.95, mode=mode)
                profit_need.append(self.need_profit)
                # 再用mean_var，看看能否参与
                try:
                    para2 = self.AssetAllocation_MeanVariance(cal_dict_data, func, pca, same_weight, before_days)
                    weighted_trade = self.pct_chg.loc[code_trade_range, Original_code] + (
                                para2 * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)  # 加权
                    if_trade = self.Risk_Estimation(weighted_trade / 100, profit=0.05, c=0.95, mode=mode)
                    profit_need.append(self.need_profit)
                except:
                    print('均值方差法无解')

                if profit_need.index(min(profit_need)) == 0:
                    para = para1.copy()
                else:
                    para = para2.copy()

                # 开始写入数据
                ind = indName.sw_level1[SW_ind.loc[prepare_date, Original_code]]
                if (ind == '银行') or (ind == '非银金融'):
                    single_amt = 2000
                    all_amt = 6000
                else:
                    single_amt = 2000
                    all_amt = 2000

                trade_result.loc[i] = Original_code, date, similarity_list[:7], min(profit_need), list(round(para, 4)),single_amt,all_amt
                i += 1

        # 第二组，样本阈值80%-100%，对冲阈值60%-100%，用前4个对冲
        factor_name = '新版本_7_(0.6, 1)_(0.8, 1)_(120, 120)_95_' + str(factor_date) + '_' + str(factor_date) + '_part2_result'
        if os.path.exists(factor_name)==True:
            factor_70 = pd.read_pickle(self.read_path + factor_name + '.pkl')
            for dict_data in tqdm(factor_70):
                Original_code, similarity_list = dict_data['stk_id'], dict_data['hedge_list'][0]['hedge_list']
                if len(similarity_list)<2:
                    continue
                code_trade_range = self.pct_chg.loc[trade_range,Original_code].dropna().index.to_list()
                # 开始用历史数据拟合结果
                cal_dict_data = dict({'date': date, 'stk_id': Original_code, 'hedge_list': similarity_list[:4]})
                profit_need = []
                para1 = self.CurveFitting_LeastSquares(cal_dict_data, func, pca, same_weight, before_days)
                weighted_trade = (self.pct_chg.loc[code_trade_range, Original_code] + (
                            para1 * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)) / 100  # 加权
                if_trade = self.Risk_Estimation(weighted_trade, profit=0.05, c=0.95, mode=mode)
                profit_need.append(self.need_profit)
                # 再用mean_var，看看能否参与
                try:
                    para2 = self.AssetAllocation_MeanVariance(cal_dict_data, func, pca, same_weight, before_days)
                    weighted_trade = self.pct_chg.loc[code_trade_range, Original_code] + (
                                para2 * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)  # 加权
                    if_trade = self.Risk_Estimation(weighted_trade / 100, profit=0.05, c=0.95, mode=mode)
                    profit_need.append(self.need_profit)
                except:
                    print('均值方差法无解')

                if profit_need.index(min(profit_need)) == 0:
                    para = para1.copy()
                else:
                    para = para2.copy()

                # 开始写入数据
                ind = indName.sw_level1[SW_ind.loc[prepare_date, Original_code]]
                if (ind == '银行') or (ind == '非银金融'):
                    single_amt = 2000
                    all_amt = 6000
                else:
                    single_amt = 2000
                    all_amt = 2000

                trade_result.loc[i] = Original_code, date, similarity_list[:7], min(profit_need), list(round(para, 4)),single_amt,all_amt
                i += 1

        # 第三组，样本阈值70%-80%，对冲阈值60%-80%，用前5个对冲
        factor_name = '新版本_7_(0.6, 1)_(0.7, 0.8)_(120, 120)_95_' + str(factor_date) + '_' + str(factor_date) + '_part3_result'
        if os.path.exists(factor_name) == True:
            factor_60 = pd.read_pickle(self.read_path + factor_name + '.pkl')
            for dict_data in tqdm(factor_60):
                Original_code, similarity_list = dict_data['stk_id'], dict_data['hedge_list'][0]['hedge_list']
                if len(similarity_list) < 2:
                    continue
                code_trade_range = self.pct_chg.loc[trade_range, Original_code].dropna().index.to_list()
                # 开始用历史数据拟合结果
                cal_dict_data = dict({'date': date, 'stk_id': Original_code, 'hedge_list': similarity_list[:5]})
                profit_need = []
                para1 = self.CurveFitting_LeastSquares(cal_dict_data, func, pca, same_weight, before_days)
                weighted_trade = (self.pct_chg.loc[code_trade_range, Original_code] + (
                        para1 * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)) / 100  # 加权
                if_trade = self.Risk_Estimation(weighted_trade, profit=0.05, c=0.95, mode=mode)
                profit_need.append(self.need_profit)
                # 再用mean_var，看看能否参与
                try:
                    para2 = self.AssetAllocation_MeanVariance(cal_dict_data, func, pca, same_weight, before_days)
                    weighted_trade = self.pct_chg.loc[code_trade_range, Original_code] + (
                            para2 * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)  # 加权
                    if_trade = self.Risk_Estimation(weighted_trade / 100, profit=0.05, c=0.95, mode=mode)
                    profit_need.append(self.need_profit)
                except:
                    print('均值方差法无解')

                if profit_need.index(min(profit_need)) == 0:
                    para = para1.copy()
                else:
                    para = para2.copy()

                # 开始写入数据
                ind = indName.sw_level1[SW_ind.loc[prepare_date, Original_code]]
                if (ind == '银行') or (ind == '非银金融'):
                    single_amt = 1000
                    all_amt = 3000
                else:
                    single_amt = 1000
                    all_amt = 1000

                trade_result.loc[i] = Original_code, date, similarity_list[:7], min(profit_need), list(round(para, 4)),single_amt,all_amt
                i += 1

        # 最后一步，格式调整和转换
        s = FactorData()
        Stock_Name = s.get_factor_value('Basic_factor', [], [datetime.datetime.now().strftime('%Y%m%d')],['short_name'])['short_name']
        New_Result = pd.DataFrame(columns=['大宗代码', '大宗名称','月最高规模（万）','单笔规模（万）', '所需折扣','对冲标的代码','对冲标的名称','对冲标的权重'])
        i = 0
        for index in trade_result.index:
            dz_code = stockList.trans_int2windcode(trade_result.loc[index, 'code'])
            dc_code = trade_result.loc[index, 'hedge_list']
            profit = trade_result.loc[index, 'profit']
            dc_weight = trade_result.loc[index, 'weight']
            dc_weight = pd.Series(dc_weight,index=dc_code[:len(dc_weight)]).reindex(dc_code)
            single_amt = trade_result.loc[index, 'single_amt']
            all_amt = trade_result.loc[index, 'all_amt']

            for code in dc_code:
                New_Result.loc[i] = dz_code, Stock_Name.loc[dz_code],all_amt,single_amt, round(1 - profit, 4),\
                                    stockList.trans_int2windcode(code), Stock_Name.loc[stockList.trans_int2windcode(code)],\
                                    dc_weight.loc[code]

                i+=1

        New_Result = New_Result.set_index(['大宗代码', '大宗名称','月最高规模（万）','单笔规模（万）','所需折扣','对冲标的代码'])

        tomorrow = get_trade_days(prepare_date, trade_days=2, delay=0, type='future')[1]
        if if_new == False:  # 如果是重新筛选，则按照最新的结果直接使用
            block_data = pd.read_pickle('/data/group/800442/800319/Afengchi/SimiStock/tracking/'+str(tomorrow)+'_block_data.pkl')
            yesterday_result = pd.read_excel('/data/group/800442/800319/Afengchi/SimiStock/大宗组合/'+str(prepare_date)+'对冲标的筛选结果.xlsx')
            yesterday_result['对冲标的权重'] = yesterday_result['对冲标的权重'].fillna(0)
            yesterday_result = yesterday_result.fillna(method='ffill')

            yesterday_stay_result = yesterday_result[yesterday_result['大宗名称'].isin(block_data['股票名称'])].set_index(['大宗代码', '大宗名称','月最高规模（万）','单笔规模（万）','所需折扣','对冲标的代码'])
            yesterday_stay_result = yesterday_stay_result.replace(0,np.nan)

            New_Result = pd.concat([yesterday_stay_result,New_Result])

        New_Result.to_excel('/data/group/800442/800319/Afengchi/SimiStock/大宗组合/' + str(tomorrow) + '对冲标的筛选结果.xlsx')
        send_file('/data/group/800442/800319/Afengchi/SimiStock/大宗组合/' + str(tomorrow) + '对冲标的筛选结果.xlsx')

        return New_Result
    # 借用近期的历史大宗成交数据，判断我们能否参与
    def TradeByData(self,factor_name,func,pca, same_weight,before_days, mode=['real', 'var']):
        # 获取个股名称
        s = FactorData()
        Stock_Name = s.get_factor_value('Basic_factor', [], [datetime.datetime.now().strftime('%Y%m%d')], ['short_name'])['short_name']

        trade_factor = pd.read_pickle(self.read_path + factor_name + '.pkl')
        trade_result = pd.DataFrame(columns=['code','name', 'date', 'profit','if_trade'])
        i = 0

        for dict_data in tqdm(trade_factor):
            Original_code, similarity_list = dict_data['stk_id'], dict_data['hedge_list'][0]['hedge_list']
            date = dict_data['date']
            profit = 1-dict_data['discount']
            trade_range = get_trade_days(date, trade_days=120, delay=0, type='history')
            code_trade_range = self.pct_chg.loc[trade_range, Original_code].dropna().index.to_list()
            # 开始用历史数据拟合结果
            cal_dict_data = dict({'date': date, 'stk_id': Original_code, 'hedge_list': similarity_list[:3]})
            profit_need = []
            # 先用curve，看是否能够参与
            para = self.CurveFitting_LeastSquares(cal_dict_data, func, pca, same_weight, before_days)
            weighted_trade = (self.pct_chg.loc[code_trade_range, Original_code] + (
                        para * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1)) / 100  # 加权
            if_trade = self.Risk_Estimation(weighted_trade, profit=profit, c=0.95, mode=mode)
            profit_need.append(if_trade)
            # 再用mean_var，看看能否参与
            try:
                para = self.AssetAllocation_MeanVariance(cal_dict_data, func, pca, same_weight, before_days)
                weighted_trade = (self.pct_chg.loc[code_trade_range, Original_code] + (
                            para * self.pct_chg.loc[code_trade_range, similarity_list].fillna(0)).sum(axis=1))/ 100  # 加权
                if_trade = self.Risk_Estimation(weighted_trade, profit=profit, c=0.95, mode=mode)
                profit_need.append(if_trade)
            except:
                print('均值方差法无解')

            # 开始写入数据
            trade_result.loc[i] = stockList.trans_int2windcode(Original_code),Stock_Name.loc[stockList.trans_int2windcode(Original_code)] ,date,profit, max(profit_need)
            i += 1

        return trade_result
    # 模拟跟踪情况
    def FakeTrade(self,end_date):
        trade_track = pd.DataFrame(columns=['大宗代码','大宗名称','大宗折扣','参与规模','参与日期'])
        money_track = pd.DataFrame()
        i=0
        read_path = '/data/group/800442/800319/Afengchi/SimiStock/大宗组合/'
        trade_result = pd.read_excel(read_path + '模拟跟踪.xlsx')
        for index in trade_result.index:
            code = trade_result.loc[index,'大宗代码']
            code_name = trade_result.loc[index, '大宗名称']
            Original_code = stockList.trans_windcode2int(code)
            profit = trade_result.loc[index,'参与折扣']
            trade_date = trade_result.loc[index,'参与日期']

            weight_choice = pd.read_excel(read_path+str(trade_date)+'对冲标的筛选结果.xlsx')
            weight_choice['大宗代码'] = weight_choice['大宗代码'].fillna(method='ffill')

            code_result = weight_choice[weight_choice['大宗代码'] == code]
            para = code_result[['对冲标的代码','对冲标的名称','对冲标的权重']].dropna()
            para['对冲标的代码'] = para['对冲标的代码'].apply(lambda x:stockList.trans_windcode2int(x))
            para = para.set_index('对冲标的代码')['对冲标的权重']
            similarity_list = para.index.to_list()
            code_amt = code_result['单笔规模（万）'].iloc[0]

            start_date = get_trade_days(trade_date, trade_days=2, delay=0, type='future')[1]

            weighted_trade = self.pct_chg.loc[start_date:end_date,Original_code] + (para * self.pct_chg.loc[start_date:end_date,similarity_list].fillna(0)).sum(axis=1)
            long_amt = (1+self.pct_chg.loc[start_date:end_date,Original_code]/100).cumprod()
            long_amt = long_amt.shift(1).fillna(1) * code_amt

            all_money = (weighted_trade/100 * long_amt).cumsum()
            all_money.loc[trade_date] = code_amt*(1-profit)
            all_money = pd.DataFrame(all_money.sort_index(),columns=[i])

            trade_track.loc[i] = code, code_name, profit,code_amt,trade_date
            money_track = round(pd.concat([money_track,all_money],axis=1),2)
            i+=1

        # 统计收益和偏离情况
        all_track = pd.concat([trade_track,money_track.T],axis=1)
        return all_track
    # 开始统计一下有效数据
    # def get_example(self):
    #     # 1、测算全体大宗个股的行业分布
    #     SW1 = getData.get_daily_1factor('SW1')
    #
    #     block_data95 = pd.read_pickle('/data/group/800442/800319/Afengchi/SimiStock/block_data/block_data_95.pkl').reset_index().drop('index',axis=1)
    #     block_data95['所属行业'] = pd.Series(block_data95.index).apply(lambda x: indName.sw_level1[SW1.loc[block_data95.loc[x, '交易日期'], block_data95.loc[x, '股票代码']]] if np.isnan(
    #             block_data95.loc[x, '交易日期']) == False else np.nan)
    #
    #     block_data95 = block_data95[block_data95['交易日期']<=20201231]
    #     block_ind_count = block_data95.groupby('所属行业')['股票代码'].count()
    #     # 2、对于筛选结果的行业分布
    #     factor_name = '新版本_14_(0.6, 0.8)_(0.7, 0.8)_(120, 120)_95_20170101_20201231_result'
    #     factor = pd.read_pickle(self.read_path + factor_name + '.pkl')
    #
    #     trade_data = pd.DataFrame(columns=['交易日期','股票代码','所属行业'])
    #     i=0
    #     for data in factor:
    #         trade_data.loc[i,'交易日期'] = data['date']
    #         trade_data.loc[i,'股票代码'] = data['stk_id']
    #         trade_data.loc[i, '所属行业'] =indName.sw_level1[SW1.loc[data['date'],data['stk_id']]]
    #         i+=1
    #     trade_ind_count = trade_data.groupby('所属行业')['股票代码'].count()
    #
    #     ind_result = pd.concat([block_ind_count,trade_ind_count],axis=1)
    #     ind_result.columns = ['全部样本','筛选样本']
    #     ind_result = ind_result.sort_values(by='全部样本',ascending=False)
    #
    #     ind_result.to_excel('/data/user/015624/结果.xlsx')
    #     send_file('/data/user/015624/结果.xlsx')
    #
    #
    #
    #
    #
    #
    #
    #     # 评估个股的行业归属
    #     trade_result = Data_Result['3_curve'][Data_Result['3_curve']['if_trade'] == True]
    #     code_result = Data_Result.loc[trade_result.index, ['code', 'date', 'discount']]
    #     code_result.columns = ['code', 'date', 'discount']
    #     SW1 = getData.get_daily_1factor('SW1')
    #
    #     trade_result[['code', 'date', 'discount']] = code_result[['code', 'date', 'discount']]
    #     trade_result = trade_result.reset_index().drop('index', axis=1)
    #     trade_result['ind'] = pd.Series(code_result.index).apply(
    #         lambda x: indName.sw_level1[SW1.loc[code_result.loc[x, 'date'], code_result.loc[x, 'code']]])
    #     trade_result['future_error_abs'] = abs(trade_result['future_error'])
    #     trade_result['profit'] = trade_result['discount'] + trade_result['future_error'] - 0.05
    #
    #     ind_result = pd.DataFrame(index=set(trade_result['ind']),
    #                               columns=['num', 'history_error', 'history_maxerror', 'future_maxerror'])
    #     ind_result['num'] = trade_result['ind'].value_counts()  # 行业分布
    #     ind_result[['history_error', 'history_maxerror', 'future_maxerror']] = \
    #         round(trade_result.groupby('ind')[['history_error', 'history_maxerror', 'future_maxerror']].quantile(0.5),4)
    #     for weight in [0.1, 0.3, 0.5, 0.7, 0.9]:
    #         ind_result[['future_error_abs' + str(weight), 'profit' + str(weight)]] = trade_result.groupby('ind')[
    #             ['future_error_abs', 'profit']].quantile(weight)
    #
    #     ind_result = ind_result.sort_values(by='num', ascending=False)
    #     ind_result.to_excel('/data/user/015624/temproary_inddata.xlsx')
    #     send_file('/data/user/015624/temproary_inddata.xlsx')
    #
    #     # 评估：不同方法，历史跟踪误差与未来跟踪误差之间的关联
    #     index_list = ['1_code_result', '1_curve', '1_meanvar',
    #                   '2_code_result', '2_curve', '2_meanvar',
    #                   '3_code_result', '3_curve', '3_meanvar',
    #                   '4_code_result', '4_curve', '4_meanvar']
    #     profit_range = pd.DataFrame(index=[0.1, 0.3, 0.5, 0.7, 0.9], columns=index_list)
    #     for ways in index_list:
    #         trade_result = Data_Result[ways][Data_Result[ways]['if_trade'] == True]
    #         trade_result['discount'] = Data_Result.loc[trade_result.index, 'discount']
    #         real_profit = (trade_result['discount'] + trade_result['future_error'] - 0.05)
    #         for i in [0.1, 0.3, 0.5, 0.7, 0.9]:
    #             profit_range.loc[i, ways] = real_profit.quantile(i)
    #
    #         profit_range.loc['胜率', ways] = (real_profit > 0).sum() / len(real_profit)
    #         profit_range.loc['盈亏比', ways] = - real_profit[real_profit > 0].mean() / real_profit[real_profit < 0].mean()
    #         profit_range.loc['平均收益',ways] = real_profit.mean()
    #     profit_range.to_excel('/data/user/015624/temproary_data.xlsx')
    #     send_file('/data/user/015624/temproary_data.xlsx')

now_date = int(datetime.datetime.now().strftime('%Y%m%d'))  # 获取今天日期
self = WeightedConfiguration(20160101, int(now_date), before_days=120, after_days=120)
#factor_name = '叠加风格5_14_0.8_v3_95_20180101_20200630_result'

# 可调节参数：
choice = 0  # choice：表明从第几个开始挑选
func = 'error'  # 'error','sumerror' 使用每日收益率误差，还是累计收益率误差
pca = False  # True,False 是否正则化
same_weight = True # True,False 是否多空权重保持一致，且必须全部为空头
before_days = 120 # 使用历史多少日数据进行训练
way = 'net' # net,long_net,first_net,situation_net  多空净值法，多头净值配平法，首日配平法，异常（即多空偏离超过0.1）配平法
num_list = [2,3,4,5,6,7] # 即测试多少个参数的对冲标的
mode = ['trade_real','var']  # real,trade_real,history,time_history,var 实际最大跟踪误差，实际跟踪误差，历史法，历史时间加权法，var

# 运行普通的结果：
factor_name = '叠加K线相似度_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20170101_20201231_result'

factor = pd.read_pickle(self.read_path + factor_name + '.pkl')
self.Test_Difference_Time(factor, func, pca, same_weight, before_days, way, mode, num_list,choice, if_ind=None)

#
# ########################## 新出的跟踪大宗结果 ####################################
# prepare_date = 20220428 # 昨天，比如今天上午收到大宗，这个日期为昨天
# if_new = False # if_new表示含义：即是否重新输出结果，还是用以前的加总
# New_Result = self.TradeOrNot(prepare_date,func='error',pca=False, same_weight=False,before_days=120,mode=['trade_real', 'var'],if_new=if_new)
#
#
# ######################### 模拟跟踪结果 #############################
# # 跟踪实盘交易
# end_date = 20220428
# all_track = self.FakeTrade(end_date)
# all_track.to_excel('模拟跟踪结果.xlsx')
# send_file('模拟跟踪结果.xlsx')
#
#
#
# # 根据最近实际成交个股的拟合
# factor_name = '新版本_14_(0.6, 1)_(0.8, 1)_(120, 120)_95_20220315_20220415_result_noSZ50'
# trade_result = self.TradeByData(factor_name,func,pca, same_weight,before_days, mode)
# trade_result.to_excel('实际交易结果-80%阈值严格版本.xlsx')
# send_file('实际交易结果-80%阈值严格版本.xlsx')
# trade_result['if_trade'].sum()

# -*- coding:UTF-8 -*-

import numpy as np
import pandas as pd
import copy
from scipy import optimize
import matplotlib.pyplot as plt
from matplotlib import cm


class Snowball:
    # maturity单位为年, 每年包含的天数记为ndays_year, S_0默认为1
    def __init__(self, knock_out, knock_in, observation_days, maturity, ndays_year, nominal_principle, r, q,
                 sigma, S0=1):
        self.knock_out = knock_out
        self.knock_in = knock_in
        self.observation_days = observation_days
        self.maturity = maturity
        self.ndays_year = ndays_year
        self.nominal_principle = nominal_principle
        self.r = r
        self.q = q
        self.sigma = sigma
        self.S0 = S0
        self.base_gbm_path = None  # 基础gbm路径，长度为maturity，初始值为1

    # 使用QMC种子加快MC收敛速度
    @staticmethod
    def _quasirandseed(filename, MC_lens, T_lens):
        QuasiRand = np.array(pd.read_pickle(filename))
        if MC_lens > len(QuasiRand):
            print(" MC length is too long!")
        RandSeed = QuasiRand[:MC_lens, :T_lens]
        return RandSeed

    # 生成正态随机数种子
    def gen_normal_seed(self, N_path, n_timestep, filename='', MCMethod='', seed=None):
        if MCMethod == "Sobol":
            epsilon = self._quasirandseed(filename, N_path, n_timestep)
        elif seed is not None:
            np.random.seed(seed)
            epsilon = np.random.randn(N_path, n_timestep)
        else:
            epsilon = np.random.randn(N_path, n_timestep)
        return epsilon

    # 由正态种子生成随机数
    def gen_gbm_from_seed(self, St, epsilon, sigma=None, q=None):
        dt = 1.0 / self.ndays_year
        v = sigma if sigma is not None else self.sigma
        q_ = q if q is not None else self.q
        S = np.exp((self.r - q_ - 0.5 * v ** 2) * dt + v * np.sqrt(dt) * epsilon)
        S = np.insert(S, 0, np.ones(epsilon.shape[0]), axis=1)  # 新增第一列全为1的值作为初始值
        S_paths = St * np.cumprod(S, axis=1)
        return S_paths

    # 生成指定初值、长度、轨道数的gbm路径
    def monte_carlo_gbm_path(self, St, N_path, n_timestep, filename='', MCMethod='', sigma=None, q=None, seed=None):
        epsilon = self.gen_normal_seed(N_path, n_timestep, filename=filename, MCMethod=MCMethod, seed=seed)
        return self.gen_gbm_from_seed(St, epsilon, sigma=sigma, q=q)

    # 为此雪球类生成以1为初值基础gbm路径，之后可复用
    def gen_base_gbm_path(self, N_path, filename='', MCMethod='', sigma=None, seed=None):
        self.base_gbm_path = self.monte_carlo_gbm_path(1, N_path, round(self.maturity * self.ndays_year),
                                                       filename=filename, MCMethod=MCMethod, sigma=sigma, seed=seed)

    # 计算单个日期的delta（返回delta向量）
    def delta(self, coupon, date_index, St_range, MC_paths=None, has_knocked_in=False):
        pv = []
        N_path = self.base_gbm_path.shape[0]
        n_timestep = round(self.maturity * self.ndays_year) - date_index
        MC_paths = MC_paths if MC_paths is not None else self.base_gbm_path
        MC_paths = MC_paths[:, :(n_timestep + 1)]
        for St in St_range:
            pv.append(self.monte_carlo_calculate_pv(St, coupon, N_path, n_timestep, has_knocked_in=has_knocked_in,
                                                    MC_paths=St * MC_paths))
        delta = np.diff(pv) / np.diff(St_range)
        return delta

    def calc_pv(self, coupon, date_index, St, has_knocked_in=False, MC_paths=None):
        MC_paths = MC_paths if MC_paths is not None else self.base_gbm_path
        N_path = MC_paths.shape[0]
        n_timestep = round(self.maturity * self.ndays_year) - date_index
        MC_paths = MC_paths[:, :(n_timestep + 1)]
        return self.monte_carlo_calculate_pv(St, coupon, N_path, n_timestep, has_knocked_in=has_knocked_in,
                                             MC_paths=St * MC_paths)

    # 计算delta，日期可以为单个日期（返回delta向量），也可以为一列日期（返回delta矩阵）
    def delta_matrix(self, coupon, date_index_range, St_range, MC_paths=None, has_knocked_in=False, parallel=False, batch=True):
        if str(date_index_range).isdigit():
            date_index_range = np.array([date_index_range])
        # 是否使用并行计算
        if parallel:
            from joblib import Parallel, delayed
            import multiprocessing as mp
            # 是否先单线程计算每日delta向量再并行计算
            if batch:
                delta_matrix = Parallel(n_jobs=mp.cpu_count())(
                    delayed(self.delta)(coupon, date_index, St_range, MC_paths=MC_paths, has_knocked_in=has_knocked_in) for date_index in
                    date_index_range)
                return np.array(delta_matrix)
            else:
                pv_matrix = Parallel(n_jobs=mp.cpu_count(), backend="threading")(
                    delayed(self.calc_pv)(coupon, date_index, St, MC_paths=MC_paths, has_knocked_in=has_knocked_in) for date_index in
                    date_index_range for St in St_range)
                pv_matrix = np.reshape(pv_matrix, (len(date_index_range), len(St_range)))
                return np.diff(pv_matrix)
        else:
            pv_matrix = []
            for date_index in date_index_range:
                pv = []
                for S in St_range:
                    pv.append(self.calc_pv(coupon, date_index, S, MC_paths=MC_paths, has_knocked_in=has_knocked_in))
                pv_matrix.append(pv)
            pv_matrix = np.array(pv_matrix)
            delta_matrix = np.diff(pv_matrix)
        return delta_matrix

    # 绘制delta曲线
    def delta_curve(self, coupon, date_index, St_range, has_knocked_in=False):
        delta = self.delta(coupon, date_index, St_range, has_knocked_in=has_knocked_in)
        plt.figure()
        plt.plot(St_range[:-1], delta)
        plt.xlabel('St')
        plt.ylabel('Delta')
        plt.show()
        return delta

    # 绘制delta曲面
    def delta_surface(self, coupon, date_index_range, St_range, has_knocked_in=False):
        delta_matrix = self.delta_matrix(self, coupon, date_index_range, St_range, has_knocked_in=has_knocked_in)
        x_mesh, y_mesh = np.meshgrid(St_range[:-1], date_index_range, indexing='ij')
        z_mesh = delta_matrix.T
        fig = plt.figure()
        sub = fig.add_subplot(111, projection='3d')
        sub.plot_surface(x_mesh, y_mesh, z_mesh, cmap=cm.jet)
        sub.set_xlabel(r'$St$')
        sub.set_ylabel(r'$time_to_maturity$')
        sub.set_zlabel(r'$delta$')
        plt.show()
        return delta_matrix

    # 计算gamma。通过broadcast机制，对delta_matrix为矩阵或者向量均可处理
    def gamma(self, coupon, date_index, St_range, has_knocked_in=False, delta_matrix=None):
        delta = delta_matrix if delta_matrix is not None else self.delta_matrix(coupon, date_index, St_range,
                                                                                has_knocked_in=has_knocked_in)
        gamma = np.diff(delta) / np.diff(St_range[:-1])
        return gamma

    # 绘制gamma曲线
    def gamma_curve(self, coupon, date_index, St_range, has_knocked_in=False):
        gamma = self.gamma(coupon, date_index, St_range, has_knocked_in=has_knocked_in)
        plt.figure()
        plt.plot(St_range[:-2], gamma)
        plt.xlabel('St')
        plt.ylabel('Gamma')
        plt.show()
        return gamma

    # 绘制gamma曲面
    def gamma_surface(self, coupon, date_index_range, St_range, has_knocked_in=False):
        gamma_matrix = self.gamma(coupon, date_index_range, St_range, has_knocked_in=has_knocked_in)
        x_mesh, y_mesh = np.meshgrid(St_range[:-2], date_index_range, indexing='ij')
        z_mesh = gamma_matrix.T
        fig = plt.figure()
        sub = fig.add_subplot(111, projection='3d')
        sub.plot_surface(x_mesh, y_mesh, z_mesh, cmap=cm.jet)
        sub.set_xlabel(r'$St$')
        sub.set_ylabel(r'$time_to_maturity$')
        sub.set_zlabel(r'$gamma$')
        plt.show()
        return gamma_matrix

    # 计算vega
    def vega(self, coupon, date_index_range, St_range, has_knocked_in=False, central_diff_length=0.01):
        if str(date_index_range).isdigit():
            date_index_range = np.array([date_index_range])
        sigma_range = np.array([self.sigma - central_diff_length, self.sigma + central_diff_length])
        vega_matrix = np.zeros((date_index_range.shape[0], St_range.shape[0]))
        N_path = self.base_gbm_path.shape[0]
        n_days_maturity = round(self.maturity * self.ndays_year)
        base_gbm_path_1 = self.monte_carlo_gbm_path(1, N_path, n_days_maturity, filename='QuasiRand.pickle',
                                                    MCMethod='Sobol', sigma=sigma_range[0])
        base_gbm_path_2 = self.monte_carlo_gbm_path(1, N_path, n_days_maturity, filename='QuasiRand.pickle',
                                                    MCMethod='Sobol', sigma=sigma_range[1])
        for i, date_index in enumerate(date_index_range):
            n_timestep = n_days_maturity - date_index
            for j, St in enumerate(St_range):
                pv_minus = self.monte_carlo_calculate_pv(St, coupon, N_path, n_timestep, has_knocked_in=has_knocked_in,
                                                         MC_paths=St * base_gbm_path_1[:, :(n_timestep + 1)])
                pv_plus = self.monte_carlo_calculate_pv(St, coupon, N_path, n_timestep, has_knocked_in=has_knocked_in,
                                                        MC_paths=St * base_gbm_path_2[:, :(n_timestep + 1)])
                vega_matrix[i, j] = (pv_plus - pv_minus) / np.diff(sigma_range)
        return vega_matrix

    # 绘制vega曲面
    def vega_surface(self, coupon, date_index_range, St_range, has_knocked_in=False, central_diff_length=0.01):
        vega_matrix = self.vega(coupon, date_index_range, St_range, has_knocked_in,
                                central_diff_length=central_diff_length)
        x_mesh, y_mesh = np.meshgrid(St_range, date_index_range, indexing='ij')
        z_mesh = vega_matrix.T
        fig = plt.figure()
        sub = fig.add_subplot(111, projection='3d')
        sub.plot_surface(x_mesh, y_mesh, z_mesh, cmap=cm.jet)
        sub.set_xlabel(r'$St$')
        sub.set_ylabel(r'$time_to_maturity$')
        sub.set_zlabel(r'$vega$')
        plt.show()
        return vega_matrix

    # 从t时点开始，敲出观察日序列的日期index
    def _get_available_observation_days(self, n_timestep):
        return self.observation_days[self.observation_days >= (self.observation_days[-1] - n_timestep)] - (
                    self.observation_days[-1] - n_timestep)

    # 从t时点开始，在每个敲出观察日可获得的票息
    def _get_available_coupon_vector(self, coupon, n_timestep):
        coupon_vector = np.array([(i + 1) * coupon / 12 for i, j in enumerate(self.observation_days)])
        return coupon_vector[self.observation_days >= (self.observation_days[-1] - n_timestep)]

    # 从敲出观察日贴现回t时点的贴现因子
    def _get_discount_factors(self, available_observation_days):
        return np.exp(-self.r * available_observation_days / self.ndays_year)

    # 保证金从0时点到t时点的时间价值乘数
    def _get_riskless_return_factor(self, n_timestep):
        return np.exp(self.r * (round(self.maturity * self.ndays_year) - n_timestep) / self.ndays_year)

    # 计算指定轨道的现值
    def get_paths_pv(self, S_paths, coupon, n_timestep, has_knocked_in=False, margin_pay_interest=False):
        available_observation_days = self._get_available_observation_days(n_timestep)
        available_coupon_vector = self._get_available_coupon_vector(coupon, n_timestep)
        discount_factors = self._get_discount_factors(available_observation_days)
        riskless_return_factor = self._get_riskless_return_factor(n_timestep) * np.abs(~margin_pay_interest)
        pv = np.zeros(S_paths.shape[0])
        # 触碰knock out障碍引发自动回购的路径的pv
        ko_matrix = S_paths[:, available_observation_days] >= (self.S0 * self.knock_out)
        ko_status = ko_matrix.any(axis=1)
        ko_pvs = np.eye(len(available_observation_days))[ko_matrix[ko_status].argmax(axis=1)] * (
                1 + available_coupon_vector) * discount_factors
        pv[ko_status] = ko_pvs.sum(axis=1) - 1 * riskless_return_factor
        # 没触碰knock out障碍但触碰knock in障碍的路径pv
        knock_in_status = (S_paths <= (self.S0 * self.knock_in)).any(axis=1)
        nko_ki_status = np.logical_and(~ko_status, knock_in_status)
        terminal_payoff = S_paths[nko_ki_status, -1] / self.S0
        terminal_payoff[terminal_payoff > 1] = 1
        pv[nko_ki_status] = terminal_payoff * discount_factors[-1] - 1 * riskless_return_factor
        # 计算没触碰到上下障碍的路径pv
        nko_nki_status = np.logical_and(~ko_status, ~knock_in_status)
        if not has_knocked_in:
            # 在St前的路径没有触碰过knock in barrier, 此时为投资者最理想的盈利情形（持有期权到期并收取高额年化coupon）
            pv[nko_nki_status] = np.ones(S_paths.shape[0])[nko_nki_status] * (1 + available_coupon_vector[-1]) * \
                                 discount_factors[-1] - 1 * riskless_return_factor
        else:
            # 在St前的路径触碰过knock in barrier, 往后路径的payoff就是个T时刻的看跌期权
            terminal_payoff = S_paths[nko_nki_status, -1] / self.S0
            terminal_payoff[terminal_payoff > 1] = 1
            pv[nko_nki_status] = terminal_payoff * discount_factors[-1] - 1 * riskless_return_factor
        return pv

    def monte_carlo_calculate_pv(self, St, coupon, N_path, n_timestep, has_knocked_in=False, MC_paths=None, MCMethod='',
                                 filename='', margin_pay_interest=False):
        S_paths = MC_paths if MC_paths is not None else self.monte_carlo_gbm_path(St, N_path, n_timestep,
                                                                                  MCMethod=MCMethod, filename=filename)
        pv = self.get_paths_pv(S_paths, coupon, n_timestep, has_knocked_in=has_knocked_in,
                               margin_pay_interest=margin_pay_interest)
        return self.nominal_principle * pv.mean()

    def monte_carlo_calculate_coupon(self, N_path=100000, n_timestep=-1, MCMethod='', filename='', use_base_gbm=True):
        MC_paths = self.S0 * self.base_gbm_path[:, :(n_timestep + 1)] if use_base_gbm else self.monte_carlo_gbm_path(
            self.S0, N_path, n_timestep, MCMethod=MCMethod, filename=filename)
        f = lambda c: self.monte_carlo_calculate_pv(self.S0, c, N_path, n_timestep, MC_paths=MC_paths)
        return optimize.newton(f, 0.15)

    def calculate_pnl(self, delta, S_path, pv_snowball):
        discount_factor = np.exp(-self.r * 1.0 / self.ndays_year)
        pv = delta[-2] * S_path[-1]
        for i in np.arange(S_path.shape[0] - 2, 0, -1):
            pv = pv * discount_factor + (delta[i - 1] - delta[i]) * S_path[i]
        pv = pv * discount_factor - delta[0] * S_path[0] - pv_snowball
        return pv

    def delta_hedge_return(self, coupon, q=0., MC_paths=None, delta_matrix_ki_filename=None,
                           delta_matrix_nki_filename=None):
        MC_paths = MC_paths if MC_paths is not None else self.base_gbm_path
        S_paths = copy.deepcopy(MC_paths) * self.S0
        ndays_maturity = round(self.maturity * self.ndays_year)
        # 一旦ki，后面的已ki状态都是True
        has_knocked_in = S_paths <= (self.S0 * self.knock_in)
        ki_status = has_knocked_in.any(axis=1)
        first_ki_index = has_knocked_in.argmax(axis=1)
        for i in range(has_knocked_in.shape[0]):
            if ki_status[i]:
                has_knocked_in[i, first_ki_index[i]:] = True
        # 寻找第一个ko的下标，得到各个轨道终止的日期下标
        has_knocked_out = S_paths[:, self.observation_days] >= (self.S0 * self.knock_out)
        ko_status = has_knocked_out.any(axis=1)  # 任何一个观察点敲出即算敲出
        first_ko_index = has_knocked_out[ko_status].argmax(axis=1)
        end_date_index = np.zeros(ko_status.shape[0], dtype='int')
        end_date_index[ko_status] = self.observation_days[first_ko_index]
        end_date_index[~ko_status] = ndays_maturity
        # 计算各路径在各时间节点上的delta(线性差值)
        z = np.zeros(S_paths.shape[0])
        for i in range(len(z)):
            z[i] = S_paths[i, :(end_date_index[i] + 1)].max()
        S_max = int(np.ceil(z.max()))
        for i in range(len(z)):
            z[i] = S_paths[i, :(end_date_index[i] + 1)].min()
        S_min = int(np.floor(z.min()))
        S_range = np.arange(S_min, S_max + 1)
        delta_matrix_nki = np.loadtxt(delta_matrix_nki_filename) if delta_matrix_nki_filename is not None else self.delta_matrix(coupon, np.arange(0, ndays_maturity + 1), S_range, has_knocked_in=False, parallel=True, batch=True)
        np.savetxt("delta_matrix_nki.txt", delta_matrix_nki)
        delta_matrix_ki = np.loadtxt(delta_matrix_ki_filename) if delta_matrix_ki_filename is not None else self.delta_matrix(coupon, np.arange(0, ndays_maturity + 1), S_range, has_knocked_in=True, parallel=True, batch=True)
        np.savetxt("delta_matrix_ki.txt", delta_matrix_ki)
        delta_S_paths_ki = np.zeros_like(S_paths)
        delta_S_paths_nki = np.zeros_like(S_paths)
        for j in range(S_paths.shape[1]):  # 第j天
            delta_S_paths_ki[:, j] = np.interp(S_paths[:, j], S_range[:-1], delta_matrix_ki[j, :])
            delta_S_paths_nki[:, j] = np.interp(S_paths[:, j], S_range[:-1], delta_matrix_nki[j, :])
        delta_S_paths = delta_S_paths_ki * has_knocked_in + delta_S_paths_nki * (1 - has_knocked_in)
        delta_convert_factor = np.diag(
            [np.exp(q * (ndays_maturity - i) / self.ndays_year) for i in np.arange(ndays_maturity + 1)])
        basis_convert_factor = np.diag(
            [np.exp(-q * (ndays_maturity - i) / self.ndays_year) for i in np.arange(ndays_maturity + 1)])
        delta_S_paths = np.matmul(delta_S_paths, delta_convert_factor)
        F_paths = np.matmul(S_paths, basis_convert_factor)
        # 分类汇总四种不同的轨道
        ki_before_end_date = np.zeros_like(ki_status) > 0
        for i in range(len(ki_before_end_date)):
            ki_before_end_date[i] = has_knocked_in[i, :(end_date_index[i] + 1)].any()
        nki_ko = np.logical_and(~ki_before_end_date, ko_status)
        ki_ko = np.logical_and(ki_before_end_date, ko_status)
        nki_nko = np.logical_and(~ki_before_end_date, ~ko_status)
        ki_nko = np.logical_and(ki_before_end_date, ~ko_status)
        # 计算所有轨道对冲的pnl
        pnl = np.zeros(delta_S_paths.shape[0])
        pv = self.get_paths_pv(S_paths, coupon, ndays_maturity)
        for i in range(delta_S_paths.shape[0]):
            pnl[i] = self.calculate_pnl(delta_S_paths[i, :(end_date_index[i] + 1)],
                                        F_paths[i, :(end_date_index[i] + 1)], pv[i])
        print('pnl_mean = ' + str(pnl.mean()))
        print('pnl_nki_ko_mean = ' + str(pnl[nki_ko].mean()))
        print('pnl_ki_ko_mean = ' + str(pnl[ki_ko].mean()))
        print('pnl_nki_nko_mean = ' + str(pnl[nki_nko].mean()))
        print('pnl_ki_nko_mean = ' + str(pnl[ki_nko].mean()))
        # 绘制pnl散点图
        max_amount = delta_S_paths.shape[0]  # 100000
        S_end = S_paths[:, -1]
        fig = plt.figure()
        # 绘制子图1: nki_ko情形下的pnl散点图
        sub1 = fig.add_subplot(221)
        pnl1 = pnl[nki_ko]
        index_cap = np.min([max_amount, pnl1.shape[0]])
        pnl1 = pnl1[:index_cap]
        x1_1 = S_end[nki_ko][:index_cap][pnl1 >= 0]
        y1_1 = pnl1[pnl1 >= 0]
        x2_1 = S_end[nki_ko][:index_cap][pnl1 < 0]
        y2_1 = pnl1[pnl1 < 0]
        sub1.scatter(x1_1, y1_1, color='#DC143C', marker='.', s=1)
        sub1.scatter(x2_1, y2_1, color='#008000', marker='.', s=1)
        sub1.hlines(0, S_end[nki_ko][:index_cap].min(), S_end[nki_ko][:index_cap].max(), color='black')
        sub1.set_title('nki_ko')
        sub1.set_xlabel(r'$S_T$')
        sub1.set_ylabel(r'$pnl$')
        # 绘制子图2: ki_ko情形下的pnl散点图
        sub2 = fig.add_subplot(222)
        pnl2 = pnl[ki_ko]
        index_cap = np.min([max_amount, pnl2.shape[0]])
        pnl2 = pnl2[:index_cap]
        x1_2 = S_end[ki_ko][:index_cap][pnl2 >= 0]
        y1_2 = pnl2[pnl2 >= 0]
        x2_2 = S_end[ki_ko][:index_cap][pnl2 < 0]
        y2_2 = pnl2[pnl2 < 0]
        sub2.scatter(x1_2, y1_2, color='#DC143C', marker='.', s=1)
        sub2.scatter(x2_2, y2_2, color='#008000', marker='.', s=1)
        sub2.hlines(0, S_end[ki_ko][:index_cap].min(), S_end[ki_ko][:index_cap].max(), color='black')
        sub2.set_title('ki_ko')
        sub2.set_xlabel(r'$S_T$')
        sub2.set_ylabel(r'$pnl$')
        # 绘制子图3: nki_nko情形下的pnl散点图
        sub3 = fig.add_subplot(223)
        pnl3 = pnl[nki_nko]
        index_cap = np.min([max_amount, pnl3.shape[0]])
        pnl3 = pnl3[:index_cap]
        x1_3 = S_end[nki_nko][:index_cap][pnl3 >= 0]
        y1_3 = pnl3[pnl3 >= 0]
        x2_3 = S_end[nki_nko][:index_cap][pnl3 < 0]
        y2_3 = pnl3[pnl3 < 0]
        sub3.scatter(x1_3, y1_3, color='#DC143C', marker='.', s=1)
        sub3.scatter(x2_3, y2_3, color='#008000', marker='.', s=1)
        sub3.hlines(0, S_end[nki_nko][:index_cap].min(), S_end[nki_nko][:index_cap].max(), color='black')
        sub3.set_title('nki_nko')
        sub3.set_xlabel(r'$S_T$')
        sub3.set_ylabel(r'$pnl$')
        # 绘制子图4: ki_nko情形下的pnl散点图
        sub4 = fig.add_subplot(224)
        pnl4 = pnl[ki_nko]
        index_cap = np.min([max_amount, pnl4.shape[0]])
        pnl4 = pnl4[:index_cap]
        x1_4 = S_end[ki_nko][:index_cap][pnl4 >= 0]
        y1_4 = pnl4[pnl4 >= 0]
        x2_4 = S_end[ki_nko][:index_cap][pnl4 < 0]
        y2_4 = pnl4[pnl4 < 0]
        sub4.scatter(x1_4, y1_4, color='#DC143C', marker='.', s=1)
        sub4.scatter(x2_4, y2_4, color='#008000', marker='.', s=1)
        sub4.hlines(0, S_end[ki_nko][:index_cap].min(), S_end[ki_nko][:index_cap].max(), color='black')
        sub4.set_title('ki_nko')
        sub4.set_xlabel(r'$S_T$')
        sub4.set_ylabel(r'$pnl$')
        plt.subplots_adjust(wspace=0.5, hspace=0.5)
        plt.show()


if __name__ == '__main__':
    obs_days = np.linspace(21, 504, 24).astype(int)  # 以0为起始index
    # obs_days = np.linspace(21, 126, 6).astype(int)
    knock_out = 1
    knock_in = 0.75
    maturity = 2
    # maturity = 0.5
    ndays1year = 252
    nominal_principle = 1
    r = 0.036
    q = 0.072
    sigma = 0.15
    # sigma = 0.30
    S0 = 100
    N_path = 100000
    n_timestep = round(maturity * ndays1year)

    # 用Quasi Monte Carlo生成雪球的几何布朗运动轨道
    import time
    # t1 = time.time()
    snowball_option = Snowball(knock_out, knock_in, obs_days, maturity, ndays1year, nominal_principle, r, q, sigma, S0)
    # snowball_option.gen_base_gbm_path(N_path, filename='QuasiRand.pickle', MCMethod='Sobol')
    snowball_option.gen_base_gbm_path(N_path, seed=1)
    print(snowball_option.monte_carlo_calculate_pv(S0, 0.23421582193334362, N_path, n_timestep, has_knocked_in=False,
                                                   MC_paths=snowball_option.base_gbm_path * S0))
    # print(snowball_option.monte_carlo_calculate_pv(50, 0.2342, N_path, 125, has_knocked_in=True,
    #                                               MC_paths=snowball_option.base_gbm_path[:,:-1] * 50))
    # print(snowball_option.monte_carlo_calculate_coupon(N_path, n_timestep))
    # a = snowball_option.delta_matrix(0.2342, 21, np.arange(98,102), has_knocked_in=False)
    # b = snowball_option.delta_matrix(0.2342, 0, np.arange(50,120), has_knocked_in=True)
    # 并行测试
    # t1 = time.time()
    # a = snowball_option.delta_matrix(0.2342, np.arange(0,127), np.arange(50,120), has_knocked_in=False, parallel=True, batch=False)
    # t2 = time.time()
    # print(t2-t1)
    # t1 = time.time()
    # a = snowball_option.delta_matrix(0.2342, np.arange(0,505), np.arange(50,120), has_knocked_in=False, parallel=True, batch=True)
    # t2 = time.time()
    # print(t2-t1)
    # t3 = time.time()
    # b = snowball_option.delta_matrix(0.2342, np.arange(0,127), np.arange(50,120), has_knocked_in=False, parallel=False)
    # t4 = time.time()
    # print(t4-t3)
    # print(a==b)
    # 生成delta曲线
    # snowball_option.delta_curve(0.1779, 0, np.arange(50, 120, 1), has_knocked_in=False)
    # 生成delta曲面（未敲入）
    # snowball_option.delta_surface(0.2342, np.arange(0,127), np.arange(50, 120, 1), has_knocked_in=False)
    # 生成delta曲面（已敲入）
    # snowball_option.delta_surface(0.2342, np.arange(0,127), np.arange(50, 120, 1), has_knocked_in=True)
    # 生成gamma曲面（未敲入）
    # snowball_option.gamma_surface(0.2342, np.arange(0,127), np.arange(50, 120, 1), False)
    # 生成vega曲面（未敲入）
    # snowball_option.vega_surface(0.2342, np.arange(0,127), np.arange(50, 120, 1), False, central_diff_length=0.01)
    # 绘制pnl散点图
    MC_paths = snowball_option.monte_carlo_gbm_path(1, N_path, n_timestep, q=0, seed=2)
    t1 = time.time()
    #snowball_option.delta_hedge_return(0.1779, q=0.072, MC_paths=MC_paths)
    snowball_option.delta_hedge_return(0.29527, q=0.072, MC_paths=MC_paths)
    t2 = time.time()
    print(t2 - t1)
    # snowball_option.delta_hedge_return(0.29527, MC_paths=MC_paths, delta_matrix_nki_filename="delta_matrix_nki.txt",
    #                                   delta_matrix_ki_filename="delta_matrix_ki.txt")

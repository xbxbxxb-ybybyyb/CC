# -*- coding: utf-8 -*-
# @Time    : 2023/3/8 14:44
# @Author  : qinyuhao

from minepy import MINE
import os
import pandas as pd
import numpy as np
import pickle
import datetime as dt
import sys
import warnings

warnings.filterwarnings('ignore')
import matplotlib

# plt.show()不会显示作图结果
matplotlib.use('Agg')
import IO as IO


# 因子测试类
class pj2FactorTest:
    # 隐藏生成函数具体内容
    def __init__(self, start_date, end_date, segment_number=20, style_list=['free_turn', 'tradingday'], cal_mi=True,
                 time_interval=[93000000, 145000000], last_is_zt=None, test_sample='bt',
                 first_over_threshold=False, break_is_zt=False,
                 first_is_zt=False, open_is_zt=False,
                 split_scene=None,  # 分场景测试['EFS_pct5_T1_high','EFS_pct5_T1_low','T_o2pre_high','T_o2pre_low'
                 # 'label_14','label_23','ret2o_high','ret2o_low','cl0','cl1','cl2']
                 # 931代表9点31买；v2o10d1：v代表均价卖，o代表开盘，10代表10分钟，d1代表931（d10代表940），ul代表涨停价
                 buy_type='0931', sell_type='v',
                 # buy_type = ['0930','0931','0941','o','od1'], sell_type = ['v','o','t','td1','od60']
                 # lzt_pattern = [3,4],1：一字板，2：T字板，3:破板回封，4：一直封
                 lzt_pattern=[3, 4], high_open=None  # lzt_pattern = [1,2,3,4], high_open = 0.8
                 ):

    def load_data(self):
        # 修改这里的路径
        buy_type = self.buy_type
        ret_type = self.return_type
        split_scene = self.split_scene
        lzt_pattern = self.lzt_pattern
        high_open = self.high_open
        sft_basic_path = #此处为saturn样本路径

        df = IO.read_data([self.start_date, self.end_date], alt=sft_basic_path)
        # ？非st股
        if 'st_indicator' in df.columns:
            st_filter = df['st_indicator'] != 1
        # ？开盘非涨跌停
        open_filter = (df['T_open_is_zt'] == False) & (df['T_open_is_dt'] == False)

        return_normal_filter = df[ret_type] != -3
        available_for_reaction_filter = df[ret_type] != -1
        after_not_ul_len_filter = df['after_not_ul_len'] > 10
        can_buy_filter = df['T_first_trans_ZT'] != 1
        all_filter = st_filter & open_filter & return_normal_filter & after_not_ul_len_filter & can_buy_filter
        if buy_type == '0930':
            all_filter = all_filter & available_for_reaction_filter
        if buy_type == '0931':
            all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 93100000) == False) & available_for_reaction_filter
        if buy_type == '0940':
            all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 94000000) == False) & available_for_reaction_filter
        if buy_type == 'o':
            if ret_type == 'label_od102o':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 93000000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
            # all_filter = all_filter & (df['t2o'].notnull())
        if buy_type == 'od1':
            if ret_type == 'label_td12od1':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 93100000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
            elif ret_type == 'label_od602od1':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 93100000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
            elif ret_type == 'label_od302od1':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 93100000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
        if buy_type == 'od30':
            if ret_type == 'label_od602od30':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 100000000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
        if buy_type == 'od10':
            if ret_type == 'label_od302od10':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 94000000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
        if buy_type == 'od180':
            if ret_type == 'label_od2402od180':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 140000000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
        if buy_type == 'to':
            if ret_type == 'label_tv2to':
                all_filter = all_filter & ((df['T_day_first_ZT_Time'] <= 93000000) == False) & (
                    df[ret_type].notnull()) & available_for_reaction_filter
        # 新增前日形态的filter
        pattern_filter = df['lzt_label_pattern'].apply(lambda x: x in lzt_pattern).values
        all_filter = all_filter & pattern_filter
        # 新增高开filter
        if high_open is not None:
            high_open_filter = df['T_o2pre'] <= 0.08
            all_filter = all_filter & high_open_filter

        # 样本筛选
        df = df[all_filter]
        df = df.rename(columns={ret_type: 'value'})
        df['value'] = df['value'] * 100
        if (ret_type == 'label_td12od1') | (ret_type == 'label_t2o'):
            df['value'] = df['value'] * -1
        # 从df.index中提取年月、年、分组（value是否大于0）、交易日信息
        df['month'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y-%m')[2:]))
        df['year'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y')))
        df['class'] = df['value'] > 0
        df['tradingday'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: int(x.strftime('%Y%m%d'))))

        self.basic_df = df[['value', 'class', 'month', 'year'] + self.style_list]

        all_factors_available = ['label_v2o10', 'label_v2o10d1', 'label_v2o10d10',
                                 'label_o2o10', 'label_o2o10d1', 'label_o2o10d10',
                                 'label_od602od1', 'label_t2o10',
                                 'label_od102o', 'label_od302od1', 'label_od602od30', 'label_od2402od180',
                                 'label_od302od10',
                                 'T_day_first_ZT_Time', 'T_first_trans_ZT', 'T_open_is_zt', 'T_open_is_dt',
                                 'st_indicator']
        if ret_type in all_factors_available:
            all_factors_available.remove(ret_type)
        # all_factor用于待测因子和已有因子的相关性计算时用
        self.all_factor = df.drop(
            ['value', 'class', 'month', 'year'] + list(set(df.columns) & set(all_factors_available)), axis=1)

    # 生成一个字典，key为形如‘202101~202105’，value为corr_month在该区间的切片
    def split(self, corr_month, split_month=6):
        dic = {}
        split_num = len(corr_month) // split_month
        for i in range(split_num):
            corr_ = corr_month.iloc[i * split_month:(i + 1) * split_month] if (
                        i != (split_num - 1)) else corr_month.iloc[i * split_month:]
            key = '%s~%s' % (min(corr_.index), max(corr_.index))
            dic[key] = corr_
        return dic

    # keys形如['202101~202105','202106~202109'],将basic_df生成字典，字典key为'202101~202105',value为basic_df在该区间的切片
    # 和上述函数区别是，split需要选择切割的大小，split_data是按传入的keys去切割
    def split_data(self, basic_df, keys):
        dic = {}
        for key in keys:
            start_month, end_month = key.split('~')[0], key.split('~')[1]  # 这个split不是上面定义的split
            df = basic_df[(basic_df['month'] >= start_month) & (basic_df['month'] <= end_month)]
            dic[key] = df
        return dic

    # 对self.basic_df计算大于/小于离群界限的比率
    def extreme_value_sta(self):
        med = self.basic_df['factor'].median()
        mad = (self.basic_df['factor'] - med).abs().median()
        sta = pd.Series()
        sta['up_3MAD_rate'] = (self.basic_df['factor'] > (med + 3 * mad)).mean()
        sta['down_3MAD_rate'] = (self.basic_df['factor'] < (med - 3 * mad)).mean()
        return sta

    def factor_test(self, factor_df, result_path, factor_corr_test=False, generate_pdf=True):
        # 待测因子的df只能1列（实际使用可以for col in df.columns）
        if len(factor_df.columns) > 1:
            print('factor_df must be only one column')
            raise Exception
        # 因子df要求列名为因子名
        self.factor_name = factor_df.columns[0]
        # basic_df过滤样本，把入参的factor_df过滤后形成self.factor_df，列名统一为'factor'
        self.factor_df = pd.DataFrame(index=self.basic_df.index)
        self.factor_df['factor'] = factor_df[self.factor_name]
        # 待测因子也加入basic_df中
        self.basic_df['factor'] = self.factor_df['factor']
        # 获取待测因子基本信息
        self.result_dic['factor_information'] = self.get_factor_information()
        # 获取月度口径下，因子与label_list元素的相关性
        self.result_dic['corr_month'] = self.get_corr_month()
        # 得到因子与label_list元素的MIC、总体相关系数、月度相关系数的均值、标准差、均值/标准差
        self.result_dic['corr_sta'] = self.get_corr_sta(self.result_dic['corr_month'])
        # 按因子值排序作为总体分布
        self.result_dic['distribution_tot'] = self.factor_df.sort_values(by='factor')
        # 每个月factor用空值补足到最大长度,返回df：columns = month
        self.result_dic['distribution_month'] = self.get_distribution_month()
        # 整个时间段的basic_df，按因子大小分层，得到每一层的style_list中元素的均值，形成返回的df
        self.result_dic['distribution_style'] = self.get_distribution_style()
        # 因子和style_list中元素的spearman相关系数，Series形式,索引为style_list
        self.result_dic['corr_style'] = self.get_corr_style()
        # 整个时间段的basic_df，按因子大小分层，得到每一层的label_list中元素的均值，形成返回的df
        self.result_dic['group_tot'] = self.get_group_test_result()
        # 对style_list中元素分层，再按待测因子聚合后，label的均值
        self.result_dic['group_tot_time_sort'] = self.get_double_group_test_result(self.style_list)
        # 整个时间段的basic_df，先按年分组，而后得到字典类型返回值，value是该年的因子分层后每一层的label_list元素值
        self.result_dic['group_by_year'] = self.get_group_test_result_by_year()
        # 对style_list中元素和待测因子双分组后的df，注意默认不return_data，和get_double_group_test_result不一样
        # 返回的是dic，key是sort_factor_list中元素，value是双分组后的df
        self.result_dic['double_group_sort'] = self.get_double_sort(sort_factor_list=self.style_list)

        # 把corr_month按半年切分，生成一个字典（key形如'16-01~16-06'，返回该字典
        # self.result_dic['corr_month'][keys]指因子与label_list元素的相关性，index是月份
        self.result_dic['corr_month_dic'] = self.split(self.result_dic['corr_month'])

        # 把basic_df切片成半年的，变成字典返回
        data_dic = self.split_data(self.basic_df.copy(), list(self.result_dic['corr_month_dic'].keys()))

        # 返回字典，key是月份，value是补充双分组后的basic_df
        self.result_dic['double_group_sort_dic'] = self.get_double_sort_dic(sort_factor_list=self.style_list,
                                                                            data_dic=data_dic)
        # value是Series，离界数据的比率
        self.result_dic['extreme_value_sta'] = self.extreme_value_sta()

        # 如果T_o2pre因子在sort_factor_list中，用T_o2pre作为入参，考察高开对因子的影响
        if ('T_o2pre' in self.result_dic['double_group_sort']):
            self.result_dic['check_diff_res'], \
            self.result_dic['check_score_res'] = self.check_score(
                self.result_dic['double_group_sort']['T_o2pre'].copy(), \
                self.result_dic['corr_month'].copy(), \
                np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
            self.result_dic['check_score_list'] = self.check_score_list(self.result_dic['double_group_sort_dic'].copy(), \
                                                                        self.result_dic['corr_month_dic'].copy(), \
                                                                        np.sign(self.result_dic['corr_sta'].loc[
                                                                                    'corr_tot']))
        # 否则根据时间入参计算分数
        elif ('tradingday' in self.result_dic['double_group_sort']):
            # 总体结果
            self.result_dic['check_diff_res'], \
            self.result_dic['check_score_res'] = self.check_score(
                self.result_dic['double_group_sort']['tradingday'].copy(), \
                self.result_dic['corr_month'].copy(), \
                np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
            # 每个半年分数构成的df
            self.result_dic['check_score_list'] = self.check_score_list(self.result_dic['double_group_sort_dic'].copy(), \
                                                                        self.result_dic['corr_month_dic'].copy(), \
                                                                        np.sign(self.result_dic['corr_sta'].loc[
                                                                                    'corr_tot']))
        # 离群值比率
        other_sta = {'up_3MAD_rate': [self.result_dic['extreme_value_sta']['up_3MAD_rate']], \
                     'down_3MAD_rate': [self.result_dic['extreme_value_sta']['down_3MAD_rate']]}
        self.result_dic['other_sta'] = pd.DataFrame(other_sta, index=[''])

        # 20210324添加同一个值的阈值
        self.result_dic['max_same_ratio'] = self.get_max_one_ratio()
        # 20210428添加同时考虑样本内外的因子分布评价，只有在20160101到20190930才运行
        if (int(self.start_date) == 20160101) & (int(self.end_date) == 20190930):
            # df:离群值比率等
            self.result_dic['distribution_stats'] = self.get_in_out_distribution_score()
            # tuple:不同切分方式下离群值的情况
            self.result_dic['in_out_LS_performance_stats'] = self.get_in_out_LS_performance()

        # 待测因子与已有因子相关性测试
        self.factor_corr_test = factor_corr_test
        if self.factor_corr_test:
            self.result_dic['factor_corr'] = self.get_corr_with_all_factor()
            self.result_dic['factor_corr_summary'] = self.result_dic['factor_corr']
            self.result_dic['factor_corr_summary'] = self.result_dic['factor_corr_summary'][
                (self.result_dic['factor_corr_summary']['factor_corr'] > 0.7)]
        now_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        # pickle用因子名命名
        self.save_pickle(self.result_dic, save_path='%s%s.pkl' % (result_path, self.factor_name))
        # 回测文件带上时间命名
        if generate_pdf:
            self.generate_pdf(self.result_dic, save_path='%s%s_%s.pdf' % (result_path, self.factor_name, now_time))

    # 生成PDF
    def generate_pdf(self, result_dic, save_path):
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import PageBreak
        from reportlab.rl_config import defaultPageSize
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        import matplotlib.pyplot as plt
        from io import BytesIO
        from reportlab.platypus import Image
        elements = []
        styles = getSampleStyleSheet()
        # 选图片式样，参考plt.style.available
        plt.style.use('ggplot')
        # 注册字体文件
        # 查看已注册字体：pdfmetrics.getRegisteredFontNames()
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        PAGE_HEIGHT = defaultPageSize[1];  # 默认页面大小的高度
        PAGE_WIDTH = defaultPageSize[0]  # 宽度
        fig_width = 7.5
        fig_height = 2

        def generate_first_page(canvas, doc):
            Title = 'Factor Test Report'
            # 保存属性设置
            # 属性设置如果没有save，在showpage以后会被恢复
            # 样例：设置1，设置2，save，那么设置12会被保留，此时设置3，showpage，会按设置123生成，但结束后设置3不会被保留
            canvas.saveState()
            canvas.setTitle(title='Factor Test Report')  # ?这一步用处不大，但正规
            PAGE_HEIGHT = defaultPageSize[1];  # 默认页面高度与宽度
            PAGE_WIDTH = defaultPageSize[0]
            canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, Title)  # 写TITLE
            canvas.setFont(psfontname='STSong-Light', size=6)  # 字体，宋体，？这一步有些问题，应该放在drawCenteredString之前才有效
            canvas.restoreState()  # 恢复设置

        def generate_later_pages(canvas, doc):
            canvas.saveState()
            canvas.setFont(psfontname='STSong-Light', size=6)
            canvas.restoreState()

        # 把df变成list形式，元素以string形式存储原先的行列与数值
        def dataframe2str(df, col_type, axis, reformat_type):
            """get dataframe column, return string with format"""
            # axis控制是否要转置
            df = df if axis == 1 else df.T
            #
            df_col = df.columns.tolist()
            df_row = df.index.tolist()
            df_str = [''] + df_row
            for col, ct in zip(df_col, col_type):
                # 如果reformat_type = True,对每一列，根据col_type调用num2str生成一个列表：[列名，str数值1，str数值2，...]
                # 否则[列名，原始数值1，原始数值2,...]
                data = [col] + num2str(df[col].values.tolist(), ct) if reformat_type == True else [col] + df[
                    col].values.tolist()
                # 按垂直方向堆叠
                df_str = np.vstack([df_str, data])
            df_str = df_str.T.tolist() if axis == 1 else df_str.tolist()
            return df_str

        # 根据data_type，对data统一：统一后为数字 or 百分比（譬如50%）的str形式
        def num2str(data, data_type):
            """take number and change format, return list of string"""
            round_num = int(data_type[-1])  # 决定截取几位小数
            number_type = data_type[:-1]  # 去掉最后一位
            if number_type == 'pct':
                data = [str(round(i * 100, round_num)) + '%' for i in data]
            elif number_type == 'dcm':
                data = [str(round(i, round_num)) for i in data]
            return data

        # 生成表格
        def generate_table(df, col_type, axis, reformat_type):
            # 输入列类型，变成list形式，data统一为Str形式
            df_str = dataframe2str(df, col_type, axis, reformat_type)
            df_str[0] = [i.encode('utf-8') for i in df_str[0]]  # 原先的columns
            t = Table(df_str)  # Table要求必须为str类型才能生成表格
            # （-1，0）代表最后一列，第0行
            # 设置了背景色，字颜色，字体；还可以有BOX：外框线，INNERGRID：内框线
            mytable = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                  ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                  ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light')])
            t.setStyle(mytable)
            return t

        # 画图
        # 通用的画图函数，把参数（颜色、大小等）统一
        def generate_plot(df, plot_name, x_label, y_label, plot_type='line', color='#e23e57', rot=0, plot_y0=False, \
                          use_index=True, secondary_y=False, stacked=False, fig_width=7.5, fig_height=2):
            plt.close()  # 关闭窗口，释放内存
            legend_on = True if min(df.shape) > 1 else False  # 是否显示图例

            # bins:纵坐标刻度，fontsize:刻度字体大小，rot:时间刻度标签显示的角度,secondary_y:把部分列以右y轴为基准画，stacked：是否堆叠，不同kind联立下有区别
            if plot_type == 'hist':  # 直方图
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on,
                                  fontsize=20,
                                  color=color, rot=rot, use_index=use_index, secondary_y=secondary_y, bins=100)
            else:
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on,
                                  fontsize=20,
                                  color=color, rot=rot, use_index=use_index, secondary_y=secondary_y, stacked=stacked)
            df_plot.set_title(plot_name, fontsize=20)
            df_plot.set_xlabel(x_label, fontsize=16)
            df_plot.set_ylabel(y_label, fontsize=16)
            # 如果plot_y0，绘制平行于x轴的水平线，alpha：透明度
            if plot_y0: plt.axhline(y=0, alpha=2, color='#414141')
            # 用二进制文件临时保存图片，再用Image函数给定在pdf中的大小
            imgdata = BytesIO()  # 二进制文件，临时保存图片
            df_plot.figure.savefig(imgdata, format='jpg', dpi=50)  # dpi：分辨率，？越小越清晰
            imgdata.seek(0)  # 用IMAGE之前先seek(0)，让指针回到起点
            plt.close()  # 关闭窗口，释放内存
            return Image(imgdata, width=fig_width * inch, height=fig_height * inch + 10)

        #
        def generate_double_sort(df):
            plt_rows = len(self.label_list)  # label的数目
            plt_cols = len(self.style_list)  # style的数目
            height_each_row = 1.7  # 5，每个label的高度
            height_calc = plt_rows * height_each_row  # label总高度
            fig_height = 20 / (7 / height_calc)
            fig = plt.figure(figsize=(10 * len(self.style_list), fig_height))  # 画布
            # ax = fig.add_subplot(plt_rows, )
            for (style, i) in zip(self.style_list, range(plt_cols)):  # 第i个style，第j个label
                for (label, j) in zip(self.label_list, range(plt_rows)):
                    # 画布被分为plt_rows * plt_cols个部分，子图在plt_cols*j+i+1的位置
                    ax = fig.add_subplot(plt_rows, plt_cols, plt_cols * j + i + 1)
                    # df[style][label]一般是双分组排序的df，具有双索引，展开
                    d = df[style][label].unstack()
                    # 画图所在位置和类型
                    d.plot(ax=ax, kind='bar')
                    ax.set_title('%s-%s' % (style, label))
                    # 标签大小
                    plt.tick_params(labelsize=16)
            # 自动调整参数，使得图片不重叠，不空缺
            plt.tight_layout()
            # 图例
            plt.legend(loc='best')
            # 用二进制文件保存图片。再用IMAGE函数调用该文件，输出固定大小的图片
            imgdata = BytesIO()
            plt.savefig(imgdata, format='jpg', dpi=100)
            imgdata.seek(0)
            plt.close()
            return Image(imgdata, width=fig_width * inch, height=height_calc * inch)

        # 对每年的双分组测试结果绘图
        def generate_group_test_year(df, cols_list):
            year_list = list(df.keys())  # list(set(df.index.get_level_values(0)))
            year_num = len(year_list)
            plt_rows = int(np.ceil(year_num / 2))
            height_each_row = 1.7  # 5
            height_calc = plt_rows * height_each_row
            fig_height = 20 / (7 / height_calc)
            plt.figure(figsize=(20, fig_height))
            for i in range(year_num):
                plt.subplot(plt_rows, 2, i + 1)
                width = 0.3
                if cols_list == ['class']:
                    x = np.arange(len(df[year_list[i]]))
                    plt.bar(x - width / 2, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0],
                            color='#1b7fbd')
                    # plt.bar(x+width/2, list(df[year_list[i]][cols_list[1]]), width=width, label =cols_list[1], color='#525252')
                    if self.test_sample == 'bt':
                        plt.ylim(0, 0.6)  # y轴显示范围
                    elif self.test_sample == 'zt':
                        plt.ylim(0, 0.8)
                else:
                    x = np.arange(len(df[year_list[i]]))
                    plt.bar(x, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0], color='#e23e57')
                    if self.test_sample == 'bt':
                        plt.ylim(-3, 2)
                    elif self.test_sample == 'zt':
                        plt.ylim(-2, 2)
                plt.tick_params(labelsize=16)
                plt.title(year_list[i], fontsize=20, fontweight='bold')
            plt.tight_layout()
            imgdata = BytesIO()
            plt.savefig(imgdata, format='jpg', dpi=50)
            imgdata.seek(0)
            plt.close()
            return Image(imgdata, width=fig_width * inch, height=height_calc * inch)

        pdf_styles = getSampleStyleSheet()  # 模板
        # 基本信息的表格
        h_factor_information = Paragraph('Factor Information', pdf_styles['Heading4'])  # 段落名称和模板
        col_type = ['str1'] * len(result_dic['factor_information'])  # 基本信息的元素个数，初始化
        t_factor_information = generate_table(result_dic['factor_information'], col_type, axis=0, reformat_type=False)
        # 打分表格：score、重复值、其他
        h_score_sta = Paragraph('Score Statistic', pdf_styles['Heading4'])
        t_score_sta = generate_table(result_dic['check_score_res'],
                                     col_type=['dcm0', 'dcm0', 'dcm0', 'dcm0', 'dcm0', 'dcm2'], axis=0,
                                     reformat_type=True)
        h_repeat_sta = Paragraph('Repeat Statistic', pdf_styles['Heading4'])
        t_repeat_sta = generate_table(result_dic['max_same_ratio'], col_type=['dcm2', 'dcm2'], axis=0,
                                      reformat_type=True)
        h_other_sta = Paragraph('Other Statistic', pdf_styles['Heading4'])
        t_other_sta = generate_table(result_dic['other_sta'],
                                     col_type=['pct2'], axis=0,
                                     reformat_type=True)
        # 基本信息和打分的内容放在一个列表里
        elements = [h_factor_information, t_factor_information, h_other_sta, t_other_sta, h_score_sta, t_score_sta,
                    h_repeat_sta, t_repeat_sta]
        # 打分的具体明细表格，也加入列表里
        h_score_list_sta = Paragraph('Interval Score', pdf_styles['Heading4'])
        t_score_list_sta = generate_table(result_dic['check_score_list'],
                                          col_type=['dcm2'] * len(result_dic['check_score_list']), axis=0,
                                          reformat_type=True)
        elements += [h_score_list_sta, t_score_list_sta]
        # 与其他因子的相关性表格
        if self.factor_corr_test:
            h_corr_with_other = Paragraph(
                'Bank Corr Statistic - %d high corr factor' % (len(result_dic['factor_corr_summary'])), \
                pdf_styles['Heading4'])
            elements.append(h_corr_with_other)
            if len(result_dic['factor_corr_summary']) > 0:
                t_corr_with_other = generate_table(result_dic['factor_corr_summary'],
                                                   col_type=['dcm4'] * len(result_dic['factor_corr_summary']), axis=0,
                                                   reformat_type=True)
                elements.append(t_corr_with_other)
        # 因子与label_list元素的MIC、总体相关系数、月度相关系数的均值、标准差、均值/标准差统计表格
        h_corr_sta = Paragraph('Correlation Statistic', pdf_styles['Heading4'])
        if len(result_dic['corr_sta']) == 5:
            col_type = ['pct2', 'pct2', 'pct2', 'pct2', 'dcm1']
        elif len(result_dic['corr_sta']) == 4:
            col_type = ['pct2', 'pct2', 'pct2', 'dcm1']
        t_corr_sta = generate_table(result_dic['corr_sta'], col_type, axis=0, reformat_type=True)
        elements += [h_corr_sta, t_corr_sta]
        # 每月分数构成的df画直方图
        p_score_list_sta = generate_plot(result_dic['check_score_list'][
                                             ['class_diff_score', 'class_stability_score', 'value_diff_score',
                                              'value_stability_score']] \
                                         , plot_name='Interval Score'
                                         , x_label='interval'
                                         , y_label='score'
                                         , color=['#525252', '#1f4068', '#900d0d', '#e23e57']
                                         , plot_type='bar', stacked=True)
        elements += [h_score_list_sta, p_score_list_sta]
        # 月度相关性直方图
        h_monthly_corr = Paragraph('Monthly Corr', pdf_styles['Heading4'])
        p_monthly_corr = generate_plot(result_dic['corr_month'][['value', 'class']], \
                                       plot_name='Monthly Corr - Value&Class', \
                                       x_label='month', y_label='corr of value&class', \
                                       plot_type='bar', color=['#e23e57', '#1b7fbd'], rot=25)
        elements += [h_monthly_corr, p_monthly_corr]
        # 直方图：整个时间段的basic_df，按因子大小分层，得到每一层的label_list中元素的均值，形成返回的df
        h_group_test = Paragraph('Group Test', pdf_styles['Heading4'])
        p_group_test_value = generate_plot(result_dic['group_tot'][['value']], plot_name='Group Test - Value',
                                           x_label='Group',
                                           y_label='value', plot_type='bar')
        p_group_test_cm = generate_plot(result_dic['group_tot'][['class']], plot_name='Group Test - Class',
                                        x_label='Group', y_label='class', plot_type='bar', color=['#1b7fbd'])
        # 直方图：按style_list分层再分组后，label_list元素均值
        p_group_test_cm_with_style0 = generate_plot(
            self.result_dic['group_tot_time_sort'][self.style_list[0]][['class']],
            plot_name='Group Test - Class - %s Neutralization' % (self.style_list[0]),
            x_label='Group', y_label='class', plot_type='bar', color=['#1b7fbd'])
        p_group_test_cm_with_style1 = generate_plot(
            self.result_dic['group_tot_time_sort'][self.style_list[1]][['class']],
            plot_name='Group Test - Class - %s Neutralization' % (self.style_list[1]),
            x_label='Group', y_label='class', plot_type='bar', color=['#1b7fbd'])
        # 绘图：按年分组，该年的因子分层后每一层的label_list元素值
        p_group_test_value_year = generate_group_test_year(result_dic['group_by_year'], cols_list=['value'])
        p_group_test_value_cm = generate_group_test_year(result_dic['group_by_year'], cols_list=['class'])
        elements += [h_group_test, p_group_test_value, p_group_test_cm, p_group_test_cm_with_style0,
                     p_group_test_cm_with_style1, p_group_test_value_year, p_group_test_value_cm]
        # 折线图：按因子值排序的basic_df
        h_ds = Paragraph('Distribution & Style', pdf_styles['Heading4'])
        p_dis = generate_plot(result_dic['distribution_tot'], plot_name='Distribution', x_label='factor',
                              y_label='value', plot_type='line', color=['#211717'], use_index=False)
        # 折线图：按因子大小分层，得到每一层的style_list中元素的均值，形成返回的df
        p_styles0 = generate_plot(result_dic['distribution_style'][self.style_list[0]],
                                  plot_name='Style - %s' % (self.style_list[0]),
                                  x_label='sorted by factor', y_label='style', plot_type='line',
                                  color=['#211717'], use_index=False)
        p_styles1 = generate_plot(result_dic['distribution_style'][self.style_list[1]],
                                  plot_name='Style - %s' % (self.style_list[1]),
                                  x_label='sorted by factor', y_label='style', plot_type='line',
                                  color=['#211717'], use_index=False)
        # 表格：因子和style_list中元素的spearman相关系数，Series形式,索引为style_list
        t_styles = generate_table(result_dic['corr_style'], col_type=['pct2', 'pct2'], axis=0, reformat_type=True)
        # 直方图：style_list中的元素，双分组后的df
        p_double_sort = generate_double_sort(result_dic['double_group_sort'])
        elements += [h_ds, p_dis, p_styles0, p_styles1, t_styles, p_double_sort]
        # score表格
        if 'check_diff_res' in self.result_dic:
            h_check_res = Paragraph('Standard Check', pdf_styles['Heading4'])
            t_check_res = generate_table(result_dic['check_diff_res'].T, ['pct2', 'pct2', 'pct2', 'pct2', 'str1'] * 2,
                                         axis=0,
                                         reformat_type=True)
            elements += [h_check_res, t_check_res]
        # 箱型图：每个月的分布
        h_dis_month = Paragraph('Distribution Each Month', pdf_styles['Heading4'])
        p_dis_month = generate_plot(result_dic['distribution_month'], plot_name='Month Distribution', x_label='factor',
                                    y_label='value', plot_type='box', rot=25, color='#414141')
        elements += [h_dis_month, p_dis_month]
        # 表格：与其他因子的相关性
        if self.factor_corr_test:
            h_corr_all = Paragraph('Correlation with Other Factors', pdf_styles['Heading4'])
            t_corr_all = generate_table(result_dic['factor_corr'].iloc[:20], col_type=['dcm4'] * 20, axis=0,
                                        reformat_type=True)
            elements += [h_corr_all, t_corr_all]
        # 画PDF
        # topmargin:顶边距
        doc = SimpleDocTemplate(save_path, pagesize=letter, topMargin=80, bottomMargin=3)
        doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)

    # result_dic存储为pickle文件
    def save_pickle(self, result_dic, save_path):
        with open(save_path, 'wb') as input:  # 'wb'：以二进制形式打开一个文件用于写入，若无此文件则创造
            pickle.dump(result_dic, input,
                        protocol=pickle.HIGHEST_PROTOCOL)  # dump:将obj对象序列化存入已经打开的file中；protocol含义：序列化协议用最高版本

    def check_standard(self, double_group_df):
        def cal_reverse_sum(rate_arr):
            index1 = np.argmax(rate_arr)
            index2 = np.argmin(rate_arr)
            if index1 < index2:  # 反向转换为从小到大排序
                rate_arr = np.flipud(rate_arr)
            rate_arr_diff = np.diff(rate_arr)
            return np.abs(np.sum(rate_arr_diff[rate_arr_diff < 0]))

        res_df = pd.DataFrame()
        diff, reverse = [], []
        for i in range(5):
            rate_arr = double_group_df['class'].unstack().iloc[i].values
            diff.append(max(rate_arr) - min(rate_arr))
            reverse.append(cal_reverse_sum(rate_arr))
        res_df['diff'], res_df['reverse'] = diff, reverse
        res_df['0.5*diff'], res_df['0.6*diff'] = res_df['diff'] * 0.5, res_df['diff'] * 0.6
        res_df['standard'] = 1
        res_df.loc[((res_df['diff'] > 0.13) & (res_df['reverse'] < res_df['0.6*diff'])), 'standard'] = 2
        res_df.loc[((res_df['diff'] > 0.18) & (res_df['reverse'] < res_df['0.5*diff'])), 'standard'] = 3
        res_df['standard'] = res_df['standard'].replace({1: 'low', 2: 'mid', 3: 'high'})
        return res_df.T

    # 返回每月的分数构成的df
    # double_group_df_dic = self.result_dic['double_group_sort_dic'].copy():字典：key是半年，value是补充双分组后的basic_df
    # month_df_dic = self.result_dic['corr_month_dic'].copy()：字典：key是半年，value是这半年里每个月因子与label_list元素的相关性
    # dir = np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
    def check_score_list(self, double_group_df_dic, month_df_dic, dir, label_test=['value']):
        keys = list(double_group_df_dic.keys())
        res_df = pd.DataFrame()
        # 每半年的分数
        for key in keys:
            double_group_df, month_df = double_group_df_dic[key], month_df_dic[key]
            x, score_df = self.check_score(double_group_df[self.style_list[1]], month_df, dir)  # 只取tradingday
            res_df[key] = score_df.loc['score']
        # 月份作为index排序
        return res_df.T.sort_index()

    #
    def check_score(self, double_group_df, month_df, dir, label_test=['value', 'class']):
        # double_group_df = self.result_dic['double_group_sort']['tradingday'].copy();即日期作为因子1，双分组后的df
        # month_df = self.result_dic['corr_month'].copy()；待测因子groupby month后与label_list的相关性
        # dir = np.sign(self.result_dic['corr_sta'].loc['corr_tot'])；因子与label_list元素的总体相关系数，取sign
        def cal_reverse_sum(rate_arr):
            # 如果最大值、最小值的索引不是从小到大，将翻转
            index1 = np.argmax(rate_arr)
            index2 = np.argmin(rate_arr)
            if index1 < index2:  # 反向转换为从小到大排序
                rate_arr = np.flipud(rate_arr)
            # 差分
            rate_arr_diff = np.diff(rate_arr)
            # 对差分结果<0的部分求和，再求绝对值
            return np.abs(np.sum(rate_arr_diff[rate_arr_diff < 0]))

        #
        diff_dic = {'value': {'reverse': [0.6, 0.5], 'diff': [1, 1.5]},
                    'class': {'reverse': [0.6, 0.5], 'diff': [0.13, 0.18]}}
        stability_dic = {'value': [0.05, 0.1],
                         'class': [0.05, 0.1]}
        #
        diff_score = pd.Series([6, 3, 0], index=['high', 'mid', 'low'])
        s_s = 20 / len(month_df)
        stability_score = pd.Series([s_s, s_s / 2, 0, -s_s / 2, -s_s],
                                    index=['high', 'mid', 'low', 'reverse_mid', 'reverse_high'])
        # 月度数据中，因子和收益率相关性如果<0，且和总体方向一致，则转为正
        for label in label_test:
            month_df[label] = month_df[label] * dir[label]
        # diff_res_df：index代表时间段，columns为评价指标（收益率top-bottom、reverse阈值、分数（label_standard）
        #
        diff_res_df = pd.DataFrame()
        stability_df = pd.DataFrame(index=month_df.index)
        for label in label_test:
            diff, reverse = [], []
            # 按日期的分组，把不同日期段下标的，再按待测因子分组后，收益率（label）的总体极差（diff）、乱序部分收益率差分的和（reverse）
            for i in range(5):
                # 第i组日期的标的，每一组待测因子在label的均值
                rate_arr = double_group_df[label].unstack().iloc[i].values
                # 第i组日期的标的，所有组待测因子在label的均值的极差
                diff.append(max(rate_arr) - min(rate_arr))
                # 把第i组日期里，待测因子分组后，乱序部分的标的组合的label的差分结果的绝对值之和
                reverse.append(cal_reverse_sum(rate_arr))
            # 把diff和reverse存下来：每个时间段，按因子分组后的收益率极差、乱序部分绝对值之和
            diff_res_df['%s_diff' % (label)], diff_res_df['%s_reverse' % (label)] = diff, reverse
            # 总体极差 * 系数
            diff_res_df['%s_high_reverse' % (label)], diff_res_df['%s_mid_reverse' % (label)] = \
                diff_res_df['%s_diff' % (label)] * diff_dic[label]['reverse'][1], \
                diff_res_df['%s_diff' % (label)] * diff_dic[label]['reverse'][0]
            # 初始化standatd值为1
            diff_res_df['%s_standard' % (label)] = 1
            # 收益率极差大于中（高）阈值，且翻转分小于极差*中系数，重新赋予standard值为2（3）
            diff_res_df.loc[((diff_res_df['%s_diff' % (label)] > diff_dic[label]['diff'][0]) & \
                             (diff_res_df['%s_reverse' % (label)] < diff_res_df['%s_mid_reverse' % (label)])), \
                            '%s_standard' % (label)] = 2
            diff_res_df.loc[((diff_res_df['%s_diff' % (label)] > diff_dic[label]['diff'][1]) & \
                             (diff_res_df['%s_reverse' % (label)] < diff_res_df['%s_mid_reverse' % (label)])), \
                            '%s_standard' % (label)] = 3
            # 把label_stand的分替换为描述性评价，得到N（N = 5)段日期下因子从收益率角度的评价
            diff_res_df['%s_standard' % (label)] = diff_res_df['%s_standard' % (label)].replace(
                {1: 'low', 2: 'mid', 3: 'high'})
            #
            stability_df['%s_standard' % (label)] = np.nan
            # Tips:month_df和stability_df表的index一样，所以可以直接用month_df筛选后的索引来筛选sta表
            # 相关性>=0.1为high；相关性在[0.05,1)为mid；abs(相关性)<0.05为low
            # 相关性小于0，对应reverse_mid和high（因为已经翻转过）
            stability_df.loc[month_df[label] >= stability_dic[label][1], '%s_standard' % (label)] = 'high'
            stability_df.loc[(month_df[label] >= stability_dic[label][0]) & (month_df[label] < stability_dic[label][1]), \
                             '%s_standard' % (label)] = 'mid'
            stability_df.loc[(month_df[label] > -stability_dic[label][0]) & (month_df[label] < stability_dic[label][0]), \
                             '%s_standard' % (label)] = 'low'
            stability_df.loc[
                (month_df[label] <= -stability_dic[label][0]) & (month_df[label] > -stability_dic[label][1]), \
                '%s_standard' % (label)] = 'reverse_mid'
            stability_df.loc[month_df[label] <= -stability_dic[label][1], '%s_standard' % (label)] = 'reverse_high'
        stability_df['count'] = 1
        # 最终得分记录在sta_df
        sta_df = pd.DataFrame(index=['high', 'mid', 'low', 'reverse_mid', 'reverse_high', 'score'])
        for label in label_test:
            # 根据diff_res_df.label_standard分组后计数
            sta_df['%s_diff_score' % (label)] = diff_res_df.groupby('%s_standard' % (label)).count()[
                '%s_diff' % (label)]
            # 乘以定好的分值（high 6,mid 3,low 0），再求和
            sta_df.loc['score', '%s_diff_score' % (label)] = (sta_df['%s_diff_score' % (label)] * diff_score).sum()
            # 同样对stability_df计数，填充空值为0
            sta_df['%s_stability_score' % (label)] = stability_df.groupby('%s_standard' % (label)).count()['count']
            sta_df['%s_stability_score' % (label)] = sta_df['%s_stability_score' % (label)].fillna(0)
            # 时间越短，分越高（stability_score和时间有关）
            sta_df.loc['score', '%s_stability_score' % (label)] = (
                        sta_df['%s_stability_score' % (label)] * stability_score).sum()
        sta_df['tot_score'] = np.nan
        sta_df.loc['score', 'tot_score'] = sta_df.loc['score'].sum()
        return diff_res_df, sta_df

    # data_dic是一个字典，key是月份，value是basic_df切片后的数据
    # 返回字典，key是月份，value是补充双分组后的basic_df
    def get_double_sort_dic(self, sort_factor_list, data_dic, sort_factor_group_num=5, factor_group_num=10,
                            return_data=False):
        all_res_dic = {}
        for key, data in data_dic.items():
            # 根据data_dic的key和value（月度basic_df），把data按照sort_factor_list和待测因子双分组，得到分组后的data（加入了i,j的分组信息）
            res_dic = self.get_double_sort(sort_factor_list, data, sort_factor_group_num, factor_group_num, return_data)
            all_res_dic[key] = res_dic
        return all_res_dic

    # 双分组函数，第一分组依据在sort_factor_list中，第二分组依据为待测因子
    def get_double_sort(self, sort_factor_list, data=None, sort_factor_group_num=5, factor_group_num=10,
                        return_data=False):
        result_dic = {}
        for sort_factor in sort_factor_list:
            # 优先用data，否则data = basic_df
            data = self.basic_df.copy() if (data is None) else data
            data['sort_factor_group'], data['factor_group'] = np.nan, np.nan
            # 第一分组每层数量
            num_each_sort_factor_group = len(data) // sort_factor_group_num
            sort_factor_group_list = []
            for i in range(sort_factor_group_num):
                if i == 0:
                    sort_factor_group_list += [i] * (
                                len(data) - (sort_factor_group_num - 1) * num_each_sort_factor_group)
                else:
                    sort_factor_group_list += [i] * num_each_sort_factor_group
            data = data.sort_values(by=sort_factor)
            data['sort_factor_group'] = sort_factor_group_list

            after_data = pd.DataFrame()
            for i in range(sort_factor_group_num):
                # 取出第一分组后的第i层
                group_factor_data = data[data['sort_factor_group'] == i].copy()
                # 第二分组每层数量
                num_each_group = len(group_factor_data) // factor_group_num
                group_list = []
                for j in range(factor_group_num):
                    if j == 0:
                        group_list += [j] * (len(group_factor_data) - (factor_group_num - 1) * num_each_group)
                    else:
                        group_list += [j] * num_each_group
                group_factor_data = group_factor_data.sort_values(by='factor')
                group_factor_data['factor_group'] = group_list
                # 把第一分组后的第i层，写好了第二分组的组数，纳入after_data
                after_data = after_data.append(group_factor_data)
            # 把第一分组为i，第二分组为j的数据，取label_list里指标的均值，写入到tmp_result
            tmp_result = pd.DataFrame()
            for i in range(sort_factor_group_num):
                for j in range(factor_group_num):
                    tmp_result[(i, j)] = \
                    after_data[(after_data['sort_factor_group'] == i) & (after_data['factor_group'] == j)].mean()[
                        self.label_list]
            # 新增一个名为index的列，存储(i,j)，再把i,j写入到sort_factor_group和factor_group中
            tmp_result = tmp_result.T.reset_index()
            tmp_result['%s_group' % (sort_factor)] = tmp_result['index'].apply(lambda x: x[0])
            tmp_result['factor_group'] = tmp_result['index'].apply(lambda x: x[1])
            # 把index放回索引，但形式去掉了括号，删掉index
            tmp_result = tmp_result.set_index(['%s_group' % (sort_factor), 'factor_group']).drop(['index'], axis=1)
            # 如果return_data，则返回按第二分组后，label_list的均值；相当于按第一分组分层，在第一分组的每一层里，按待测因子排序，把每一层排序相同的取出来
            # 如果not return_data，则返回加上i,j的df
            if return_data:
                result_dic[sort_factor] = after_data.groupby('factor_group').mean()[self.label_list]
            else:
                result_dic[sort_factor] = tmp_result
        return result_dic

    # corr_month指月度口径下，因子与label_list中元素（return,class等）的相关系数
    # 得到因子与label_list元素的MIC、总体相关系数、月度相关系数的均值、标准差、均值/标准差
    def get_corr_sta(self, corr_month):
        sta_df = pd.DataFrame(index=self.label_list)
        # 计算互信息系数（MIC）:因子与收益率，因子与class
        if self.cal_mi:
            mine = MINE()
            mine.compute_score(self.basic_df['factor'], self.basic_df['value'])
            mi_value = mine.mic()
            sta_df.loc['value', 'mic_tot'] = mi_value
            mine_c = MINE()
            mine_c.compute_score(self.basic_df['factor'], self.basic_df['class'])
            mi_value_c = mine_c.mic()
            sta_df.loc['class', 'mic_tot'] = mi_value_c
        # 对label_list中元素（return,class等），计算因子与该元素的spearman相关系数(总体口径)，月度spearman相关系数的均值、标准差、均值/标准差
        sta_df['corr_tot'] = [self.basic_df['factor'].corr(self.basic_df[label], method='spearman') for label in
                              self.label_list]
        sta_df['corr_month_mean'] = [corr_month[label].mean() for label in self.label_list]
        sta_df['corr_month_std'] = [corr_month[label].std() for label in self.label_list]
        sta_df['corr_month_mean_std'] = sta_df['corr_month_mean'] / sta_df['corr_month_std']
        return sta_df.T

    # 按年份分组后，再在每年按因子大小分组计算label_list值
    def get_group_test_result_by_year(self, segment_number=None):
        segment_number = self.segment_number if segment_number is None else segment_number
        result_dic = {}
        # 按year分组，字典值为该年数据分组后label_list的值
        for year, year_data in self.basic_df.groupby('year'):
            result_dic[year] = self.get_group_test_result(data=year_data, segment_number=segment_number)
        return result_dic

    # 与get_distribution_style类似，但计算的是按因子值分组后，label_list的均值
    def get_group_test_result(self, data=None, segment_number=None):
        # 优先用方法里的层数、基础数据传参，如果为None则用类里的传参
        segment_number = self.segment_number if segment_number is None else segment_number
        data = self.basic_df if data is None else data
        # basic_df按因子大小排序，计算每层数据量
        sorted_factor_data = data.sort_values(by='factor').copy()
        num_each_group = int(len(sortedgroup_tot_time_sort_factor_data) / segment_number)
        group_index_list = []
        for i in range(segment_number):
            group_index_list = (group_index_list + [i] * num_each_group) if i != (segment_number - 1) \
                else (group_index_list + [i] * (
                        len(sorted_factor_data) - num_each_group * segment_number + num_each_group))
        sorted_factor_data['group'] = group_index_list
        return sorted_factor_data.groupby('group').mean()[self.label_list]

    # 和get_double_sort相比，区别是return_data为True,意味着返回的是双分组后，按第一分组分层，再按待测因子聚合后，label_list各个指标的均值
    def get_double_group_test_result(self, style_factor_list):
        data = self.get_double_sort(style_factor_list, sort_factor_group_num=20, factor_group_num=20, return_data=True)
        return data

    # 对整个时间段的basic_df，按因子大小分层，查看每一层的style_list中元素的均值
    def get_distribution_style(self, disribution_style_segment_num=20):
        if len(self.style_list) == 0:
            return None
        # basic_df排序
        factor_sorted_data = self.basic_df.sort_values(by='factor')
        # 每层数
        num_each_segment = len(factor_sorted_data) // disribution_style_segment_num
        index_list = []
        # 非最后一层：每层数个i;最后一层：剩下个i
        # 形如[1,1,1,2,2,2,3,3,3,3]
        for i in range(disribution_style_segment_num):
            if i < disribution_style_segment_num - 1:
                index_list += [i] * num_each_segment
            else:
                index_list += [i] * (len(factor_sorted_data) - len(index_list))
        # 'index'为所属层数编号
        factor_sorted_data['index'] = index_list
        # 把style对应列，两端去极值
        for style in self.style_list:
            up_quantile_data = factor_sorted_data[style].quantile(0.98)
            down_quantile_data = factor_sorted_data[style].quantile(0.02)
            factor_sorted_data.loc[factor_sorted_data[style] > up_quantile_data, style] = up_quantile_data
            factor_sorted_data.loc[factor_sorted_data[style] < down_quantile_data, style] = down_quantile_data
        # 返回style_list的每层均值
        distribution_style = factor_sorted_data.groupby('index').mean()[self.style_list]
        return distribution_style

    # 因子和style_list中元素的spearman相关系数
    # 返回Series,索引为style_list
    def get_corr_style(self):
        if len(self.style_list) == 0:
            return None
        style_corr = pd.DataFrame()
        style_corr['corr'] = self.basic_df[self.style_list].corrwith(self.basic_df['factor'], method='spearman')
        return style_corr

    # 把每个月的factor用空值补足到最大长度
    # df：columns = month
    def get_distribution_month(self):
        distribution_month = pd.DataFrame()
        for month, month_data in self.basic_df.groupby('month'):
            distribution_month[month] = list(month_data['factor']) + [np.nan] * (
                        self.max_num_one_month - len(month_data['factor']))
        return distribution_month

    # 同一个值（重复值）的比率
    def get_max_one_ratio(self):
        import collections
        sample_number = len(self.factor_df)
        factor_value_distribution = np.array(list(collections.Counter(self.factor_df['factor']).values()))
        factor_value_distribution.sort()
        max_same_number = factor_value_distribution[~0]  # ~0 = -1
        second_max_same_number = factor_value_distribution[~1:].sum()
        max_same_ratio = max_same_number / sample_number
        second_max_same_ratio = second_max_same_number / sample_number
        return pd.DataFrame([max_same_ratio, second_max_same_ratio], columns=['repeated_ratio'],
                            index=['first', 'first+second']).T

    # df:在in/out区间的离群值比率
    def get_in_out_distribution_score(self):
        # 按时间段切片
        in_factor_data = self.factor_df['factor'].loc[pd.Timestamp('20160101'):pd.Timestamp('20181231')]
        out_factor_data = self.factor_df['factor'].loc[pd.Timestamp('20180101'):pd.Timestamp('20190930')]
        # 分位数
        in_low_q, in_high_q = in_factor_data.quantile(0.2), in_factor_data.quantile(0.8)
        # out部分低于/高于in部分固定界限的比率
        out_lower_ratio = (out_factor_data <= in_low_q).mean()
        out_higher_ratio = (out_factor_data >= in_high_q).mean()

        # 下面是用3倍mad方法
        # 返回ser的离群值比率、中位数、mad
        def extreme_value_sta_in(ser, th=3):
            med = ser.median()
            mad = (ser - med).abs().median()
            extreme_pct = ((ser > (med + th * mad)) | (ser < (med - th * mad))).mean()
            return extreme_pct, med, mad

        # 返回ser的离群值比率
        def extreme_value_sta_out(ser, med, mad, th=3):
            extreme_pct = ((ser > (med + th * mad)) | (ser < (med - th * mad))).mean()
            return extreme_pct

        # in的离群值比率，阈值
        in_extreme_ratio, in_med, in_mad = extreme_value_sta_in(in_factor_data)
        # out按照In的阈值，得到的离群值比率
        out_extreme_ratio = extreme_value_sta_out(out_factor_data, in_med, in_mad)
        return pd.DataFrame([out_lower_ratio, out_higher_ratio, in_extreme_ratio, out_extreme_ratio]
                            , columns=['distribution_stats']
                            , index=['out_lower', 'out_higher', 'in_extreme', 'out_extreme']).T

    # 生成离群值占比、label表现等
    def get_in_out_LS_performance(self):
        #
        in_out_LS_performance = pd.DataFrame(index=self.label_list)
        for label in self.label_list:
            # 把factor和label按时间切分
            in_factor_data_with_label = self.basic_df[['factor', label]].loc[
                                        pd.Timestamp('20160101'):pd.Timestamp('20181231')]
            out_factor_data_with_label = self.basic_df[['factor', label]].loc[
                                         pd.Timestamp('20180101'):pd.Timestamp('20190930')]
            # in部分的分位数阈值
            thred_in_head = in_factor_data_with_label['factor'].quantile(0.15)
            thred_in_tail = in_factor_data_with_label['factor'].quantile(1 - 0.15)
            # in部分离群值均值
            in_head = in_factor_data_with_label[in_factor_data_with_label['factor'] <= thred_in_head][label].mean()
            in_tail = in_factor_data_with_label[in_factor_data_with_label['factor'] >= thred_in_tail][label].mean()
            # 以in部分阈值为基准，out部分离群值均值
            out_head = out_factor_data_with_label[out_factor_data_with_label['factor'] <= thred_in_head][label].mean()
            out_tail = out_factor_data_with_label[out_factor_data_with_label['factor'] >= thred_in_tail][label].mean()
            # 上述结果写入LS_p表，label作为index
            in_out_LS_performance.loc[label, 'in_head'] = in_head
            in_out_LS_performance.loc[label, 'in_tail'] = in_tail
            in_out_LS_performance.loc[label, 'out_head'] = out_head
            in_out_LS_performance.loc[label, 'out_tail'] = out_tail
        ## 按月切分
        # 每个月因子值数目、label在离群部分的均值
        in_out_LS_performance_month_df = pd.DataFrame()
        groupby_month_data = self.basic_df.groupby('month')
        # 每个月因子值的数目
        in_out_LS_performance_month_df['count'] = groupby_month_data.count()['factor']
        # 每个月label在离群部分的均值
        for label in self.label_list:
            in_out_LS_performance_month_df[label + '_head'] = groupby_month_data.apply(lambda x: x[x['factor'] \
                                                                                                   <= thred_in_head][
                label].mean())
            in_out_LS_performance_month_df[label + '_tail'] = groupby_month_data.apply(lambda x: x[x['factor'] \
                                                                                                   >= thred_in_tail][
                label].mean())
        ## 按num切分
        in_out_LS_performance_num_df = pd.DataFrame()
        # 45代表2016-2019.9共45个月，fix_num看作平均每个月的个数
        fix_num = int(len(self.basic_df) // 45)
        self.basic_df['fix_num_group'] = np.array(list(map(lambda x: x // fix_num, np.arange(len(self.basic_df)))))
        groupby_fix_num_data = self.basic_df.groupby('fix_num_group')
        # 按fix_num重新切割后每一组的个数
        in_out_LS_performance_num_df['count'] = groupby_fix_num_data.count()['factor']
        # 每个分组的离群值在label的均值
        for label in self.label_list:
            in_out_LS_performance_num_df[label + '_head'] = groupby_fix_num_data.apply(lambda x: \
                                                                                           x[x[
                                                                                                 'factor'] <= thred_in_head][
                                                                                               label].mean())
            in_out_LS_performance_num_df[label + '_tail'] = groupby_fix_num_data.apply(lambda x: \
                                                                                           x[x[
                                                                                                 'factor'] >= thred_in_tail][
                                                                                               label].mean())
        ## 按季节切分
        in_out_LS_performance_season_df = pd.DataFrame()
        # 'season' = xxxx年xx季度
        self.basic_df['season'] = self.basic_df.reset_index()['dt'].apply(
            lambda x: x.strftime('%Y') + '-' + str((int(x.strftime('%m')) - 1) // 3 + 1)).values
        groupby_season_data = self.basic_df.groupby('season')
        in_out_LS_performance_season_df['count'] = groupby_season_data.count()['factor']
        for label in self.label_list:
            in_out_LS_performance_season_df[label + '_head'] = groupby_season_data.apply(
                lambda x: x[x['factor'] <= thred_in_head][label].mean())
            in_out_LS_performance_season_df[label + '_tail'] = groupby_season_data.apply(
                lambda x: x[x['factor'] >= thred_in_tail][label].mean())

        return in_out_LS_performance, in_out_LS_performance_month_df, in_out_LS_performance_num_df, in_out_LS_performance_season_df

    # 获取basic_df中待测因子groupby month后的数量、与label_list中的spearman相关系数
    def get_corr_month(self):
        corr_month_df = pd.DataFrame()
        groupby_month_data = self.basic_df.groupby('month')
        corr_month_df['count'] = groupby_month_data.count()['factor']
        for label in self.label_list:
            corr_month_df[label] = groupby_month_data.apply(lambda x: x['factor'].corr(x[label], method='spearman'))
        # 获取每月最大数目:=max(每个月因子的最大数量,每个月label_list里元素的最大数量)
        self.max_num_one_month = max(
            [groupby_month_data.count()['factor'].max()] + [groupby_month_data.count()[label].max() for label in
                                                            self.label_list])
        return corr_month_df

    # 因子基本信息
    def get_factor_information(self):
        factor_information = pd.DataFrame()
        factor_information['Factor Info'] = pd.Series({'Factor Name': self.factor_name,
                                                       # 'Test Sample': self.test_sample,
                                                       'Label Type': self.return_type,
                                                       'Test Period': '%d - %d' % (self.start_date, self.end_date),
                                                       'Date Count': len(self.factor_df.unstack()),
                                                       'Sample Count': len(self.factor_df),
                                                       'Nan|Inf Count': len(self.factor_df) - len(self.factor_df[
                                                                                                      self.factor_df[
                                                                                                          'factor'] ==
                                                                                                      self.factor_df[
                                                                                                          'factor']]) + np.sum(
                                                           np.isinf(self.factor_df['factor']))})
        if self.test_sample == 'bt':
            factor_information[' '] = ['Segment Number', 'Buy Type', 'Last is Zt', 'First Over Threshold',
                                       'Break is Zt', 'Style List']
            factor_information['Settings'] = [self.segment_number, str(self.buy_type), str(self.last_is_zt),
                                              str(self.first_over_threshold), str(self.break_is_zt),
                                              str(self.style_list)]
        elif self.test_sample == 'zt':
            factor_information[' '] = ['Segment Number', 'Buy Type', 'Last is Zt', 'Open is Zt', 'First is Zt',
                                       'Style List']
            factor_information['Settings'] = [self.segment_number, str(self.buy_type), str(self.last_is_zt),
                                              str(self.open_is_zt), str(self.first_is_zt), str(self.style_list)]
        return factor_information

    # 和已有所有因子的相关性
    def get_corr_with_all_factor(self, group_num=5):
        corr_res = pd.DataFrame()
        corr_res['factor_corr'] = self.all_factor.corrwith(self.factor_df['factor'], method='spearman')
        corr_res['factor_corr_abs'] = corr_res['factor_corr'].abs()
        corr_res = corr_res.sort_values(by='factor_corr_abs', ascending=False)
        return corr_res[['factor_corr']].abs()

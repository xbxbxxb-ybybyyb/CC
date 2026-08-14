# -*- coding: utf-8 -*-
# @Time    : 2023/2/21 13:11
# @Author  : qinyuhao
from project_2_factor_test_v2 import pj2FactorTest
import pandas as pd
import numpy as np
import datetime as dt
import IO as IO


def generate_factors_pdf(date,
                         result_path,
                         test_factor_list,
                         save_name='Test Factors',
                         is_run_factor=False,
                         path_ori='/data/user/015585/01-因子挖掘/',
                         style_list=['free_turn', 'Lzt_ZT_Time', 'tradingday'],
                         start_date = 20160101,
                         end_date = 20181231,
                         buy_type = '0931',
                         lzt_pattern = [3, 4],
                         auto_get_df_ori = True):
    if auto_get_df_ori:
        sft_basic_path = '/data/user/018107/factor_zoo2/factor_lib_update/warehouse/warehouse_931/sft_basic_formal_931_20160101_20181231.h5'
        df_ori = IO.read_data([start_date, end_date], alt=sft_basic_path)
    else:
        df_ori = None
    now_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = '%s%s_%s.pdf' % (result_path, save_name, now_time)
    # 根据因子列表，生成h5路径字典
    def generate_factor_h5_path_dic(test_factor_list, date=date):
        factor_h5_path_dic = {}
        for factor_name in test_factor_list:
            path = path_ori + date + '/' + factor_name + '_20160101_20181231.h5'
            factor_h5_path_dic[factor_name] = path
        return factor_h5_path_dic
    # 根据因子列表，单因子回测并保存结果至字典
    def generate_factor_result_dic(factor_h5_path_dic, date=date,
                                   start_date=start_date, end_date=end_date,
                                   buy_type=buy_type,
                                   lzt_pattern=lzt_pattern,
                                   style_list=style_list):
        factor_result_dic = {}
        result_path = path_ori + date + '/'
        for key in factor_h5_path_dic:
            h5_path = factor_h5_path_dic[key]
            df = pd.read_hdf(h5_path)
            factor_test = pj2FactorTest(start_date=start_date, end_date=end_date,
                                        buy_type=buy_type,
                                        lzt_pattern=lzt_pattern,
                                        style_list=style_list,
                                        df_ori=df_ori)
            for col in df.columns:
                factor_test.factor_test(df[[col]], result_path, factor_corr_test=True, generate_pdf=False)
            factor_result_dic[key] = factor_test
        return factor_result_dic
    factor_h5_path_dic = generate_factor_h5_path_dic(test_factor_list=test_factor_list, date=date)
    factor_result_dic = generate_factor_result_dic(factor_h5_path_dic, date=date, style_list=style_list)
    # 生成函数的预定义函数
    from reportlab.lib.units import inch
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet
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
    label_list = factor_result_dic[list(factor_result_dic.keys())[0]].label_list
    style_list = factor_result_dic[list(factor_result_dic.keys())[0]].style_list
    def generate_first_page(canvas, doc):
        Title = save_name + ' Test Report'
        # 保存属性设置
        # 属性设置如果没有save，在showpage以后会被恢复
        # 样例：设置1，设置2，save，那么设置12会被保留，此时设置3，showpage，会按设置123生成，但结束后设置3不会被保留
        canvas.saveState()
        canvas.setTitle(title=Title)  # ?这一步用处不大，但正规
        PAGE_HEIGHT = defaultPageSize[1];  # 默认页面高度与宽度
        PAGE_WIDTH = defaultPageSize[0]
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, Title)  # 写TITLE
        canvas.setFont(psfontname='STSong-Light', size=6)  # 字体，宋体
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
            data = [(i if type(i) == str else (str(round(i * 100, round_num)) + '%')) for i in data]
        elif number_type == 'dcm':
            data = [(i if type(i) == str else str(round(i, round_num))) for i in data]
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
    def generate_plot(df, plot_name, x_label, y_label, plot_type='line', rot=0, plot_y0=False, \
                      use_index=True, secondary_y=False, stacked=False, fig_width=7.5, fig_height=2, color=None):
        plt.close()  # 关闭窗口，释放内存
        legend_on = True if min(df.shape) > 1 else False  # 是否显示图例

        # bins:纵坐标刻度，fontsize:刻度字体大小，rot:时间刻度标签显示的角度,secondary_y:把部分列以右y轴为基准画，stacked：是否堆叠，不同kind联立下有区别
        if color == None:
            if plot_type == 'hist':  # 直方图
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                                  rot=rot, use_index=use_index, secondary_y=secondary_y, bins=100)
            else:
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                                  rot=rot, use_index=use_index, secondary_y=secondary_y, stacked=stacked)
        else:
            if plot_type == 'hist':  # 直方图
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                                  rot=rot, use_index=use_index, secondary_y=secondary_y, bins=100, color=color)
            else:
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                                  rot=rot, use_index=use_index, secondary_y=secondary_y, stacked=stacked, color=color)
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
    def generate_double_sort(df):
        plt_rows = len(label_list)  # label的数目
        plt_cols = len(style_list)  # style的数目
        height_each_row = 1.7  # 5，每个label的高度
        height_calc = plt_rows * height_each_row  # label总高度
        fig_height = 20 / (7 / height_calc)
        fig = plt.figure(figsize=(10 * len(style_list), fig_height))  # 画布
        # ax = fig.add_subplot(plt_rows, )
        for (style, i) in zip(style_list, range(plt_cols)):  # 第i个style，第j个label
            for (label, j) in zip(label_list, range(plt_rows)):
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
    def generate_group_test_year(df, cols_list, test_sample):
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
                if test_sample == 'bt':
                    plt.ylim(0, 0.6)  # y轴显示范围
                elif test_sample == 'zt':
                    plt.ylim(0, 0.8)
            else:
                x = np.arange(len(df[year_list[i]]))
                plt.bar(x, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0], color='#e23e57')
                if test_sample == 'bt':
                    plt.ylim(-3, 2)
                elif test_sample == 'zt':
                    plt.ylim(-2, 2)
            plt.tick_params(labelsize=16)
            plt.title(year_list[i], fontsize=20, fontweight='bold')
        plt.tight_layout()
        imgdata = BytesIO()
        plt.savefig(imgdata, format='jpg', dpi=50)
        imgdata.seek(0)
        plt.close()
        return Image(imgdata, width=fig_width * inch, height=height_calc * inch)

    # 初始化
    pdf_styles = getSampleStyleSheet()  # 模板
    # Factor Information 基本信息的表格
    factor_info = factor_result_dic[list(factor_result_dic.keys())[0]].result_dic['factor_information']
    factor_info.loc['Factor Name', 'Factor Info'] = save_name
    factor_info.loc['Nan|Inf Count', 'Settings'] = 'Shown Below'
    h_factor_information = Paragraph('Factors Information', pdf_styles['Heading4'])  # 段落名称和模板
    col_type = ['str1'] * len(factor_info)
    t_factor_information = generate_table(factor_info, col_type, axis=0, reformat_type=True)
    elements = [h_factor_information, t_factor_information]
    # Factors & Style
    t_factor_style = pd.concat([pd.DataFrame(test_factor_list), pd.DataFrame(style_list)], axis=1)
    t_factor_style.columns = ['Factors', 'Style']
    t_factor_style.index = range(1, len(t_factor_style) + 1)
    t_factor_style = t_factor_style.fillna('')
    col_type = ['str1'] * len(t_factor_style)
    t_factor_style = generate_table(t_factor_style, col_type, axis=0, reformat_type=True)
    elements += [t_factor_style]
    # Repeat\Other(离群)
    h_repeat_extreme_sta = Paragraph('Repeat & Extreme Statistic', pdf_styles['Heading4'])
    h_repeat_extreme_sta.keepWithNext = True
    df_res_repeat_extreme_sta = pd.DataFrame()
    for key in factor_result_dic:
        result_dic = factor_result_dic[key].result_dic
        df_res_repeat_extreme_sta_key = pd.concat([result_dic['max_same_ratio'], result_dic['other_sta']], axis=1)
        df_res_repeat_extreme_sta_key.index = [key]
        df_res_repeat_extreme_sta = pd.concat([df_res_repeat_extreme_sta, df_res_repeat_extreme_sta_key], axis=0)
    t_repeat_extreme_sta = generate_table(df_res_repeat_extreme_sta, col_type=['pct2'] * len(df_res_repeat_extreme_sta),
                                          axis=0, reformat_type=True)
    elements += [h_repeat_extreme_sta, t_repeat_extreme_sta]

    # Correlation Statistic
    h_corr_sta = Paragraph('Correlation Statistic', pdf_styles['Heading4'])
    h_corr_sta.keepWithNext = True
    elements += [h_corr_sta]
    for label in label_list:
        together_corr_sta_label = []
        h_corr_sta_label = Paragraph(label, pdf_styles['Heading5'])
        together_corr_sta_label += [h_corr_sta_label]
        df_res_corr_sta_label = pd.DataFrame()
        for key in factor_result_dic:
            result_dic = factor_result_dic[key].result_dic
            df_res_corr_sta = result_dic['corr_sta'].copy()
            df_res_corr_sta.loc['corr_weight'] = result_dic['head_weight_ic']
            df_res_corr_sta.loc['corr_pure'] = result_dic['pure_ic']
            df_res_corr_sta = pd.DataFrame(df_res_corr_sta[label])
            df_res_corr_sta.columns = [key[11:]]
            df_res_corr_sta_label = pd.concat([df_res_corr_sta_label, df_res_corr_sta], axis=1)
        if len(df_res_corr_sta_label) == 7:
            col_type = ['pct2', 'pct2', 'pct2', 'pct2', 'dcm1', 'pct2', 'pct2']
        elif len(df_res_corr_sta_label) == 6:
            col_type = ['pct2', 'pct2', 'pct2', 'dcm1', 'pct2', 'pct2']
        t_corr_sta = generate_table(df_res_corr_sta_label, col_type, axis=0, reformat_type=True)
        together_corr_sta_label += [t_corr_sta]
        elements += [KeepTogether(together_corr_sta_label)]

    # 因子组相关
    h_corr_factors = Paragraph('Factors Corr', pdf_styles['Heading4'])
    h_corr_factors.keepWithNext = True
    elements += [h_corr_factors]
    factors_df = pd.DataFrame()
    for key in factor_result_dic:
        factor_df = pd.DataFrame(factor_result_dic[key].basic_df['factor'])
        factor_df.columns = [key[11:]]
        factors_df = pd.concat([factors_df, factor_df], axis=1)
    factors_df_corr = factors_df.corr(method='spearman')
    for i in range(len(test_factor_list)):
        for j in range(len(test_factor_list)):
            if i > j:
                factors_df_corr.iloc[i, j] = ''
    col_type = ['dcm2'] * len(test_factor_list)
    t_corr_factors = generate_table(factors_df_corr, col_type, axis=0, reformat_type=True)
    elements += [t_corr_factors]

    # Bank Corr Statistic
    if factor_result_dic[list(factor_result_dic.keys())[0]].factor_corr_test:
        h_corr_with_other = Paragraph('Bank Corr Statistic', pdf_styles['Heading4'])
        h_corr_with_other.keepWithNext = True
        elements += [h_corr_with_other]
        df_res_factors_corr_summary = pd.DataFrame()
        for key in factor_result_dic:
            df_res_factor_corr_summary = pd.DataFrame(factor_result_dic[key].result_dic['factor_corr_summary'])
            df_res_factor_corr_summary.columns = [key[11:]]
            df_res_factors_corr_summary = pd.concat([df_res_factors_corr_summary, df_res_factor_corr_summary], axis=1)
        df_res_factors_corr_summary = df_res_factors_corr_summary.fillna('')
        t_corr_with_other = generate_table(df_res_factors_corr_summary,
                                           col_type=['dcm4'] * len(df_res_factors_corr_summary),
                                           axis=0, reformat_type=True)
        elements += [t_corr_with_other]

    # Score Statistic
    h_score_sta = Paragraph('Score Statistic', pdf_styles['Heading4'])
    h_score_sta.keepWithNext = True
    df_factors_check_score_res = pd.DataFrame()
    for key in factor_result_dic:
        df_res_check_score_res_score = pd.DataFrame(factor_result_dic[key].result_dic['check_score_res'].loc['score'])
        df_res_check_score_res_score.columns = [key[11:]]
        df_factors_check_score_res = pd.concat([df_factors_check_score_res, df_res_check_score_res_score], axis=1)
    t_score_sta = generate_table(df_factors_check_score_res, col_type=['dcm2'] * len(df_factors_check_score_res),
                                 axis=0, reformat_type=True)
    elements += [h_score_sta, t_score_sta]

    # Head Statistic
    h_head_sta = Paragraph('Head Statistic', pdf_styles['Heading4'])
    h_head_sta.keepWithNext = True
    df_factors_head_group_quantile = pd.DataFrame()
    for key in factor_result_dic:
        df_res_head_group_quantile = pd.DataFrame(factor_result_dic[key].result_dic['head_group_quantile']['quantile'])
        df_res_head_group_quantile.columns = [key[11:]]
        df_factors_head_group_quantile = pd.concat([df_factors_head_group_quantile, df_res_head_group_quantile], axis=1)
    t_head_sta = generate_table(df_factors_head_group_quantile, col_type=['dcm2'] * len(df_factors_head_group_quantile),
                                axis=0, reformat_type=True)
    elements += [h_head_sta, t_head_sta]
    # Interval Score
    h_score_list_sta = Paragraph('Interval Score', pdf_styles['Heading4'])
    h_score_list_sta.keepWithNext = True
    df_factors_check_score_list = pd.DataFrame()
    for key in factor_result_dic:
        df_res_check_score_list = pd.DataFrame(factor_result_dic[key].result_dic['check_score_list']['tot_score'])
        df_res_check_score_list.columns = [key[11:]]
        df_factors_check_score_list = pd.concat([df_factors_check_score_list, df_res_check_score_list], axis=1)
    t_score_list_sta = generate_table(df_factors_check_score_list,
                                      col_type=['dcm2'] * len(result_dic['check_score_list']), axis=0, reformat_type=True)
    p_score_list_sta = generate_plot(df_factors_check_score_list,
                                     plot_name='Factors Interval Score', x_label='interval', y_label='score',
                                     plot_type='bar', stacked=False)
    elements += [h_score_list_sta, t_score_list_sta, p_score_list_sta]
    # IC Decay
    h_ic_decay = Paragraph('IC Decay', pdf_styles['Heading4'])
    h_ic_decay.keepWithNext = True
    df_factors_decay_ic = pd.DataFrame()
    for key in factor_result_dic:
        df_res_decay_ic = pd.DataFrame(factor_result_dic[key].result_dic['decay_ic'])
        df_res_decay_ic.columns = [key[11:]]
        df_factors_decay_ic = pd.concat([df_factors_decay_ic, df_res_decay_ic], axis=1)
    p_ic_decay = generate_plot(df_factors_decay_ic, plot_name='IC Decay', x_label='decay',
                               y_label='IC', plot_type='bar')
    elements += [KeepTogether([h_ic_decay, p_ic_decay])]
    # Monthly Corr
    together_monthly_corr = []
    h_monthly_corr = Paragraph('Monthly Corr', pdf_styles['Heading4'])
    h_monthly_corr.keepWithNext = True
    together_monthly_corr += [h_monthly_corr]
    for key in factor_result_dic:
        df_res_corr_month = factor_result_dic[key].result_dic['corr_month'][label_list]
        p_monthly_corr = generate_plot(df_res_corr_month,
                                       plot_name='Monthly Corr - Value&Class -' + key[11:],
                                       x_label='month', y_label='corr of value&class', plot_type='bar', rot=25)
        together_monthly_corr += [p_monthly_corr]
    elements += [KeepTogether(together_monthly_corr)]
    # Group Test
    h_group_test = Paragraph('Group Test', pdf_styles['Heading4'])
    together_group_test = []
    together_group_test += [h_group_test]
    color_dic = {'value': None,
                 'class': '#1b7fbd'}
    for label in label_list:
        color = color_dic[label]
        h_group_test_label = Paragraph('Group Test - ' + label, pdf_styles['Heading5'])
        together_group_test += [h_group_test_label]
        for key in factor_result_dic:
            p_group_test_value = generate_plot(factor_result_dic[key].result_dic['group_tot'][[label]],
                                               plot_name=key,
                                               x_label='Group', y_label='value', plot_type='bar',
                                               color=color)
            together_group_test += [p_group_test_value]
    elements += [KeepTogether(together_group_test)]
    for style in style_list:
        together_group_test_neu_label = []
        h_group_test_neu_label = Paragraph('Group Test - Class & %s Neutralization' % (style), pdf_styles['Heading5'])
        together_group_test_neu_label += [h_group_test_neu_label]
        for key in factor_result_dic:
            p_group_test_style = generate_plot(factor_result_dic[key].result_dic['group_tot_time_sort'][style][['class']],
                                               plot_name=key,
                                               x_label='Group', y_label='class', plot_type='bar', color=color_dic['class'])
            together_group_test_neu_label += [p_group_test_value]
        elements += [KeepTogether(together_group_test_neu_label)]

    h_group_test_year = Paragraph('Group Test Year', pdf_styles['Heading5'])
    elements += [h_group_test_year]
    for key in factor_result_dic:
        h_group_test_year_key = Paragraph(key[11:], pdf_styles['Heading6'])
        elements += [h_group_test_year_key]
        for label in label_list:
            p_group_test_value_year = generate_group_test_year(factor_result_dic[key].result_dic['group_by_year'],
                                                               cols_list=[label],
                                                               test_sample=factor_result_dic[
                                                                   list(factor_result_dic.keys())[0]].test_sample)
            elements += [p_group_test_value_year]
    # Distribution & Style
    h_ds = Paragraph('Distribution & Style', pdf_styles['Heading4'])
    h_ds.keepWithNext = True
    elements += [h_ds]
    # Dis
    h_dis = Paragraph('Distribution', pdf_styles['Heading5'])
    elements += [h_dis]
    for key in factor_result_dic:
        p_dis = generate_plot(factor_result_dic[key].result_dic['distribution_tot'],
                              plot_name='Distribution - ' + key, x_label='factor',
                              y_label='value', plot_type='line', use_index=False)
        elements += [p_dis]
    # Style
    for style in style_list:
        h_style = Paragraph('Style - ' + style, pdf_styles['Heading5'])
        elements += [h_style]
        for key in factor_result_dic:
            p_styles = generate_plot(factor_result_dic[key].result_dic['distribution_style'][style],
                                     plot_name='Style - %s - %s' % (style, key),
                                     x_label='sorted by factor', y_label='style', plot_type='line', use_index=False)
            elements += [p_styles]
    # Style Corr Table
    df_factors_corr_style = pd.DataFrame()
    for key in factor_result_dic:
        df_res_corr_style = factor_result_dic[key].result_dic['corr_style']
        df_res_corr_style.columns = [key]
        df_factors_corr_style = pd.concat([df_factors_corr_style, df_res_corr_style], axis=1)
    t_styles = generate_table(df_factors_corr_style, col_type=['pct2'] * len(df_factors_corr_style), axis=0,
                              reformat_type=True)
    elements += [t_styles]
    # Double Sort
    h_style_double_sort = Paragraph('Style - Factor Double Group', pdf_styles['Heading5'])
    elements += [h_style_double_sort]
    for key in factor_result_dic:
        h_style_double_sort_factor = Paragraph(key, pdf_styles['Heading6'])
        p_double_sort = generate_double_sort(factor_result_dic[key].result_dic['double_group_sort'])
        elements += [h_style_double_sort_factor, p_double_sort]
    # Standard Check
    if 'check_diff_res' in factor_result_dic[list(factor_result_dic.keys())[0]].result_dic:
        h_check_res = Paragraph('Standard Check', pdf_styles['Heading4'])
        h_check_res.keepWithNext = True
        elements += [h_check_res]
        for key in factor_result_dic:
            h_check_res_factor = Paragraph(key, pdf_styles['Heading5'])
            t_check_res_factor = generate_table(factor_result_dic[key].result_dic['check_diff_res'].T,
                                                ['pct2', 'pct2', 'pct2', 'pct2', 'str1'] * 2,
                                                axis=0,
                                                reformat_type=True)
            elements += [h_check_res_factor, t_check_res_factor]
    # Distribution Each Month
    h_dis_month = Paragraph('Distribution Each Month', pdf_styles['Heading4'])
    h_dis_month.keepWithNext = True
    elements += [h_dis_month]
    for key in factor_result_dic:
        p_dis_month = generate_plot(factor_result_dic[key].result_dic['distribution_month'],
                                    plot_name='Month Distribution - ' + key,
                                    x_label='factor',
                                    y_label='value',
                                    plot_type='box', rot=25)
        elements += [p_dis_month]
    # Correlation with Other Factors
    if factor_result_dic[list(factor_result_dic.keys())[0]].factor_corr_test:
        h_corr_all = Paragraph('Correlation with Other Factors', pdf_styles['Heading4'])
        elements += [h_corr_all]
        df_factors_factor_corr = pd.DataFrame()
        for key in factor_result_dic:
            df_res_factor_corr = pd.DataFrame(factor_result_dic[key].result_dic['factor_corr'].iloc[:20])
            df_res_factor_corr.columns = [key]
            df_factors_factor_corr = pd.concat([df_factors_factor_corr, df_res_factor_corr], axis=1)
        df_factors_factor_corr = df_factors_factor_corr.fillna('')
        t_corr_all = generate_table(df_factors_factor_corr,
                                    col_type=['dcm4'] * len(df_factors_factor_corr),
                                    axis=0, reformat_type=True)
        elements += [t_corr_all]
    # 收尾
    doc = SimpleDocTemplate(save_path, pagesize=letter, topMargin=80, bottomMargin=3)
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)
    return factor_result_dic
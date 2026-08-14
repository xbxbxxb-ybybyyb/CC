# -*- coding: utf-8 -*-

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
matplotlib.use('Agg')
import IO as IO

class pj2FactorTest:
    def __init__(self, start_date, end_date, segment_number=20, style_list=['T_free_turn', 'Next_o2pre'], cal_mi = True,
                 time_interval=[93000000, 145000000], last_is_zt=None, test_sample='bt',
                 first_over_threshold=False, break_is_zt=False,
                 first_is_zt=False, open_is_zt=False,
                 split_scene = None, # 分场景测试['EFS_pct5_T1_high','EFS_pct5_T1_low','T_o2pre_high','T_o2pre_low'
                                                              # 'label_14','label_23','ret2o_high','ret2o_low','cl0','cl1','cl2']
                 buy_type = '0931', sell_type = 'v', # buy_type = ['0930','0931','0941','o','od1'], sell_type = ['v','o','t','td1','od60']
                 lzt_pattern = [3,4], high_open = None # lzt_pattern = [1,2,3,4], high_open = 0.8
                 ):
        #test_sample = 'bt' or 'zt'
        self.start_date, self.end_date = start_date, end_date
        self.segment_number = segment_number
        self.style_list = style_list
        self.cal_mi = cal_mi
        self.last_is_zt = last_is_zt
        self.time_interval = time_interval
        self.test_sample = test_sample
        if test_sample == 'bt':
            self.break_is_zt = break_is_zt
            self.first_over_threshold = first_over_threshold
        elif test_sample =='zt':
            self.first_is_zt = first_is_zt
            self.open_is_zt = open_is_zt
        self.buy_type = buy_type
        self.sell_type = sell_type
        self.lzt_pattern = lzt_pattern
        self.high_open = high_open
        if buy_type == '0930':
            self.return_type = 'label_' + sell_type + '2o10'
        elif buy_type == '0931':
            self.return_type = 'label_' + sell_type + '2o10d1'
        elif buy_type == '0940':
            self.return_type = 'label_' + sell_type + '2o10d10'
        elif buy_type == 'o':
            self.return_type = 'label_' + sell_type + '2o'
        elif buy_type == 'od1':
            self.return_type = 'label_' + sell_type + '2od1'
        elif buy_type == 'od10':
            self.return_type = 'label_' + sell_type + '2od10'
        elif buy_type == 'od30':
            self.return_type = 'label_' + sell_type + '2od30'
        elif buy_type == 'od180':
            self.return_type = 'label_' + sell_type + '2od180'
        elif buy_type == 'to':
            self.return_type = 'label_' + sell_type + '2to'
        self.label_list = ['value','class']
        self.split_scene = split_scene
        self.basic_df = None
        self.load_data()
        self.result_dic = {}
        self.factor_name = None
        self.factor_df = None

    def load_data(self):
        # 修改这里的路径
        buy_type = self.buy_type
        ret_type = self.return_type
        split_scene = self.split_scene
        lzt_pattern = self.lzt_pattern
        high_open = self.high_open
        sft_basic_path = '/data/group/800463/data/project2_public/next_factor_lib/sft_update_next.pkl'
        df = pd.read_pickle(sft_basic_path).loc[pd.Timestamp(str(self.start_date)): pd.Timestamp(str(self.end_date))]

        saturn_filter=df['saturn_filter']==1
        st_filter = df['st_indicator'] != 1
        open_filter = (df['Next_open_is_zt'] == False) & (df['Next_open_is_dt'] == False)
        return_normal_filter = df[ret_type] != -3
        available_for_reaction_filter = df[ret_type] != -1
        can_buy_filter = df['Next_first_trans_ZT'] != 1
        all_filter = saturn_filter&st_filter & open_filter & return_normal_filter  & can_buy_filter
        if buy_type == '0930':
            all_filter = all_filter & available_for_reaction_filter
        if buy_type == '0931':
            all_filter = all_filter & ((df['Next_day_first_ZT_Time'] <= 93100000) == False)& ((df['Next_day_first_DT_Time'] <= 93100000) == False) & available_for_reaction_filter
        if buy_type == '0940':
            all_filter = all_filter & ((df['Next_day_first_ZT_Time'] <= 94000000) == False)& ((df['Next_day_first_DT_Time'] <= 93100000) == False) & available_for_reaction_filter

        # 新增高开filter
        if high_open is not None:
            high_open_filter = df['Next_o2pre'] <= 0.08
            all_filter = all_filter & high_open_filter

        #样本筛选
        df = df[all_filter]
        df = df.rename(columns = {ret_type:'value'})
        df['value'] = df['value'] * 100
        if (ret_type == 'label_td12od1') | (ret_type == 'label_t2o'):
            df['value'] = df['value'] * -1
        df['month'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y-%m')[2:]))
        df['year'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y')))
        df['class'] = df['value'] > 0
        df['tradingday'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: int(x.strftime('%Y%m%d'))))

        self.basic_df = df[['value', 'class', 'month', 'year']+self.style_list]

        all_factors_available = ['label_v2o10','label_v2o10d1','label_v2o10d10',
                                 'label_o2o10','label_o2o10d1','label_o2o10d10',
                                 'label_od602od1','label_t2o10',
                                 'label_od102o','label_od302od1','label_od602od30','label_od2402od180','label_od302od10',
                                 'T_day_first_ZT_Time','T_day_first_DT_Time','T_first_trans_ZT','T_open_is_zt', 'T_open_is_dt','st_indicator',
                                 'Next_day_first_ZT_Time','Next_day_first_DT_Time','Next_first_trans_ZT','Next_open_is_zt', 'Next_open_is_dt',]
        if ret_type in all_factors_available:
            all_factors_available.remove(ret_type)
        self.all_factor = df.drop(['value', 'class', 'month', 'year']+list(set(df.columns)&set(all_factors_available)), axis=1)

    def split(self, corr_month, split_month=6):
        dic ={}
        split_num = len(corr_month) // split_month
        for i in range(split_num):
            corr_ = corr_month.iloc[i*split_month:(i+1)*split_month] if (i!=(split_num-1)) else corr_month.iloc[i*split_month:]
            key = '%s~%s'%(min(corr_.index), max(corr_.index))
            dic[key] = corr_
        return dic

    def split_data(self, basic_df, keys):
        dic = {}
        for key in keys:
            start_month, end_month = key.split('~')[0], key.split('~')[1]
            df = basic_df[(basic_df['month']>=start_month) & (basic_df['month']<=end_month)]
            dic[key] = df
        return dic

    def extreme_value_sta(self):
        med = self.basic_df['factor'].median()
        mad = (self.basic_df['factor'] - med).abs().median()
        sta = pd.Series()
        sta['up_3MAD_rate'] = (self.basic_df['factor']>(med + 3 * mad)).mean()
        sta['down_3MAD_rate'] = (self.basic_df['factor'] < (med - 3 * mad)).mean()
        return sta

    def factor_test(self, factor_df, result_path, factor_corr_test=False, generate_pdf=True):
        if len(factor_df.columns)>1:
            print('factor_df must be only one column')
            raise Exception

        if factor_corr_test:
            check_res=pd.read_excel('/data/group/800463/data/project2_public/next_factor_lib/check_res_tot_saturnnext.xlsx')
            check_res = check_res.set_index('factor_name')[['in_score', 'in_IC_tot']]
            self.check_res=check_res

        self.factor_name = factor_df.columns[0]
        self.factor_df = pd.DataFrame(index=self.basic_df.index)   #basic_df过滤样本
        self.factor_df['factor'] = factor_df[self.factor_name]
        self.basic_df['factor'] = self.factor_df['factor']

        self.result_dic['factor_information'] = self.get_factor_information()

        self.result_dic['corr_month'] = self.get_corr_month()
        self.result_dic['corr_sta'] = self.get_corr_sta(self.result_dic['corr_month'])

        self.result_dic['distribution_tot'] = self.factor_df.sort_values(by='factor')
        self.result_dic['distribution_month'] = self.get_distribution_month()
        self.result_dic['distribution_style'] = self.get_distribution_style()
        self.result_dic['corr_style'] = self.get_corr_style()

        self.result_dic['group_tot'] = self.get_group_test_result()
        self.result_dic['group_tot_time_sort'] = self.get_double_group_test_result(self.style_list)

        self.result_dic['group_by_year'] = self.get_group_test_result_by_year()
        self.result_dic['double_group_sort'] = self.get_double_sort(sort_factor_list=self.style_list)

        self.result_dic['corr_month_dic'] = self.split(self.result_dic['corr_month'])
        data_dic = self.split_data(self.basic_df.copy(), list(self.result_dic['corr_month_dic'].keys()))
        self.result_dic['double_group_sort_dic'] = self.get_double_sort_dic(sort_factor_list=self.style_list, data_dic = data_dic)
        self.result_dic['extreme_value_sta'] = self.extreme_value_sta()
        if ('Next_o2pre' in self.result_dic['double_group_sort']):
            self.result_dic['check_diff_res'], self.result_dic['check_score_res'] = self.check_score(self.result_dic['double_group_sort']['Next_o2pre'].copy(), self.result_dic['corr_month'].copy(), np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
            self.result_dic['check_score_list'] = self.check_score_list(self.result_dic['double_group_sort_dic'].copy(), self.result_dic['corr_month_dic'].copy(), np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
        elif  ('tradingday' in self.result_dic['double_group_sort']):
            self.result_dic['check_diff_res'], self.result_dic['check_score_res'] = self.check_score(self.result_dic['double_group_sort']['tradingday'].copy(), self.result_dic['corr_month'].copy(), np.sign(self.result_dic['corr_sta'].loc['corr_tot']))
            self.result_dic['check_score_list'] = self.check_score_list(self.result_dic['double_group_sort_dic'].copy(), self.result_dic['corr_month_dic'].copy(), np.sign(self.result_dic['corr_sta'].loc['corr_tot']))

        other_sta = {'up_3MAD_rate':[self.result_dic['extreme_value_sta']['up_3MAD_rate']],'down_3MAD_rate':[self.result_dic['extreme_value_sta']['down_3MAD_rate']]}

        self.result_dic['other_sta'] = pd.DataFrame(other_sta, index=[''])
        # 20210324添加同一个值的阈值
        self.result_dic['max_same_ratio'] = self.get_max_one_ratio()
        # 20210428添加同时考虑样本内外的因子分布评价，只有在20160101到20190930才运行
        if (int(self.start_date) == 20160101) & (int(self.end_date) == 20190930):
            self.result_dic['distribution_stats'] = self.get_in_out_distribution_score()
            self.result_dic['in_out_LS_performance_stats'] = self.get_in_out_LS_performance()

        self.factor_corr_test = factor_corr_test
        if self.factor_corr_test:
            self.result_dic['factor_corr']= self.get_corr_with_all_factor()
            self.result_dic['factor_corr_summary'] = self.result_dic['factor_corr']
            self.result_dic['factor_corr_summary'] = self.result_dic['factor_corr_summary'][(self.result_dic['factor_corr_summary']['factor_corr']>0.65)]
            self.result_dic['factor_corr_summary'] = self.result_dic['factor_corr_summary'].join(self.check_res)
        now_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_pickle(self.result_dic, save_path='%s%s.pkl'%(result_path, self.factor_name))
        if generate_pdf:
            self.generate_pdf(self.result_dic, save_path='%s%s_%s.pdf' % (result_path, self.factor_name, now_time))

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
        plt.style.use('ggplot')
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        PAGE_HEIGHT = defaultPageSize[1];
        PAGE_WIDTH = defaultPageSize[0]
        fig_width = 7.5
        fig_height = 2
        def generate_first_page(canvas, doc):
            Title = 'Factor Test Report'
            canvas.saveState()
            canvas.setTitle(title='Factor Test Report')
            PAGE_HEIGHT = defaultPageSize[1];
            PAGE_WIDTH = defaultPageSize[0]
            canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, Title)
            canvas.setFont(psfontname='STSong-Light', size=6)
            canvas.restoreState()

        def generate_later_pages(canvas, doc):
            canvas.saveState()
            canvas.setFont(psfontname='STSong-Light', size=6)
            canvas.restoreState()

        def dataframe2str(df, col_type, axis, reformat_type):
            """get dataframe column, return string with format"""
            df = df if axis == 1 else df.T
            df_col = df.columns.tolist()
            df_row = df.index.tolist()
            df_str = [''] + df_row
            for col, ct in zip(df_col, col_type):
                data = [col] + num2str(df[col].values.tolist(), ct) if reformat_type == True else [col] + df[
                    col].values.tolist()
                df_str = np.vstack([df_str, data])
            df_str = df_str.T.tolist() if axis == 1 else df_str.tolist()
            return df_str

        def num2str(data, data_type):
            """take number and change format, return list of string"""
            round_num = int(data_type[-1])
            number_type = data_type[:-1]
            if number_type == 'pct':
                data = [str(round(i * 100, round_num)) + '%' for i in data]
            elif number_type == 'dcm':
                data = [str(round(i, round_num)) for i in data]
            return data

        def generate_table(df, col_type, axis, reformat_type):
            df_str = dataframe2str(df, col_type, axis, reformat_type)
            df_str[0] = [i.encode('utf-8') for i in df_str[0]]
            t = Table(df_str)
            mytable = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                  ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                  ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light')])
            t.setStyle(mytable)
            return t

        def generate_plot(df, plot_name, x_label, y_label, plot_type='line', color='#e23e57', rot=0, plot_y0=False, use_index=True, secondary_y=False, stacked=False, fig_width=7.5, fig_height=2):
            plt.close()
            legend_on = True if min(df.shape) > 1 else False
            if plot_type == 'hist':
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                                  color=color, rot=rot, use_index=use_index, secondary_y=secondary_y, bins=100)
            else:
                df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                                  color=color, rot=rot, use_index=use_index, secondary_y=secondary_y, stacked=stacked)
            df_plot.set_title(plot_name, fontsize=20)
            df_plot.set_xlabel(x_label, fontsize=16)
            df_plot.set_ylabel(y_label, fontsize=16)

            if plot_y0: plt.axhline(y=0, alpha=2, color='#414141')
            imgdata = BytesIO()
            df_plot.figure.savefig(imgdata, format='jpg', dpi=50)
            imgdata.seek(0)
            plt.close()
            return Image(imgdata, width=fig_width * inch, height=fig_height * inch+10)

        def generate_double_sort(df):
            plt_rows = len(self.label_list)
            plt_cols = len(self.style_list)
            height_each_row = 1.7  # 5
            height_calc = plt_rows * height_each_row
            fig_height = 20 / (7 / height_calc)
            fig = plt.figure(figsize=(10*len(self.style_list), fig_height))
            #ax = fig.add_subplot(plt_rows, )
            for (style, i) in zip(self.style_list, range(plt_cols)):
                for (label, j) in zip(self.label_list, range(plt_rows)):
                    ax = fig.add_subplot(plt_rows, plt_cols, plt_cols*j+i+1)
                    d = df[style][label].unstack()
                    d.plot(ax=ax, kind='bar')
                    ax.set_title('%s-%s'%(style, label))
                    plt.tick_params(labelsize=16)
            plt.tight_layout()
            plt.legend(loc='best')
            imgdata = BytesIO()
            plt.savefig(imgdata, format='jpg', dpi=100)
            imgdata.seek(0)
            plt.close()
            return Image(imgdata, width=fig_width * inch, height=height_calc * inch)

        def generate_group_test_year(df, cols_list):
            year_list = list(df.keys())#list(set(df.index.get_level_values(0)))
            year_num = len(year_list)
            plt_rows = int(np.ceil(year_num / 2))
            height_each_row = 1.7  # 5
            height_calc = plt_rows * height_each_row
            fig_height = 20 / (7 / height_calc)
            plt.figure(figsize=(20, fig_height))
            for i in range(year_num):
                plt.subplot(plt_rows, 2, i + 1)
                width = 0.3
                if cols_list==['class']:
                    x = np.arange(len(df[year_list[i]]))
                    plt.bar(x-width/2, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0],color='#1b7fbd')
                    # plt.bar(x+width/2, list(df[year_list[i]][cols_list[1]]), width=width, label =cols_list[1], color='#525252')
                    if self.test_sample=='bt':
                        plt.ylim(0, 0.6)
                    elif self.test_sample=='zt':
                        plt.ylim(0, 0.8)
                else:
                    x = np.arange(len(df[year_list[i]]))
                    plt.bar(x, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0], color='#e23e57')
                    if self.test_sample=='bt':
                        plt.ylim(-3, 2)
                    elif self.test_sample=='zt':
                        plt.ylim(-2, 2)
                plt.tick_params(labelsize=16)
                plt.title(year_list[i], fontsize=20, fontweight='bold')

            plt.tight_layout()
            imgdata = BytesIO()
            plt.savefig(imgdata, format='jpg', dpi=50)
            imgdata.seek(0)
            plt.close()
            return Image(imgdata, width=fig_width * inch, height=height_calc * inch)

        pdf_styles = getSampleStyleSheet()
        h_factor_information = Paragraph('Factor Information', pdf_styles['Heading4'])
        col_type = ['str1'] * len(result_dic['factor_information'])
        t_factor_information = generate_table(result_dic['factor_information'], col_type, axis=0, reformat_type=False)
        h_score_sta = Paragraph('Score Statistic', pdf_styles['Heading4'])
        t_score_sta = generate_table(result_dic['check_score_res'], col_type=['dcm0', 'dcm0', 'dcm0', 'dcm0', 'dcm0', 'dcm2'], axis=0, reformat_type=True)
        h_repeat_sta = Paragraph('Repeat Statistic', pdf_styles['Heading4'])
        t_repeat_sta = generate_table(result_dic['max_same_ratio'], col_type=['dcm2', 'dcm2'], axis=0, reformat_type=True)
        h_other_sta = Paragraph('Other Statistic', pdf_styles['Heading4'])
        t_other_sta = generate_table(result_dic['other_sta'],
                                     col_type=['pct2'], axis=0,
                                     reformat_type=True)
        elements = [h_factor_information, t_factor_information, h_other_sta, t_other_sta, h_score_sta, t_score_sta,h_repeat_sta,t_repeat_sta]

        h_score_list_sta = Paragraph('Interval Score', pdf_styles['Heading4'])
        t_score_list_sta = generate_table(result_dic['check_score_list'], col_type=['dcm2']*len(result_dic['check_score_list']), axis=0, reformat_type=True)
        elements += [h_score_list_sta, t_score_list_sta]

        if self.factor_corr_test:
            h_corr_with_other = Paragraph('Bank Corr Statistic - %d high corr factor'%(len(result_dic['factor_corr_summary'])), pdf_styles['Heading4'])
            elements.append(h_corr_with_other)
            if len(result_dic['factor_corr_summary'])>0:
                t_corr_with_other = generate_table(result_dic['factor_corr_summary'], col_type=['dcm4']*len(result_dic['factor_corr_summary']), axis=0, reformat_type=True)
                elements.append(t_corr_with_other)

        h_corr_sta = Paragraph('Correlation Statistic', pdf_styles['Heading4'])
        if len(result_dic['corr_sta'])==5:
            col_type = ['pct2', 'pct2', 'pct2', 'pct2', 'dcm1']
        elif len(result_dic['corr_sta'])==4:
            col_type = ['pct2', 'pct2', 'pct2', 'dcm1']
        t_corr_sta = generate_table(result_dic['corr_sta'], col_type, axis=0, reformat_type=True)
        elements += [h_corr_sta, t_corr_sta]

        p_score_list_sta = generate_plot(result_dic['check_score_list'][['class_diff_score', 'class_stability_score', 'value_diff_score', 'value_stability_score']], plot_name='Interval Score', x_label='interval', y_label='score', color=['#525252', '#1f4068', '#900d0d', '#e23e57'], plot_type='bar', stacked=True)
        elements += [h_score_list_sta, p_score_list_sta]

        h_monthly_corr = Paragraph('Monthly Corr', pdf_styles['Heading4'])
        p_monthly_corr = generate_plot(result_dic['corr_month'][['value','class']], plot_name='Monthly Corr - Value&Class', x_label='month', y_label='corr of value&class', plot_type='bar', color=['#e23e57', '#1b7fbd'], rot=25)
        elements += [h_monthly_corr, p_monthly_corr]

        h_group_test = Paragraph('Group Test', pdf_styles['Heading4'])
        p_group_test_value = generate_plot(result_dic['group_tot'][['value']], plot_name='Group Test - Value', x_label='Group',
                                           y_label='value', plot_type='bar')
        p_group_test_cm = generate_plot(result_dic['group_tot'][['class']], plot_name='Group Test - Class',
                                        x_label='Group', y_label='class', plot_type='bar', color=['#1b7fbd'])
        p_group_test_cm_with_style0 = generate_plot(self.result_dic['group_tot_time_sort'][self.style_list[0]][['class']], plot_name='Group Test - Class - %s Neutralization'%(self.style_list[0]),
                                                   x_label='Group', y_label='class', plot_type='bar',color=['#1b7fbd'])
        p_group_test_cm_with_style1 = generate_plot(self.result_dic['group_tot_time_sort'][self.style_list[1]][['class']],
                                                    plot_name='Group Test - Class - %s Neutralization' % (self.style_list[1]),
                                                    x_label='Group', y_label='class', plot_type='bar', color=['#1b7fbd'])

        p_group_test_value_year = generate_group_test_year(result_dic['group_by_year'], cols_list=['value'])
        p_group_test_value_cm = generate_group_test_year(result_dic['group_by_year'], cols_list=['class'])

        elements += [h_group_test, p_group_test_value, p_group_test_cm, p_group_test_cm_with_style0, p_group_test_cm_with_style1, p_group_test_value_year, p_group_test_value_cm]

        h_ds = Paragraph('Distribution & Style', pdf_styles['Heading4'])
        p_dis = generate_plot(result_dic['distribution_tot'], plot_name='Distribution', x_label='factor',
                              y_label='value', plot_type='line', color=['#211717'], use_index=False)
        p_styles0 = generate_plot(result_dic['distribution_style'][self.style_list[0]], plot_name='Style - %s'%(self.style_list[0]),
                                 x_label='sorted by factor', y_label='style', plot_type='line',
                                 color=['#211717'], use_index=False)
        p_styles1 = generate_plot(result_dic['distribution_style'][self.style_list[1]], plot_name='Style - %s' % (self.style_list[1]),
                                 x_label='sorted by factor', y_label='style', plot_type='line',
                                 color=['#211717'], use_index=False)

        t_styles = generate_table(result_dic['corr_style'], col_type=['pct2', 'pct2'], axis=0, reformat_type=True)
        p_double_sort = generate_double_sort(result_dic['double_group_sort'])
        elements += [h_ds, p_dis, p_styles0, p_styles1, t_styles, p_double_sort]

        if 'check_diff_res' in self.result_dic:
            h_check_res = Paragraph('Standard Check', pdf_styles['Heading4'])
            t_check_res = generate_table(result_dic['check_diff_res'].T, ['pct2', 'pct2', 'pct2', 'pct2', 'str1']*2, axis=0,
                                         reformat_type=True)
            elements += [h_check_res, t_check_res]

        h_dis_month = Paragraph('Distribution Each Month', pdf_styles['Heading4'])
        p_dis_month = generate_plot(result_dic['distribution_month'], plot_name='Month Distribution', x_label='factor',
                                    y_label='value', plot_type='box', rot=25, color='#414141')
        elements += [h_dis_month, p_dis_month]

        if self.factor_corr_test:
            h_corr_all = Paragraph('Correlation with Other Factors', pdf_styles['Heading4'])
            t_corr_all = generate_table(result_dic['factor_corr'].iloc[:20], col_type=['dcm4']*20, axis=0, reformat_type=True)
            elements += [h_corr_all, t_corr_all]

        doc = SimpleDocTemplate(save_path, pagesize=letter, topMargin=80, bottomMargin=3)
        doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)

    def save_pickle(self, result_dic, save_path):
        with open(save_path, 'wb') as input:
            pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)

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
        res_df['standard'] = res_df['standard'].replace({1:'low', 2:'mid', 3:'high'})
        return res_df.T

    def check_score_list(self, double_group_df_dic, month_df_dic, dir, label_test=['value']):
        keys = list(double_group_df_dic.keys())
        res_df = pd.DataFrame()
        for key in keys:
            double_group_df, month_df = double_group_df_dic[key], month_df_dic[key]
            x, score_df = self.check_score(double_group_df[self.style_list[1]], month_df, dir)
            res_df[key] = score_df.loc['score']
        return res_df.T.sort_index()

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
        return diff_res_df , sta_df

    def get_double_sort_dic(self, sort_factor_list, data_dic, sort_factor_group_num=5, factor_group_num=10, return_data=False):
        all_res_dic = {}
        for key, data in data_dic.items():
            res_dic = self.get_double_sort(sort_factor_list, data, sort_factor_group_num, factor_group_num, return_data)
            all_res_dic[key] = res_dic
        return all_res_dic

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

    def get_corr_sta(self, corr_month):
        sta_df = pd.DataFrame(index=self.label_list)
        if self.cal_mi:
            mine = MINE()
            mine.compute_score(self.basic_df['factor'], self.basic_df['value'])
            mi_value = mine.mic()
            sta_df.loc['value','mic_tot'] = mi_value
            mine_c = MINE()
            mine_c.compute_score(self.basic_df['factor'], self.basic_df['class'])
            mi_value_c = mine_c.mic()
            sta_df.loc['class','mic_tot'] = mi_value_c
        sta_df['corr_tot'] = [self.basic_df['factor'].corr(self.basic_df[label], method='spearman') for label in self.label_list]
        sta_df['corr_month_mean'] = [corr_month[label].mean() for label in self.label_list]
        sta_df['corr_month_std'] = [corr_month[label].std() for label in self.label_list]
        sta_df['corr_month_mean_std'] = sta_df['corr_month_mean'] / sta_df['corr_month_std']
        return sta_df.T

    def get_group_test_result_by_year(self, segment_number=None):
        segment_number = self.segment_number if segment_number is None else segment_number
        result_dic = {}
        for year, year_data in self.basic_df.groupby('year'):
            result_dic[year] =self.get_group_test_result(data=year_data, segment_number=segment_number)
        return result_dic

    def get_group_test_result(self, data=None, segment_number=None):
        segment_number = self.segment_number if segment_number is None else segment_number
        data = self.basic_df if data is None else data

        sorted_factor_data = data.sort_values(by='factor').copy()
        num_each_group = int(len(sorted_factor_data) / segment_number)
        group_index_list = []
        for i in range(segment_number):
            group_index_list = (group_index_list + [i] * num_each_group) if i != (segment_number - 1) \
                else (group_index_list + [i] * (len(sorted_factor_data) - num_each_group * segment_number + num_each_group))
        sorted_factor_data['group'] = group_index_list
        return sorted_factor_data.groupby('group').mean()[self.label_list]

    def get_double_group_test_result(self, style_factor_list):
        data = self.get_double_sort(style_factor_list, sort_factor_group_num=20, factor_group_num=20, return_data=True)
        return data

    def get_distribution_style(self, disribution_style_segment_num=20):
        if len(self.style_list)==0:
            return None
        factor_sorted_data = self.basic_df.sort_values(by='factor')
        num_each_segment = len(factor_sorted_data) // disribution_style_segment_num
        index_list = []
        for i in range(disribution_style_segment_num):
            if i < disribution_style_segment_num-1:
                index_list += [i] * num_each_segment
            else:
                index_list += [i] * (len(factor_sorted_data) - len(index_list))
        factor_sorted_data['index'] = index_list
        #两端去极值
        for style in self.style_list:
            up_quantile_data = factor_sorted_data[style].quantile(0.98)
            down_quantile_data = factor_sorted_data[style].quantile(0.02)
            factor_sorted_data.loc[factor_sorted_data[style] > up_quantile_data, style] = up_quantile_data
            factor_sorted_data.loc[factor_sorted_data[style] < down_quantile_data, style] = down_quantile_data
        distribution_style = factor_sorted_data.groupby('index').mean()[self.style_list]
        return distribution_style

    def get_corr_style(self):
        if len(self.style_list)==0:
            return None
        style_corr = pd.DataFrame()
        style_corr['corr'] = self.basic_df[self.style_list].corrwith(self.basic_df['factor'], method='spearman')
        return style_corr

    def get_distribution_month(self):
        distribution_month = pd.DataFrame()
        for month, month_data in self.basic_df.groupby('month'):
            distribution_month[month] = list(month_data['factor']) + [np.nan] * (self.max_num_one_month - len(month_data['factor']))
        return distribution_month

    def get_max_one_ratio(self):
        import collections
        sample_number = len(self.factor_df)
        factor_value_distribution = np.array(list(collections.Counter(self.factor_df['factor']).values()))
        factor_value_distribution.sort()
        max_same_number = factor_value_distribution[~0]
        second_max_same_number = factor_value_distribution[~1:].sum()
        max_same_ratio = max_same_number / sample_number
        second_max_same_ratio = second_max_same_number / sample_number
        return pd.DataFrame([max_same_ratio, second_max_same_ratio],columns = ['repeated_ratio'] ,index = ['first','first+second']).T

    def get_in_out_distribution_score(self):
        in_factor_data = self.factor_df['factor'].loc[pd.Timestamp('20160101'):pd.Timestamp('20181231')]
        out_factor_data = self.factor_df['factor'].loc[pd.Timestamp('20180101'):pd.Timestamp('20190930')]
        in_low_q,in_high_q = in_factor_data.quantile(0.2),in_factor_data.quantile(0.8)
        out_lower_ratio = (out_factor_data<=in_low_q).mean()
        out_higher_ratio = (out_factor_data>=in_high_q).mean()
        def extreme_value_sta_in(ser, th=3):
            med = ser.median()
            mad = (ser - med).abs().median()
            extreme_pct = ((ser > (med + th * mad)) | (ser < (med - th * mad))).mean()
            return extreme_pct, med, mad
        def extreme_value_sta_out(ser, med, mad, th=3):
            extreme_pct = ((ser > (med + th * mad)) | (ser < (med - th * mad))).mean()
            return extreme_pct
        in_extreme_ratio, in_med, in_mad = extreme_value_sta_in(in_factor_data)
        out_extreme_ratio = extreme_value_sta_out(out_factor_data, in_med, in_mad)
        return pd.DataFrame([out_lower_ratio,out_higher_ratio,in_extreme_ratio, out_extreme_ratio]
                            ,columns = ['distribution_stats']
                            ,index = ['out_lower','out_higher','in_extreme','out_extreme']).T

    def get_in_out_LS_performance(self):
        in_out_LS_performance = pd.DataFrame(index = self.label_list)
        for label in self.label_list:
            in_factor_data_with_label = self.basic_df[['factor',label]].loc[pd.Timestamp('20160101'):pd.Timestamp('20181231')]
            out_factor_data_with_label = self.basic_df[['factor',label]].loc[pd.Timestamp('20180101'):pd.Timestamp('20190930')]
            thred_in_head = in_factor_data_with_label['factor'].quantile(0.15)
            thred_in_tail = in_factor_data_with_label['factor'].quantile(1-0.15)
            in_head = in_factor_data_with_label[in_factor_data_with_label['factor']<=thred_in_head][label].mean()
            in_tail = in_factor_data_with_label[in_factor_data_with_label['factor']>=thred_in_tail][label].mean()
            out_head = out_factor_data_with_label[out_factor_data_with_label['factor']<=thred_in_head][label].mean()
            out_tail = out_factor_data_with_label[out_factor_data_with_label['factor']>=thred_in_tail][label].mean()
            in_out_LS_performance.loc[label,'in_head'] = in_head
            in_out_LS_performance.loc[label,'in_tail'] = in_tail
            in_out_LS_performance.loc[label,'out_head'] = out_head
            in_out_LS_performance.loc[label,'out_tail'] = out_tail
        in_out_LS_performance_month_df = pd.DataFrame()
        groupby_month_data = self.basic_df.groupby('month')
        in_out_LS_performance_month_df['count'] = groupby_month_data.count()['factor']
        for label in self.label_list:
            in_out_LS_performance_month_df[label+'_head'] = groupby_month_data.apply(lambda x: x[x['factor']<=thred_in_head][label].mean())
            in_out_LS_performance_month_df[label+'_tail'] = groupby_month_data.apply(lambda x: x[x['factor']>=thred_in_tail][label].mean())
        in_out_LS_performance_num_df = pd.DataFrame()
        fix_num = int(len(self.basic_df)//45)
        self.basic_df['fix_num_group'] = np.array(list(map(lambda x:x//fix_num,np.arange(len(self.basic_df)))))
        groupby_fix_num_data = self.basic_df.groupby('fix_num_group')
        in_out_LS_performance_num_df['count'] = groupby_fix_num_data.count()['factor']
        for label in self.label_list:
            in_out_LS_performance_num_df[label+'_head'] = groupby_fix_num_data.apply(lambda x: x[x['factor']<=thred_in_head][label].mean())
            in_out_LS_performance_num_df[label+'_tail'] = groupby_fix_num_data.apply(lambda x: x[x['factor']>=thred_in_tail][label].mean())
        in_out_LS_performance_season_df = pd.DataFrame()
        self.basic_df['season'] = self.basic_df.reset_index()['dt'].apply(lambda x:x.strftime('%Y')+'-'+str((int(x.strftime('%m'))-1)//3+1)).values
        groupby_season_data = self.basic_df.groupby('season')
        in_out_LS_performance_season_df['count'] = groupby_season_data.count()['factor']
        for label in self.label_list:
            in_out_LS_performance_season_df[label+'_head'] = groupby_season_data.apply(lambda x: x[x['factor']<=thred_in_head][label].mean())
            in_out_LS_performance_season_df[label+'_tail'] = groupby_season_data.apply(lambda x: x[x['factor']>=thred_in_tail][label].mean())

        return in_out_LS_performance, in_out_LS_performance_month_df, in_out_LS_performance_num_df, in_out_LS_performance_season_df

    def get_corr_month(self):
        corr_month_df = pd.DataFrame()
        groupby_month_data = self.basic_df.groupby('month')
        corr_month_df['count'] = groupby_month_data.count()['factor']
        for label in self.label_list:
            corr_month_df[label] = groupby_month_data.apply(lambda x: x['factor'].corr(x[label], method='spearman'))
        self.max_num_one_month = max(
            [groupby_month_data.count()['factor'].max()] + [groupby_month_data.count()[label].max() for label in self.label_list])
        return corr_month_df

    def get_factor_information(self):
        factor_information = pd.DataFrame()
        factor_information['Factor Info'] = pd.Series({'Factor Name': self.factor_name,
                                                       # 'Test Sample': self.test_sample,
                                                       'Label Type': self.return_type,
                                                       'Test Period': '%d - %d' % (self.start_date, self.end_date),
                                                       'Date Count': len(self.factor_df.unstack()),
                                                       'Sample Count': len(self.factor_df),
                                                       'Nan|Inf Count': len(self.factor_df) - len(self.factor_df[self.factor_df['factor'] == self.factor_df['factor']])+np.sum(np.isinf(self.factor_df['factor']))})
        if self.test_sample == 'bt':
            factor_information[' '] = ['Segment Number', 'Buy Type', 'Last is Zt', 'First Over Threshold', 'Break is Zt', 'Style List']
            factor_information['Settings'] = [self.segment_number, str(self.buy_type), str(self.last_is_zt),
                                              str(self.first_over_threshold), str(self.break_is_zt) ,str(self.style_list)]
        elif self.test_sample == 'zt':
            factor_information[' '] = ['Segment Number', 'Buy Type', 'Last is Zt', 'Open is Zt', 'First is Zt', 'Style List']
            factor_information['Settings'] = [self.segment_number, str(self.buy_type), str(self.last_is_zt),
                                              str(self.open_is_zt), str(self.first_is_zt), str(self.style_list)]
        return factor_information

    def get_corr_with_all_factor(self, group_num=5):
        corr_res = pd.DataFrame()
        corr_res['factor_corr'] = self.all_factor.corrwith(self.factor_df['factor'], method='spearman')
        corr_res['factor_corr_abs'] = corr_res['factor_corr'].abs()
        corr_res = corr_res.sort_values(by='factor_corr_abs', ascending=False)
        return corr_res[['factor_corr']].abs()



if __name__ == '__main__':
    start_date, end_date = 20160101, 20191231

    df0 = pd.read_hdf('/data/user/018107/tmp/test_last_factor.h5')
    result_path = '/data/user/018107/tmp/'
    factor_test = pj2FactorTest(start_date, end_date)
    factor_test.factor_test(df0, result_path, factor_corr_test=True)

    df1= pd.read_hdf('/data/user/018107/tmp/test_trade_factor.h5')
    result_path = '/data/user/018107/tmp/'
    factor_test = pj2FactorTest(start_date, end_date)
    factor_test.factor_test(df1, result_path, factor_corr_test=True)

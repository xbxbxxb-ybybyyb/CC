import os
import pandas as pd
import numpy as np
import pickle
import datetime as dt
import sys
sys.path.append("../")
from multifactor.IO import IO as self_IO
sys.path.append("/..")

class strongFactorTest:
    def __init__(self, start_date, end_date, segment_number=20, before_day_zt=[-1, 0], style_list=['price', 'time'], time_interval=[93000000, 150000000], strong_type=[3], label_list=['value', 'class', 'mixed']):
        self.start_date, self.end_date = start_date, end_date
        self.segment_number = segment_number
        self.style_list = style_list
        self.before_day_zt = before_day_zt
        self.time_interval = time_interval
        self.strong_type = strong_type
        self.label_list = label_list
        self.basic_df = None
        self.load_data()
        self.result_dic = {}
        self.factor_name = None
        self.factor_df = None

    def load_data(self):
        def cal_time_from_open(trade_time):
            trade_time = dt.datetime.strptime(str(trade_time)[:-3], '%H%M%S')
            time_9_30 = dt.datetime.strptime('93000', '%H%M%S')
            time_12_00 = dt.datetime.strptime('120000', '%H%M%S')
            minute = (trade_time - time_9_30).total_seconds() / 60
            if trade_time > time_12_00:
                minute = minute - 1.5 *60
            return minute

        df = self_IO.read_data([self.start_date, self.end_date], alt='/data/user/013600/strong/basic/basic.h5')
        #md_data = self_IO.read_data([self.start_date, self.end_date], columns=['close', 'free_float_shares'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        time_interval_filter = (df['BT_Time']>=self.time_interval[0]) & (df['BT_Time']<=self.time_interval[1])
        strong_type_filter = df['StrongTypes'].apply(lambda x: x in self.strong_type)
        before_day_zt_filter = df['beforeDateZTFactor'].apply(lambda x: x in self.before_day_zt)
        df = df[time_interval_filter & strong_type_filter & before_day_zt_filter]
        df = df.rename(columns = {'BT_Time':'time', 'BT_Price':'price', 'label_T_is_zt':'class',
                                  'label_TN_o2ul':'value'})
        #df['size'] = (md_data['close'] * md_data['free_float_shares']).apply(np.log)
        df['price'] = df['price'].apply(np.log)
        df['time'] = df['time'].apply(lambda x: cal_time_from_open(x))
        df['mixed'] = ((df['value']>0) & (df['class']==1)).apply(lambda x: 1 if x else 0)
        df['month'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y-%m')[2:]))
        df['year'] = list(pd.Series(df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y')))
        self.basic_df = df

        all_factor = pd.read_pickle('/data/user/013600/strong/all_factor/all_factor.pkl')
        all_factor['datelist'] = all_factor['datelist'].apply(lambda x: pd.Timestamp(str(x)))
        all_factor = all_factor.rename(columns={'datelist':'dt', 'stockID':'Ticker'})
        all_factor = all_factor.set_index(['dt', 'Ticker'])
        self.all_factor = pd.DataFrame(index=self.basic_df)
        other_factor = self_IO.read_data([self.start_date, self.end_date], alt='/data/user/013600/strong/all_factor/all_factor_xquant_20160101_20191018_20191118_1534.h5')
        self.all_factor = all_factor
        self.all_factor = self.all_factor.join(other_factor, rsuffix='other')
        self.all_factor = self.all_factor.reindex(self.basic_df.index)

        #freetrun
        self.basic_df['freeturn'] = self.all_factor['freeturn']

    def factor_test(self, factor_df, result_path, factor_corr_test=False):
        if len(factor_df.columns)>1:
            print('factor_df must be only one column')
            raise Exception

        self.factor_name = factor_df.columns[0]
        self.factor_df = pd.DataFrame(index=self.basic_df.index)   #basic_df过滤样本
        self.factor_df['factor'] = factor_df[self.factor_name]
        self.basic_df['factor'] = self.factor_df['factor']

    #    self.factor_df = self.factor_df.dropna(axis=0, subset=['factor'])
    #    self.basic_df = self.basic_df.dropna(axis=0, subset=['factor'])

        self.result_dic['factor_information'] = self.get_factor_information()

        self.result_dic['corr_month'] = self.get_corr_month()
        self.result_dic['corr_sta'] = self.get_corr_sta(self.result_dic['corr_month'])
        print(self.result_dic['corr_sta'])

        self.result_dic['distribution_tot'] = self.factor_df.sort_values(by='factor')
        self.result_dic['distribution_month'] = self.get_distribution_month()
        self.result_dic['distribution_style'] = self.get_distribution_style()
        self.result_dic['corr_style'] = self.get_corr_style()

        self.result_dic['group_tot'] = self.get_group_test_result()
        self.result_dic['group_tot_time_sort'] = self.get_double_group_test_result(['time'])
        self.result_dic['group_by_year'] = self.get_group_test_result_by_year()
        self.result_dic['double_group_sort'] = self.get_double_sort(sort_factor_list=self.style_list)

        self.factor_corr_test = factor_corr_test
        if self.factor_corr_test:
            self.result_dic['factor_corr'] = self.get_corr_with_all_factor()

        now_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        #self.save_pickle(self.result_dic, save_path='%s%s.pkl'%(result_path, self.factor_name))
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

        def generate_plot(df, plot_name, x_label, y_label, plot_type='line', color='#e23e57', rot=0, plot_y0=False, use_index=True, secondary_y=False, fig_width=7.5, fig_height=2):
            plt.close()
            legend_on = True if min(df.shape) > 1 else False
            df_plot = df.plot(kind=plot_type, figsize=(fig_width * 3, fig_height * 3), legend=legend_on, fontsize=20,
                              color=color, rot=rot, use_index=use_index, secondary_y=secondary_y)
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
                if len(cols_list)==2:
                    x = np.arange(len(df[year_list[i]]))
                    plt.bar(x-width/2, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0],color='#1b7fbd')
                    plt.bar(x+width/2, list(df[year_list[i]][cols_list[1]]), width=width, label =cols_list[1], color='#525252')
                    plt.ylim(0, 0.5)
                else:
                    x = np.arange(len(df[year_list[i]]))
                    plt.bar(x, list(df[year_list[i]][cols_list[0]]), width=width, label=cols_list[0], color='#e23e57')
                    plt.ylim(-5, 0)
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
        h_corr_sta = Paragraph('Correlation Statistic', pdf_styles['Heading4'])
        col_type = ['pct2', 'pct2', 'pct2', 'dcm1']
        t_corr_sta = generate_table(result_dic['corr_sta'], col_type, axis=0, reformat_type=True)
        elements = [h_factor_information, t_factor_information, h_corr_sta, t_corr_sta]

        h_monthly_corr = Paragraph('Monthly Corr', pdf_styles['Heading4'])
        p_monthly_corr = generate_plot(result_dic['corr_month'][['class', 'mixed']], plot_name='Monthly Corr - Class&Mixed', x_label='month', y_label='corr of class&mixed', plot_type='bar', color=['#1b7fbd', '#525252'], rot=25)
        elements += [h_monthly_corr, p_monthly_corr]

        h_group_test = Paragraph('Group Test', pdf_styles['Heading4'])
        p_group_test_value = generate_plot(result_dic['group_tot'][['value']], plot_name='Group Test - Value', x_label='Group',
                                           y_label='value', plot_type='bar')
        p_group_test_cm = generate_plot(result_dic['group_tot'][['class', 'mixed']], plot_name='Group Test - Class&Mixed',
                                        x_label='Group', y_label='class&mixed', plot_type='bar', color=['#1b7fbd', '#525252'])
        p_group_test_cm_with_time = generate_plot(self.result_dic['group_tot_time_sort']['time'][['class', 'mixed']], plot_name='Group Test - Class&Mixed - Time Neutralization',
                                                  x_label='Group', y_label='class&mixed', plot_type='bar',color=['#1b7fbd', '#525252'])
        p_group_test_value_year = generate_group_test_year(result_dic['group_by_year'], cols_list=['value'])
        p_group_test_value_cm = generate_group_test_year(result_dic['group_by_year'], cols_list=['class', 'mixed'])

        elements += [h_group_test, p_group_test_value, p_group_test_cm, p_group_test_cm_with_time, p_group_test_value_year, p_group_test_value_cm]

        h_ds = Paragraph('Distribution & Style', pdf_styles['Heading4'])
        p_dis = generate_plot(result_dic['distribution_tot'], plot_name='Distribution', x_label='factor',
                              y_label='value', plot_type='line', color=['#211717'], use_index=False)
        p_styles = generate_plot(result_dic['distribution_style'], plot_name='Style',
                                 x_label='sorted by factor', y_label='style', plot_type='line',
                                 color=['#2f416d', '#14868c'], use_index=False, secondary_y=['price'])
        t_styles = generate_table(result_dic['corr_style'], col_type=['pct2', 'pct2'], axis=0, reformat_type=True)
        p_double_sort = generate_double_sort(result_dic['double_group_sort'])

        h_dis_month = Paragraph('Distribution Each Month', pdf_styles['Heading4'])
        p_dis_month = generate_plot(result_dic['distribution_month'], plot_name='Month Distribution', x_label='factor',
                                    y_label='value', plot_type='box', rot=25, color='#414141')
        elements += [h_ds, p_dis, p_styles, t_styles, p_double_sort, h_dis_month, p_dis_month]

        if self.factor_corr_test:
            h_corr_all = Paragraph('Correlation with Other Factors', pdf_styles['Heading4'])
            t_corr_all = generate_table(result_dic['factor_corr'].iloc[:20], col_type=['dcm2']*20, axis=0, reformat_type=True)
            print(result_dic['factor_corr'].iloc[:3])
            print(result_dic['factor_corr'].loc['freeturn'])
            elements += [h_corr_all, t_corr_all]

        doc = SimpleDocTemplate(save_path, pagesize=letter, topMargin=80, bottomMargin=3)
        doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)

    def save_pickle(self, result_dic, save_path):
        with open(save_path, 'wb') as input:
            pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)

    def get_double_sort(self, sort_factor_list, sort_factor_group_num=5, factor_group_num=10, return_data=False):
        result_dic = {}
        for sort_factor in sort_factor_list:
            data = self.basic_df.copy()
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
                                                       'Test Period': '%d - %d' % (self.start_date, self.end_date),
                                                       'Date Count': len(self.factor_df.unstack()),
                                                       'Sample Count': len(self.factor_df),
                                                       'Nan|Inf Count': len(self.factor_df) - len(
                                                           self.factor_df[self.factor_df['factor'] == self.factor_df['factor']])})
        factor_information[' '] = ['Segment Number', 'Time Interval', 'Strong Type', 'Before Day Zt', 'Style List']
        factor_information['Settings'] = [self.segment_number, str(self.time_interval), str(self.strong_type),
                                          str(self.before_day_zt), str(self.style_list)]
        return factor_information

    def get_corr_with_all_factor(self):
        corr_res = pd.DataFrame()
        corr_res['factor_corr'] = self.all_factor.corrwith(self.factor_df['factor'], method='spearman')
        corr_res['factor_corr_abs'] = corr_res['factor_corr'].abs()
        corr_res = corr_res.sort_values(by='factor_corr_abs', ascending=False)
        return corr_res[['factor_corr']]

#sft = strongFactorTest(start_date, end_date, before_day_zt=[-1,0], style_list=['freeturn', 'time'])
#sft.factor_test(factor_df[[factor_col]], result_path='/data/user/013600/strong/%s/' % (factor_name),  factor_corr_test=True)
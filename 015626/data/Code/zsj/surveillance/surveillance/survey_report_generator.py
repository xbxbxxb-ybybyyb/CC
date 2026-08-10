# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 13:28:29 2018

@author: 012315
"""

import datetime
import pandas as pd
import numpy as np
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
import seaborn as sns
from io import BytesIO
from reportlab.platypus import Image
from multifactor.backtest.utility import pprint
import os

# import warnings
# warnings.simplefilter('error')

plt.style.use('ggplot')
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
PAGE_HEIGHT = defaultPageSize[1];
PAGE_WIDTH = defaultPageSize[0]

fig_width = 7
fig_height = 8
#fig_height = 2.5

def dataframe2str(df, col_type, axis, reformat_type):
    """get dataframe column, return string with format"""
    df = df if axis == 1 else df.T
    df_col = df.columns.tolist()
    index_length = len(df.index.names)
    if index_length>1:
        df_row = [df.index.names[0]] + df.index.get_level_values(0).tolist()
        for i in range(1,index_length):
            data = [df.index.names[0]] + df.index.get_level_values(i).tolist() 
            df_row = np.vstack([df_row,data])
        df_str = df_row       
    else:
        df_row = df.index.tolist()
        df_str = [''] + df_row
    for col, ct in zip(df_col, col_type):
        data = [col] + num2str(df[col].values.tolist(), ct) if reformat_type == True else [col] + df[col].values.tolist()
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


def generate_first_page(canvas, doc):
    title = 'Factor Surveillance Report'
    canvas.saveState()
    canvas.setTitle(title=title)
    PAGE_HEIGHT = defaultPageSize[1]
    PAGE_WIDTH = defaultPageSize[0]
    canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, title)
    canvas.setFont(psfontname='STSong-Light', size=6)
    canvas.restoreState()


def generate_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont(psfontname='STSong-Light', size=6)
    canvas.restoreState()


def generate_table(df, col_type, axis, reformat_type):
    df_str = dataframe2str(df, col_type, axis, reformat_type)
    df_str[0] = [i.encode('utf-8') for i in df_str[0]]
    t = Table(df_str)
    mytable = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                          ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                          ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light')])
    t.setStyle(mytable)
    return t


def generate_plot(df, plot_name, x_label, y_label, plot_type='line',c_width=None,c_height=None):
    plt.close()
    legend_on = True if min(df.shape) > 1 else False
    if plot_type=='stack_bar':
        stack=True
        plot_type='bar'
    else:
        stack=False
    if c_width is not None and c_height is not None:
        df_plot = df.plot(kind=plot_type, stacked=stack, figsize=(c_width*3, c_height*3), legend=legend_on, fontsize=14)
    else:
        df_plot = df.plot(kind=plot_type, stacked=stack, figsize=(fig_width*3, fig_height*3), legend=legend_on, fontsize=14)
    df_plot.set_title(plot_name, fontsize=20)
    df_plot.set_xlabel(x_label, fontsize=16)
    df_plot.set_ylabel(y_label, fontsize=16)
    plt.tight_layout()   
    if plot_type=='stack_bar':
        plt.legend(bbox_to_anchor=(0.5,0),ncol=len(df_plot.columns))
        plt.ylim([0,1])
    imgdata = BytesIO()
    df_plot.figure.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    if c_width is not None and c_height is not None:
        return Image(imgdata, width=c_width * inch, height=c_height * inch)
    else:      
        return Image(imgdata, width=fig_width * inch, height=1.1*fig_height * inch)

def generate_heatmap_plot(correlation_matrix,plot_name,c_width=None,c_height=None):
    plt.close()
    plt.ioff()
    #sns.set(style="white")
    mask = np.zeros_like(correlation_matrix, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    f, ax = plt.subplots(figsize=(11, 9))
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    if c_width is not None and c_height is not None:
        plt.subplots(figsize=(c_width*3, c_height*3))
    else:
        plt.subplots(figsize=(fig_width*3, fig_height*3))
    df_plot = sns.heatmap(correlation_matrix,mask=mask,cmap=cmap)
    plt.title(plot_name,fontsize=20)
    imgdata = BytesIO()
    df_plot.figure.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    if c_width is not None and c_height is not None:
        return Image(imgdata, width=c_width * inch, height=c_height * inch)
    else:      
        return Image(imgdata, width=fig_width * inch, height=1.1*fig_height * inch)
    


#ret_dist_pct.plot(kind='bar',stacked=True,figsize=[11,3])
#plt.legend(bbox_to_anchor=(1.005,0.5), loc="center left")
    

def generate_bar_line_plot(df, title, bar_column, line_column):
    plt.figure(figsize=(fig_width*3, fig_height*3))
    plt.subplot(211)
    plt.bar(np.arange(len(df)), df[bar_column])
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xticks([])
    plt.subplot(212)
    plt.plot(df[line_column])
    plt.title(line_column)
    plt.xlabel('')
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=fig_width * inch, height=fig_height * inch)


def generate_segment_ret_year(df, col_name='Return(Ann.)'):
    df = df[col_name]
    df = df.rename(index={'Benchmark': 'Index'})
    year_list = list(set(df.index.get_level_values(0)))
    year_list.sort(reverse=True)
    year_num = len(year_list)
    plt_rows = int(np.ceil(year_num / 2))
    height_each_row = 1.7#5
    height_calc = plt_rows * height_each_row
    fig_height = 20 / (7 / height_calc)
    plt.figure(figsize=(20, fig_height))
    for i in range(year_num):
        plt.subplot(plt_rows, 2, i + 1)
        sliced = df.loc[year_list[i]]
        sliced.plot(kind='bar', fontsize=12)
        plt.title(col_name + ' - ' + str(year_list[i]), fontsize=15, fontweight='bold')
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    #return Image(imgdata, width=fig_width * inch, height=height_calc * inch)
    return generate_image_helper(imgdata, fig_width,height_calc,inch)

def generate_image_helper(imgdata,fig_width,fig_height,inch,max_width=456,max_height=664):
    return Image(imgdata, width=min(fig_width*inch,max_width), height=min(fig_height*inch,max_height))

#top_num = 20
def generate_subplot_by_column(df,prefix='',top_num=None,plot_type='barh'):
    col_list = df.columns
    col_num = len(col_list)
    plt_rows = int(np.ceil(col_num / 2))
    height_each_row = 1.7#5
    height_calc = plt_rows * height_each_row
    fig_height = 20 / (7 / height_calc)
    plt.figure(figsize=(20, fig_height))
    for i in range(col_num):
        plt.subplot(plt_rows, 2, i + 1)
        if top_num is not None:
            top_use = min(top_num,len(df[col_list[i]].dropna()))
            sliced = df[col_list[i]].sort_values().iloc[-1*top_use:]
        else:    
            sliced = df[col_list[i]]
        sliced.plot(kind=plot_type, fontsize=12)
        plt.title(prefix + ' - ' + str(col_list[i]), fontsize=15, fontweight='bold')
    plt.tight_layout()
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=fig_width * inch, height=height_calc * inch)

def generate_plot_with_secondary(df1, df2, plot_name, x_label, y_label1, y_label2, plot_type='line'):
    fig, ax = plt.subplots()
    df1.index.name = ''
    df2.index.name = ''
    df1_plot = df1.plot(ax=ax, kind=plot_type, figsize=(fig_width*3, fig_height*3), fontsize=14)
    df1_plot.set_title(plot_name, fontsize=20)
    ax.set_xlabel(x_label, fontsize=16)
    df1_plot.set_ylabel(y_label1, fontsize=16)
    df2_plot = df2.plot(ax=ax, kind=plot_type, figsize=(fig_width*3, fig_height*3), fontsize=14, secondary_y=True, style='--')
    df2_plot.set_ylabel(y_label2, fontsize=16)
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=fig_width * inch, height=fig_height * inch)


#top_num = 20

def generate_subplot_mi(df_mi,prefix='',plot_type='barh',sort=True):
    col_list = list(set(df_mi.index.get_level_values(0)))
    col_list.sort(reverse=True)
    col_num = len(col_list)
    plt_rows = int(np.ceil(col_num / 2))
    height_each_row = 1.5#5
    height_calc = plt_rows * height_each_row
    fig_height = 20 / (7 / height_calc)
    plt.figure(figsize=(20, fig_height))
    for i in range(col_num):
        plt.subplot(plt_rows, 2, i + 1)
        sliced = df_mi.xs(col_list[i],level=0)[df_mi.columns[0]]
        if sort:
            sliced  = sliced.sort_values(ascending=True)
        sliced.plot(kind=plot_type, fontsize=12)
        plt.title(prefix + ' - ' + str(col_list[i]), fontsize=15, fontweight='bold')
        plt.ylabel('')
    plt.tight_layout()
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg', dpi=100)
    imgdata.seek(0)
    plt.close()
    #return Image(imgdata, width=fig_width * inch, height=height_calc * inch)
    return generate_image_helper(imgdata, fig_width,height_calc,inch)




def generate_pdf(excel_name, output_folder):
    show_max_trail = 240
    show_max_trail1 = 60
    top_line_num = 10
    top_num = 20
    pprint('Retrieving basic numbers from Excel')
    with pd.ExcelFile(excel_name) as xls_handle:
        summary = pd.read_excel(xls_handle, sheetname='summary', index_col=0)

        max_q_stats = pd.read_excel(xls_handle, sheetname='max_q_stats')
        ic_stats = pd.read_excel(xls_handle, sheetname='ic_stats')
        #max_q_stats_by_year = pd.read_excel(xls_handle, sheetname='max_q_stats_by_year', index_col=[0, 1]).drop_duplicates()  #.fillna('')
        #ic_stats_by_year = pd.read_excel(xls_handle, sheetname='ic_stats_by_year', index_col=[0, 1]).drop_duplicates()  # .fillna('')
        max_q_df = pd.read_excel(xls_handle, sheetname='max_q_df', index_col=0)
        ic_ts_df = pd.read_excel(xls_handle, sheetname='ic_ts_df', index_col=0)
        max_q_summary = pd.read_excel(xls_handle, sheetname='max_q_summary', index_col=0)
        ic_summary = pd.read_excel(xls_handle, sheetname='ic_summary', index_col=0)
        correlation_stats = pd.read_excel(xls_handle, sheetname='correlation_stats', index_col=0)
        ic_corr = pd.read_excel(xls_handle, sheetname='ic_corr', index_col=0)
        max_q_corr = pd.read_excel(xls_handle, sheetname='max_q_corr', index_col=0)
        positive_excess_ret_roll = pd.read_excel(xls_handle, sheetname='positive_excess_ret_roll', index_col=0)
        ic_dist_pct = pd.read_excel(xls_handle, sheetname='ic_dist_pct', index_col=0)
        max_q_ret_dist_pct = pd.read_excel(xls_handle, sheetname='max_q_ret_dist_pct', index_col=0)
        ic_per_year = pd.read_excel(xls_handle, sheetname='ic_per_year', index_col=[0,1])
        #ic_per_month = pd.read_excel(xls_handle, sheetname='ic_per_month', index_col=[0,1])
        max_q_per_year = pd.read_excel(xls_handle, sheetname='max_q_per_year', index_col=[0,1])
        #max_q_per_month = pd.read_excel(xls_handle, sheetname='max_q_per_month', index_col=[0,1])
        trail_ic = pd.read_excel(xls_handle, sheetname='trail_ic', index_col=[0])
        trail_max_q = pd.read_excel(xls_handle, sheetname='trail_max_q', index_col=[0])
        max_q_stats_by_year_top = pd.read_excel(xls_handle, sheetname='max_q_stats_by_year_top', index_col=[0,1])
        ic_stats = pd.read_excel(xls_handle, sheetname='ic_stats', index_col=[0])

                          
    has_data = np.isfinite(max_q_df).sum(axis=1)>0
    for i in range(1,len(has_data)):
        if has_data.iloc[-i]:
            break
    holding_period = i-1

    
    top_trail_max_q1 = trail_max_q['last %d days'%(show_max_trail1)].sort_values(ascending=False).iloc[:top_line_num]
    top_trail_max_q_cumsum1 = max_q_df[top_trail_max_q1.index].iloc[-holding_period-show_max_trail1:-holding_period].fillna(0).cumsum()

    top_trail_ic1 = trail_ic['last %d days'%(show_max_trail1)].sort_values(ascending=False).iloc[:top_line_num]
    top_trail_ic_cumsum1 = ic_ts_df[top_trail_ic1.index].iloc[-holding_period-show_max_trail1:-holding_period].fillna(0).cumsum()

    top_trail_max_q = trail_max_q['last %d days'%(show_max_trail)].sort_values(ascending=False).iloc[:top_line_num]
    top_trail_max_q_cumsum = max_q_df[top_trail_max_q.index].iloc[-holding_period-show_max_trail:-holding_period].fillna(0).cumsum()

    top_trail_ic = trail_ic['last %d days'%(show_max_trail)].sort_values(ascending=False).iloc[:top_line_num]
    top_trail_ic_cumsum = ic_ts_df[top_trail_ic.index].iloc[-holding_period-show_max_trail:-holding_period].fillna(0).cumsum()

    measure_summary = pd.concat([max_q_summary,ic_summary],axis=1)
    measure_summary = measure_summary.iloc[1:,[0,2,3,5]]
    measure_summary.columns = ['Excess Return','Info Ratio','IC','ICIR']

    correlation_stats = correlation_stats.iloc[1:,:]
    corr_mean = pd.concat([ic_corr.mean(),max_q_corr.mean()],axis=1)
    corr_mean.columns = ['IC','Excess Return']

    pprint('Generating tables')

    col_type = ['str1','str1','dcm0', 'dcm3', 'dcm3','pct2','dcm2']
    t_summary = generate_table(summary, col_type, axis=0, reformat_type=True)

    col_type = ['pct2','dcm2', 'dcm3','dcm2']
    t_measure_summary = generate_table(measure_summary, col_type, axis=1, reformat_type=True)

    col_type = ['pct2','pct2']
    t_correlation_stats = generate_table(correlation_stats, col_type, axis=1, reformat_type=True)

    col_type = ['dcm4', 'dcm4', 'dcm2']
    t_ic_stats = generate_table(ic_stats, col_type, axis=1, reformat_type=True)
    
    col_type = ['pct2', 'pct2', 'dcm2']
    t_max_q_stats = generate_table(max_q_stats, col_type, axis=1, reformat_type=True)
    

    col_type = ['pct2', 'pct2', 'dcm2']
    t_max_q_stats_by_year_top = generate_table(max_q_stats_by_year_top, col_type, axis=1, reformat_type=True)

    pprint('Generating graphs')
    #g_max_q_stats_excess_ret = generate_plot(max_q_stats[['excess_ret']].sort_values('excess_ret').iloc[-1*max_num:], plot_name='Excess Return - All History',x_label='Excess Return (Ann.)', y_label='', plot_type='barh')
    #g_t_ic_stats = generate_plot(ic_stats[['ic_mean']].sort_values('ic_mean').iloc[-1*max_num:], plot_name='IC - All History',x_label='IC', y_label='', plot_type='barh')

    g_trail_max_q = generate_subplot_by_column(trail_max_q,prefix='Excess Return',top_num=top_num)
    g_trail_ic = generate_subplot_by_column(trail_ic,prefix='IC',top_num=top_num)

    g_top_trail_max_q_cumsum = generate_plot(top_trail_max_q_cumsum, 'Cum Excess Return - Top %d Factors (last %d days)'%(top_line_num,show_max_trail), 
                                             x_label='', y_label='CumRet', plot_type='line',c_width=7,c_height=2)    
    g_top_trail_ic_cumsum = generate_plot(top_trail_ic_cumsum, 'Cum IC - Top %d Factors (last %d days)'%(top_line_num,show_max_trail), x_label='', 
                                          y_label='Cum IC', plot_type='line',c_width=7,c_height=2)    

    g_top_trail_max_q_cumsum1 = generate_plot(top_trail_max_q_cumsum1, 'Cum Excess Return - Top %d Factors (last %d days)'%(top_line_num,show_max_trail1), 
                                             x_label='', y_label='CumRet', plot_type='line',c_width=7,c_height=2)    
    g_top_trail_ic_cumsum1 = generate_plot(top_trail_ic_cumsum1, 'Cum IC - Top %d Factors (last %d days)'%(top_line_num,show_max_trail1), x_label='', 
                                          y_label='Cum IC', plot_type='line',c_width=7,c_height=2)    

    g_positive_excess_ret_roll = generate_plot(positive_excess_ret_roll, 'Number of Factors with Positive Excess Return', x_label='', 
                                          y_label='Number of Factors', plot_type='bar',c_width=7,c_height=2)    
    
    g_max_q_per_year = generate_subplot_mi(max_q_per_year,prefix='Excess Return',plot_type='barh',sort=True)
    g_ic_per_year = generate_subplot_mi(ic_per_year,prefix='IC',plot_type='barh',sort=True)


    g_ret_dist_pct = generate_plot(max_q_ret_dist_pct, 'Excess Return Distribution', x_label='', 
                                   y_label='Excess Return(monthly)', plot_type='stack_bar',c_width=7,c_height=2)

    g_ic_dist_pct = generate_plot(ic_dist_pct, 'IC Distribution', x_label='', 
                                   y_label='IC(monthly)', plot_type='stack_bar',c_width=7,c_height=2)    
    
    g_corr_mean = generate_plot(corr_mean, 'Factor Correlation\n(average pairwise correlation with other factors)', x_label='correlation', 
                                   y_label='density', plot_type='kde',c_width=7,c_height=1.5)
    
    g_ic_corr = generate_heatmap_plot(ic_corr,'IC Correlation',c_width=7,c_height=7)
    
    pprint('Generating headers')
    styles = getSampleStyleSheet()
    heading_size = styles['Heading4']
    h_sum = Paragraph('Factor Surveillance Report', heading_size)
    h_max_q_stats = Paragraph("Excess Return - All History", heading_size)
    h_ic_stats = Paragraph("IC - All History", heading_size)

    h_distribution = Paragraph("Factor Distribution ", heading_size)
    
    h_top_trail = Paragraph("Performance Tracker - last %d days"%show_max_trail, heading_size)
    h_top_trail1 = Paragraph("Performance Tracker - last %d days"%show_max_trail1, heading_size)

    h_trail_max_q = Paragraph("Trailing Excess Return ", heading_size)
    h_trail_ic = Paragraph("Trailing IC", heading_size)
    h_max_q_stats_by_year_top = Paragraph("Excess Return Top Performer by Year", heading_size)
    h_max_q_per_year = Paragraph("Excess Return by Year", heading_size)
    h_ic_per_year = Paragraph("IC by Year", heading_size)
    
    h_measure_summary = Paragraph("Factor Summary - Excess Return & IC", heading_size)
    h_correlation_stats = Paragraph("Factor Correlation - Excess Return & IC", heading_size)
    h_corr_mean = Paragraph("Factor Correlation", heading_size)

    now = datetime.datetime.today()
    file_date = now.strftime("%Y%m%d_%H%M%S")
    pdf_report_date = 'Test Date:  ' + now.strftime("%Y-%m-%d %H:%M:%S")
    report_name = 'Factor_Surveillance_Report_' + str(file_date)
    h_date = Paragraph(pdf_report_date, styles['Normal'])
    plt.ioff()
    
    pprint('Generating pdf')
    pdf_path = os.path.join(output_folder, report_name+'.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.8 * inch,
                            bottomMargin=0.8 * inch)
    elements = []
    elements.append(h_date)
    elements.append(h_sum)
    
    elements.append(t_summary)
    
    elements.append(h_measure_summary)
    elements.append(t_measure_summary)
    elements.append(h_correlation_stats)
    elements.append(t_correlation_stats)    
    elements.append(PageBreak())
    
    elements.append(h_distribution)
    elements.append(g_positive_excess_ret_roll)
    elements.append(g_ret_dist_pct)
    elements.append(g_ic_dist_pct)
    elements.append(PageBreak())

    elements.append(h_top_trail1)
    elements.append(g_top_trail_max_q_cumsum1)
    elements.append(g_top_trail_ic_cumsum1)
    
    elements.append(h_top_trail)
    elements.append(g_top_trail_max_q_cumsum)
    elements.append(g_top_trail_ic_cumsum)
    elements.append(PageBreak())

    elements.append(h_corr_mean)   
    elements.append(g_corr_mean)   
    elements.append(g_ic_corr)    
    elements.append(PageBreak())
    
    elements.append(h_trail_max_q)
    elements.append(g_trail_max_q)
    elements.append(PageBreak())
#        
    elements.append(h_trail_ic)
    elements.append(g_trail_ic)
    elements.append(PageBreak())
    
    elements.append(h_max_q_per_year)
    elements.append(g_max_q_per_year)
    elements.append(PageBreak())

    elements.append(h_ic_per_year)
    elements.append(g_ic_per_year)
    elements.append(PageBreak())
#
    elements.append(h_max_q_stats_by_year_top)
    elements.append(t_max_q_stats_by_year_top)
    elements.append(PageBreak())
    
    elements.append(h_max_q_stats)
    elements.append(t_max_q_stats)
    elements.append(PageBreak())

    elements.append(h_ic_stats)
    elements.append(t_ic_stats)
    elements.append(PageBreak())
    
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)
    pprint('Report generation complete')
    return

#excel_name = r'A:\zhisj\public\factor_status\star_analyst\factor_summary.xlsx'
#output_folder = r'A:\zhisj\public\factor_status\star_analyst'
#generate_pdf(excel_name, output_folder)


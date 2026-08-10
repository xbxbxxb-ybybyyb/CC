# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 11:22:29 2017

@author: 012315
"""
import datetime
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Spacer,Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak
from reportlab.rl_config import defaultPageSize
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from reportlab.platypus import Image
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

plt.style.use('ggplot')
#sns.set_style("whitegrid") 
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0] 


from matplotlib import pyplot as plt
plt.style.use('ggplot')
########################################################################

def dataframe2str(df,col_type,axis,reformat_type):
    "get dataframe column, return string with format"
    df = df if axis == 1 else df.T
    df_col = df.columns.tolist()
    df_row = df.index.tolist()
    df_str = ['']+df_row
    for col,ct in zip(df_col,col_type):
        data = [col] + num2str(df[col].values.tolist(),ct) if reformat_type==True else [col] + df[col].values.tolist()
        df_str = np.vstack([df_str,data])
    df_str = df_str.T.tolist() if axis==1 else df_str.tolist()   
    return df_str
    
def num2str(data,data_type):
    """take number and change format, return list of string"""
    round_num = int(data_type[-1])  
    number_type = data_type[:-1]
    if number_type =='pct':
        data = [str(round(i*100,round_num))+'%' for i in data]
    elif number_type == 'dcm':
        data = [str(round(i,round_num)) for i in data]
    return data 

def myFirstPage(canvas, doc):
    Title = 'Factor Backtest Report'
    canvas.saveState()
    canvas.setTitle(title='Factor Backtest Report')
    #canvas.setFont('STSong-Light',12)
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0] 
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108,Title)
    canvas.setFont(psfontname='STSong-Light',size=6)
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont(psfontname='STSong-Light',size=6)
    canvas.restoreState()


def GenerateTable(df,col_type,axis,reformat_type):
    df_str = dataframe2str(df,col_type,axis,reformat_type)
    df_str[0] = [i.encode('utf-8') for i in df_str[0]]
    t = Table(df_str)
    mytable = TableStyle([('BACKGROUND',(0,0),(-1,0),colors.white),
                          ('TEXTCOLOR',(0,0),(-1,0),colors.black),
                          ('FONTNAME',(0,0),(-1,-1),'STSong-Light')])
    t.setStyle(mytable)
    return t

def generate_plot(df,plot_name,x_label,y_label,plot_type='line'):
    plt.close()
    legend_on = True if min(df.shape)>1 else False
    df_plot = df.plot(kind=plot_type,figsize=(18,7.5),legend = legend_on,fontsize=14)
    df_plot.set_title(plot_name,fontsize=20)
    df_plot.set_xlabel(x_label,fontsize=16)
    df_plot.set_ylabel(y_label,fontsize=16)
    imgdata = BytesIO()
    df_plot.figure.savefig(imgdata, format='jpg',dpi=100)
    imgdata.seek(0)
    plt.close() # This is the key!!!
    return Image(imgdata,width=6*inch, height=2.5*inch)



########################################################################



def generate_bar_line_plot(df,title,bar_column,line_column):
    plt.figure(figsize=(18,7.5))
    plt.subplot(211)
    plt.bar(np.arange(len(df)),df[bar_column])
    plt.title(title,fontsize=14, fontweight='bold')
    plt.xticks([])
    plt.subplot(212)
    plt.plot(df[line_column])
    plt.title(line_column)
    plt.xlabel('Date')
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg',dpi=100)
    imgdata.seek(0)
    plt.close() # This is the key!!!
    return Image(imgdata,width=6*inch, height=2.5*inch)

#df = seg_ret_performance.iloc[:,:6]
def generate_performance_report(df):    
    col_name = df.columns
    idx_name = df.index.tolist()
    idx_name[idx_name.index('Benchmark')] = 'Index'
    df.index = idx_name
    plt.figure(figsize=(18,12))
    for i in range(len(col_name)):
        plt.subplot(2,3,i+1)
        df.iloc[:,i].plot(kind='bar',fontsize=12)
        plt.title(col_name[i],fontsize=15, fontweight='bold')
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg',dpi=100)
    imgdata.seek(0)
    plt.close() # This is the key!!!
    return Image(imgdata,width=6*inch, height=4*inch)

#df = seg_return_30_stat_year
def generate_segment_ret_year(df,col_name='Return(Ann.)'):    
    df = df[col_name]
    #col_name = df.columns
    #idx_name = list(set(df.index.get_level_values(1)))
    df = df.rename(index={'Benchmark': 'Index'})
    year_list = list(set(df.index.get_level_values(0)))
    year_list.sort(reverse=True)
    year_num = len(year_list)
    plt_rows = int(np.ceil(year_num/2))
    height_each_row = 1.6
    height_calc = plt_rows*height_each_row
    fig_height = 20/(7/height_calc)
    plt.figure(figsize=(20,fig_height))
    for i in range(year_num):
        plt.subplot(plt_rows,2,i+1)
        df.loc[year_list[i]].plot(kind='bar',fontsize=12)
        plt.title(col_name+' - '+str(year_list[i]),fontsize=15, fontweight='bold')
    imgdata = BytesIO()
    plt.savefig(imgdata, format='jpg',dpi=100)
    imgdata.seek(0)
    plt.close() # This is the key!!!
    return Image(imgdata,width=7*inch, height=height_calc*inch)



def half_life_raw(A):
    under_half = A.abs()<(A.abs().max()/2)
    half_position = under_half.idxmax()
    return half_position

#excel_name = 'S:\\Quant\\backtest\\backtest_output\\zsj_pv\\minute\\\pm_comb_neu_ind_size\\FactorBacktest_pm_comb_neu_ind_size.xlsx'

def GeneratePdf(excel_name,factor_name,output_folder,easy_test=False):
    print ('-'*5 + '   Generating Backtest Report   '+'-'*5)

    sum_df = pd.read_excel(excel_name,sheetname='因子信息')
    fac_stat = pd.read_excel(excel_name,sheetname='因子原始统计')
    seg_ret_performance = pd.read_excel(excel_name,sheetname='分层测试_组合表现')
    seg_ret_30_performance = pd.read_excel(excel_name,sheetname='分层测试_30组合表现')
    seg_return_30_stat_year = pd.read_excel(excel_name,sheetname='分层30组合年度',index_col=[0,1]).fillna('')
    seg_ret_perf_year = pd.read_excel(excel_name,sheetname='分层测试_组合年度',index_col=[0,1]).fillna('')
    seg_ret = pd.read_excel(excel_name,sheetname='分层测试_日收益率',index_col=0)

    Alpha_cumsum = pd.read_excel(excel_name,sheetname='因子Alpha',index_col=0)
    #turnover =  pd.read_excel(excel_name,sheetname='分层测试_换手率')
    factor_auto_correlation = pd.read_excel(excel_name,sheetname='因子自相关性',index_col=0)
    IC_combined =  pd.read_excel(excel_name,sheetname='因子IC序列',index_col=0)
    IC_combined_stats = pd.read_excel(excel_name,sheetname='因子IC序列统计')
    factor_ts = pd.read_excel(excel_name,sheetname='因子完整度',index_col=0)
    IC_decay =  pd.read_excel(excel_name,sheetname='因子IC有效期')
    if easy_test == False:
        fac_corr = pd.read_excel(excel_name,sheetname='因子共线性')
        fac_TIC = pd.read_excel(excel_name,sheetname='T值与IC')
        fac_TIC_Test =  pd.read_excel(excel_name,sheetname='T值与IC检验')        
        IC_ts = pd.DataFrame(fac_TIC['IC'])
        IC_ts['Avg 30 Period'] = fac_TIC['IC'].rolling(window=30).mean()
        Tstat_ts =  pd.DataFrame(fac_TIC['T-stat'])
        Tstat_ts['Avg 30 Period'] = fac_TIC['T-stat'].rolling(window=30).mean()
    
    IC_halflife = half_life_raw(IC_decay)
    IC_combined_cumsum  = IC_combined.cumsum()
    seg_ret_30_annret = seg_ret_30_performance['Return(Ann.)']
    fac_stat.columns = ['Basic Statistics']
    factor_auto_correlation_rolling = factor_auto_correlation.rolling(window=20).mean()
    #turnover['Q1_Avg5']  = turnover['Q1'].rolling(window=5).mean()
    #turnover['Corr_Avg5']  = turnover['Correlation'].rolling(window=5).mean()
    #turnover = turnover[['Q1_Avg5','Corr_Avg5']]#.iloc[:,[0,-2,-1]]
    seg_cumret = (seg_ret.fillna(0)+1).cumprod()

    seg_ret_year = seg_ret_perf_year['Return(Ann.)'].unstack()
    seg_num = len(seg_ret_year.columns)-2
    col_name=seg_ret_year.columns.tolist()
    spec_col = [col for col in col_name if col.find('-')>0]
    col_name_order = ['Q'+str(i+1) for i in range(seg_num)] + spec_col + ['Benchmark']        
    seg_ret_year = seg_ret_year[col_name_order]
    seg_sharpe_year = (seg_ret_perf_year['Sharpe Ratio'].unstack())[col_name_order]
    seg_sharpe_year = seg_sharpe_year.replace(to_replace='',value=np.nan)
    long_short_ret = (seg_ret.fillna(0)+1).groupby(seg_ret.index.year).cumprod()[spec_col]
    year_num = long_short_ret.groupby(long_short_ret.index.year).count()
    year_list = year_num.index.tolist()
    max_day = int(year_num.max())
    return_by_year = pd.DataFrame(columns=year_list,index=[i for i in range(max_day)])
    for year in year_list:
        return_by_year[year] = [i[0] for i in long_short_ret.loc[str(year)].values.tolist()]+[np.nan]*(max_day-int(year_num.loc[year]))
    
    """table"""
    col_type = ['str1']*len(sum_df) 
    t_sum =  GenerateTable(sum_df,col_type,axis=0,reformat_type=False)
    col_type = ['dcm2','dcm2','pct2','dcm3','dcm3','dcm2','dcm2']
    t_fac_stat =  GenerateTable(fac_stat.T,col_type,axis=1,reformat_type=True)    
    col_type = ['pct2','pct2','dcm2','pct2','pct2','dcm2','pct2']
    t_seg_ret = GenerateTable(seg_ret_performance,col_type,axis=1,reformat_type=True)
    col_type = ['dcm5']*3
    t_IC_combined_stats= GenerateTable(IC_combined_stats,col_type,axis=0,reformat_type=True)
    
    if easy_test == False:
        col_type =['dcm3','dcm3','dcm3','dcm3','pct2','dcm2','pct2','dcm2','pct2','dcm2','dcm2','dcm2','dcm2']                 
        t_fac_TIC_Test = GenerateTable(fac_TIC_Test,col_type,axis=0,reformat_type=True)
        col_type = ['pct2']*9
        t_fac_corr = GenerateTable(fac_corr,col_type,axis=0,reformat_type=True)    
    
    """graph"""
    g_seg_ret_performance = generate_performance_report(seg_ret_performance.iloc[:,:6])
    g_seg_cumret = generate_plot(seg_cumret,plot_name='Quintile Return',x_label='Day',y_label='Cummulative Return')
    g_IC_decay = generate_plot(IC_decay,plot_name='IC Decay \n Half Life:'+str(IC_halflife.values[0])+' days',x_label='Days after factor',y_label='IC')
    g_factor_auto_correlation_rolling = generate_plot(factor_auto_correlation_rolling,plot_name='Factor Auto Correlation',x_label='Date',y_label='Correlation')
    g_return_by_year = generate_plot(return_by_year,plot_name=spec_col[0]+' Return by Year',x_label='day in year',y_label='Cummulative Return')
    g_seg_ret_year = generate_plot(seg_ret_year,plot_name='Total Return',x_label='Year',y_label='Return (Ann.)',plot_type='bar')
    g_seg_sharpe_year = generate_plot(seg_sharpe_year,plot_name='Sharpe Ratio',x_label='Year',y_label='Sharpe Ratio',plot_type='bar')
    g_Alpha_cumsum = generate_plot(Alpha_cumsum,plot_name='Factor Alpha (IC*Dispersion)',x_label='Day',y_label='Cum Alpha')
    g_seg_ret_30_annret = generate_plot(seg_ret_30_annret,plot_name='Segment Return - All History',x_label='Quintile',y_label='Return (Ann.)',plot_type='bar')
    g_IC_combined_cumsum = generate_plot(IC_combined_cumsum,plot_name='Cumulative IC Comparison',x_label='Time',y_label='Cum IC')
    g_factor_ts = generate_plot(factor_ts,plot_name='Stock Count with Factor',x_label='Time',y_label='Number of Stocks')
    g_seg_return_30_stat_year = generate_segment_ret_year(seg_return_30_stat_year,col_name='Return(Ann.)')
    
    
    if easy_test == False:
        Tstat_ts['Avg 30 Period'] = Tstat_ts['Avg 30 Period'].fillna(0)
        IC_ts['Avg 30 Period'] = IC_ts['Avg 30 Period'].fillna(0)
        g_Tstat = generate_bar_line_plot(df=Tstat_ts,title='T-Statistics',bar_column='T-stat',line_column='Avg 30 Period')
        g_IC = generate_bar_line_plot(df=IC_ts,title='IC',bar_column='IC',line_column='Avg 30 Period')
        
        
        
    """Note"""
    styles = getSampleStyleSheet()
    heading_size = styles['Heading4']
    h_sum = Paragraph('Factor Information',heading_size)
    h_fac_stat = Paragraph('Factor Distribution',heading_size)
    h_seg_ret = Paragraph("Quintile Return Performance",heading_size)
    h_return_by_year = Paragraph("Long Short Return",heading_size)
    h_seg_year = Paragraph("Performance by Year",heading_size)
    h_seg_cumret = Paragraph("Quintile Return",heading_size)
    h_IC_decay = Paragraph("IC Decay",heading_size)
    #h_turnover = Paragraph("Portfolio Turnover",heading_size)
    h_factor_auto_correlation_rolling = Paragraph("Factor Auto Correlation",heading_size)
    h_Alpha_cumsum = Paragraph("Alpha",heading_size)
    h_seg_ret_30_annret = Paragraph("30 Segment",heading_size)
    h_seg_ret_30_year = Paragraph("Segment Return by Year",heading_size)
    h_IC_combined_cumsum = Paragraph("IC Comparison",heading_size)
    h_factor_ts = Paragraph("Stock Count",heading_size)
    
    now=datetime.datetime.today()
    file_date=now.strftime("%Y%m%d_%H%M%S")    
    pdf_report_date='Test Date:  ' + now.strftime("%Y-%m-%d %H:%M:%S")   
    report_name = 'FactorBacktes_'+str(factor_name)+'_'+str(file_date)     
    #h_title = Paragraph("Factor Backtest Report",styles['Normal'])
    h_date = Paragraph(pdf_report_date,styles['Normal'])
    plt.ioff()
    
    if easy_test == False:
        h_fac_TIC_Test = Paragraph("T-Stats & IC Test",heading_size)
        h_fac_corr = Paragraph("Factor Correlation with Style Factor",heading_size)
        h_Tstat = Paragraph("T-Statistics by Time",heading_size)
        h_IC = Paragraph("IC by Time",heading_size)
    

    doc = SimpleDocTemplate(output_folder+report_name+".pdf", pagesize=letter)
    elements = []
    #elements.append(h_title)
    elements.append(h_date)
    elements.append(h_sum)
    elements.append(t_sum)
    
    
    elements.append(h_IC_combined_cumsum)
    elements.append(t_IC_combined_stats)
    elements.append(g_IC_combined_cumsum)
    
    elements.append(h_fac_stat)
    elements.append(t_fac_stat) 
    elements.append(PageBreak())  
            
    elements.append(h_Alpha_cumsum)
    elements.append(g_Alpha_cumsum)
    elements.append(h_seg_ret_30_annret)
    elements.append(g_seg_ret_30_annret)
    elements.append(PageBreak()) 
    
    elements.append(h_seg_ret_30_year)
    elements.append(g_seg_return_30_stat_year)
    elements.append(PageBreak()) 
    
    elements.append(h_seg_year)
    elements.append(g_seg_ret_year)
    
    elements.append(h_seg_ret)
    #elements.append(t_seg_ret)
    elements.append(g_seg_ret_performance)
    elements.append(PageBreak()) 
    
    elements.append(h_seg_cumret)
    elements.append(g_seg_cumret)
    elements.append(h_return_by_year)
    elements.append(g_return_by_year)
    elements.append(g_seg_sharpe_year)
    elements.append(PageBreak()) 
    
    #elements.append(h_turnover)
    #elements.append(g_turnover)
    elements.append(h_factor_ts)
    elements.append(g_factor_ts) 
    elements.append(h_factor_auto_correlation_rolling)
    elements.append(g_factor_auto_correlation_rolling)
    
    elements.append(h_IC_decay)
    elements.append(g_IC_decay)
    
    if easy_test == False:
        elements.append(h_fac_TIC_Test)
        elements.append(t_fac_TIC_Test)
        elements.append(h_IC)
        elements.append(g_IC)
        elements.append(h_Tstat)
        elements.append(g_Tstat)
        elements.append(h_fac_corr)
        elements.append(t_fac_corr)
        
        
    doc.build(elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    return 





def generate_pdf(excel_name,output_folder=None,easy_test=False):
    output_folder = excel_name[:excel_name.rfind('\\')+1] if output_folder is None else output_folder
    factor_name = excel_name[excel_name.find('FactorBacktest_')+15:excel_name.rfind('.xlsx')]
    print ('Generating PDF')

    sum_df = pd.read_excel(excel_name,sheetname='summary_info')
    fac_stat = pd.read_excel(excel_name,sheetname='distribution')
    seg_ret_30_performance = pd.read_excel(excel_name,sheetname='seg_return_30_stat')
    seg_return_30_stat_year = pd.read_excel(excel_name,sheetname='seg_return_30_stat_year',index_col=[0,1]).fillna('')
    #Alpha_cumsum = pd.read_excel(excel_name,sheetname='Alpha_cumsum',index_col=0)
    factor_auto_correlation = pd.read_excel(excel_name,sheetname='factor_auto_correlation',index_col=0)
    IC_combined =  pd.read_excel(excel_name,sheetname='IC_ts',index_col=0)
    IC_combined_stats = pd.read_excel(excel_name,sheetname='IC_ts_stats')
    factor_ts = pd.read_excel(excel_name,sheetname='stock_count',index_col=0)
    IC_decay =  pd.read_excel(excel_name,sheetname='IC_Decay')

#    if easy_test == False:
#        fac_corr = pd.read_excel(excel_name,sheetname='factor_corr',index_col=0)

    IC_combined_cumsum  = IC_combined.cumsum()
    seg_ret_30_annret = seg_ret_30_performance['Return(Ann.)']
    fac_stat.columns = ['Basic Statistics']
    factor_auto_correlation_rolling = factor_auto_correlation.rolling(window=20).mean()

    IC_combined_roll = IC_combined.rolling(60).mean()
    """
    seg_ret_year = seg_ret_perf_year['Return(Ann.)'].unstack()
    seg_num = len(seg_ret_year.columns)-2
    col_name=seg_ret_year.columns.tolist()
    spec_col = [col for col in col_name if col.find('-')>0]
    col_name_order = ['Q'+str(i+1) for i in range(seg_num)] + spec_col + ['Benchmark']        
    seg_ret_year = seg_ret_year[col_name_order]
    long_short_ret = (seg_ret.fillna(0)+1).groupby(seg_ret.index.year).cumprod()[spec_col]
    year_num = long_short_ret.groupby(long_short_ret.index.year).count()
    year_list = year_num.index.tolist()
    max_day = int(year_num.max())
    return_by_year = pd.DataFrame(columns=year_list,index=[i for i in range(max_day)])
    for year in year_list:
        return_by_year[year] = [i[0] for i in long_short_ret.loc[str(year)].values.tolist()]+[np.nan]*(max_day-int(year_num.loc[year]))
    seg_ret_performance['Sharpe Ratio'][spec_col] = np.nan
    """
    
    """table"""
    col_type = ['str1']*len(sum_df) 
    t_sum =  GenerateTable(sum_df,col_type,axis=0,reformat_type=False)
    col_type = ['dcm2','dcm2','pct2','dcm3','dcm3','dcm2','dcm2']
    t_fac_stat =  GenerateTable(fac_stat.T,col_type,axis=1,reformat_type=True)    
    col_type = ['pct2','pct2','dcm2','pct2','pct2','dcm2','pct2']
    t_seg_ret = GenerateTable(seg_ret_30_performance,col_type,axis=1,reformat_type=True)
    col_type = ['dcm5']*3
    t_IC_combined_stats= GenerateTable(IC_combined_stats,col_type,axis=0,reformat_type=True)

    
#    if easy_test == False:
#        #t_fac_corr = GenerateTable(fac_corr,col_type,axis=0,reformat_type=True) 
#        fac_corr_r20 = fac_corr.rolling(20).mean()
#        g_fac_corr = generate_plot(fac_corr_r20,plot_name='Correlation with Style Factor (rolling 20 days)',x_label='Day',y_label='Correlation')
    
    """graph"""
#    g_seg_ret_performance = generate_performance_report(seg_ret_performance.iloc[:,:6])
#    g_seg_cumret = generate_plot(seg_cumret,plot_name='Cummulative Return',x_label='Day',y_label='Cummulative Return')

    g_IC_decay = generate_plot(IC_decay,plot_name='IC Decay',x_label='Days after factor',y_label='IC',plot_type='bar')
    g_factor_auto_correlation_rolling = generate_plot(factor_auto_correlation_rolling,plot_name='Factor Auto Correlation',x_label='Date',y_label='Correlation')

#    g_return_by_year = generate_plot(return_by_year,plot_name=spec_col[0]+' Return by Year',x_label='day in year',y_label='Cummulative Return')
#    g_seg_ret_year = generate_plot(seg_ret_year,plot_name='Annualized Return by Year',x_label='Year',y_label='Return (Ann.)',plot_type='bar')

    #g_Alpha_cumsum = generate_plot(Alpha_cumsum,plot_name='Cummulative Alpha (IC*Dispersion)',x_label='Day',y_label='Cum Alpha')
    g_seg_ret_30_annret = generate_plot(seg_ret_30_annret,plot_name='Segment Return - All History',x_label='Quintile',y_label='Return (Ann.)',plot_type='bar')
    g_IC_combined_cumsum = generate_plot(IC_combined_cumsum,plot_name='Cumulative IC Comparison',x_label='Time',y_label='Cum IC')
    g_factor_ts = generate_plot(factor_ts,plot_name='Stock Count with Factor',x_label='Time',y_label='Number of Stocks')
    g_seg_return_30_stat_year = generate_segment_ret_year(seg_return_30_stat_year,col_name='Return(Ann.)')
    g_IC_combined_roll = generate_plot(IC_combined_roll,plot_name='IC (Rolling 120 day Average) ',x_label='Day',y_label='IC')
    
    """Note"""
    styles = getSampleStyleSheet()
    heading_size = styles['Heading4']
    h_sum = Paragraph('Factor Information',heading_size)
    #h_fac_stat = Paragraph('Factor Distribution',heading_size)
    h_seg_ret = Paragraph("Quintile Return Performance",heading_size)
    #h_turnover = Paragraph("Portfolio Turnover",heading_size)
    h_seg_ret_30_year = Paragraph("Segment Return by Year",heading_size)
    h_IC_combined_cumsum = Paragraph("IC Stats",heading_size)
    
    now=datetime.datetime.today()
    file_date=now.strftime("%Y%m%d_%H%M%S")    
    pdf_report_date='Test Date:  ' + now.strftime("%Y-%m-%d %H:%M:%S")   
    report_name = 'FactorBacktes_'+str(factor_name)+'_'+str(file_date)     
    #h_title = Paragraph("Factor Backtest Report",styles['Normal'])
    h_date = Paragraph(pdf_report_date,styles['Normal'])
    plt.ioff()
    
    doc = SimpleDocTemplate(output_folder+report_name+".pdf", pagesize=letter)
    elements = []
    #elements.append(h_title)
    elements.append(h_date)
    elements.append(h_sum)
    elements.append(t_sum)
    
    elements.append(h_IC_combined_cumsum)
    elements.append(t_IC_combined_stats)
    elements.append(g_IC_combined_cumsum)
    elements.append(g_IC_combined_roll)
    elements.append(PageBreak()) 
    #elements.append(h_fac_stat)
    elements.append(t_fac_stat) 

    elements.append(g_seg_ret_30_annret)
    elements.append(g_factor_ts) 
    elements.append(g_IC_decay)
    elements.append(PageBreak()) 
    
    elements.append(h_seg_ret_30_year)
    elements.append(g_seg_return_30_stat_year)
    elements.append(PageBreak()) 
    
    elements.append(g_factor_auto_correlation_rolling)
    
    
    elements.append(PageBreak()) 

    elements.append(h_seg_ret)    
    elements.append(t_seg_ret) 

    
    doc.build(elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    
    
    return 


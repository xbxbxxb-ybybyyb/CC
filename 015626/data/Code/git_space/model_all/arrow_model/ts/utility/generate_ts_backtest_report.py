import os
import datetime
import pandas as pd
import numpy as np
import warnings
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print (code_base)
sys.path.insert(0, os.path.dirname(code_base))
pa = '/data/user/012315/alpha'
sys.path.insert(0, pa)


#from .pdf_config import *		
#from .naming_config import *
from multifactor.backtest.pdf_config import *
from multifactor.backtest.naming_config import *


    
def dataframe2str(df, col_type, axis, reformat_type):
    """get dataframe column, return string with format"""
    df = df if axis == 1 else df.T
    df_col = df.columns.tolist()
    df_row = df.index.tolist()
    df_str = [''] + df_row
    for col, ct in zip(df_col, col_type):
        data = [col] + num2str(df[col].values.tolist(), ct) if reformat_type == True else [col] + df[col].values.tolist()
        df_str = np.vstack([df_str, data])
    df_str = df_str.T.tolist() if axis == 1 else df_str.tolist()
    return df_str

def num2str(data, data_type):
    # take number and change format, return list of string
    round_num = int(data_type[-1])
    number_type = data_type[:-1]
    if isinstance(data,np.float):
        if number_type == 'pct':
            data = ('{:' + ('.%d' % round_num) + '%'+ '}').format(data) if not pd.isnull(data) else 'NaN'
        elif number_type == 'dcm':
            data = ('{:' + ('.%d' % round_num) + 'f'+ '}').format(data) if not pd.isnull(data) else 'NaN'
    else:
        if number_type == 'pct':
            data = [('{:' + ('.%d' % round_num) + '%' + '}').format(i) if not pd.isnull(i) else 'NaN' for i in data]
        elif number_type == 'dcm':
            data = [('{:' + ('.%d' % round_num) + 'f' + '}').format(i) if not pd.isnull(i) else 'NaN' for i in data]
        elif number_type == 'str':
            data = [i for i in data]
    return data


def legend_helper():
    handles, labels = [], []
    for ax in plt.gcf().axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.append(h)
            labels.append(l)
    return handles, labels


def generate_table(df, col_type, axis, reformat_type):
    df_str = dataframe2str(df, col_type, axis, reformat_type)
    df_str[0] = [i.encode('utf-8') for i in df_str[0]]
    t = Table(df_str)
    mytable = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                          ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                          ('FONTNAME', (0, 0), (-1, -1), font_name),
                          ('FONTSIZE', (0, 0), (-1, -1), CANVAS_FONT_SIZE)])
    t.setStyle(mytable)
    return t

def generate_plot(df, plot_name, x_label, y_label, 
                  plot_type='line', rot=None, 
                  legend_outside=False, bottom=None, 
                  show_stats=False,show_format='pct2',
                  **kwargs):
   
    legend_on = True if min(df.shape) > 1 else False
    fig, ax = plt.subplots()
    df_plot = df.plot(kind=plot_type, figsize=(fig_width, fig_height),
                      legend=legend_on, fontsize=font_size_axis, rot=rot, **kwargs)
    if legend_on:
        if legend_outside:
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=font_size_legend)
        else:
            plt.legend(loc=legend_loc, fontsize=font_size_legend)
    if bottom is not None:
        plt.subplots_adjust(bottom=bottom)
    if plot_type=='line' and show_stats:
        if isinstance(df,pd.DataFrame):
            #if df.shape[1]>1:
            df_list = df.columns.tolist()
            add_str = ''
            for d in df_list:
                mean = df[d].mean()
                current_percentile = calc_percentile(df[d].dropna()).iloc[-1]*100
                add_str = add_str + '\n%s - Avg:%s  Current Percentile:%.2f'%(d,num2str(mean,show_format),current_percentile)+'%'
            plot_name = plot_name + add_str
        else:
            mean = df.mean()
            current_percentile = calc_percentile(df.dropna()).iloc[-1]*100
            plot_name = plot_name + '\nAvg:%s  Current Percentile:%.2f'%(num2str(mean,show_format),current_percentile)+'%'
    df_plot.set_title(plot_name, fontsize=font_size_title, fontweight=font_title_weight)
    df_plot.set_xlabel(x_label, fontsize=font_size_axis)
    df_plot.set_ylabel(y_label, fontsize=font_size_axis)
    imgdata = BytesIO()
    df_plot.figure.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=img_width*inch, height=img_height*inch)


def generate_price_with_label(price,label,show_week=False,plot_return=False):
    plt.figure(figsize=(fig_width, fig_height))
    label = label.reindex(index=price.index)
    fig, ax = plt.subplots()
    fig.set_size_inches(18,6)
    plt.plot(price)
    plt.rc('font', size=14)
    fake_x = price.index
    plt1 = plt.fill_between(x=fake_x, y1=label,y2=0, where=label>0,color='red', alpha=0.25, transform=ax.get_xaxis_transform())
    plt2 = plt.fill_between(x=fake_x, y1=label,y2=1, where=label<0,color='green', alpha=0.25, transform=ax.get_xaxis_transform())
    plt.ylim(price.min(), price.max())
    l1 = plt.legend([plt1, plt2], ["long", "short"], loc='upper left')
    if show_week:
        # Define the date format
        date_form = DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(date_form)
        # Ensure a major tick for each week using (interval=1)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    imgdata = BytesIO()
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    plt.style.use('ggplot')        
    return Image(imgdata, width=img_width*inch, height=img_height*inch)

def generate_plot_with_secondary(df1, df2, plot_name, x_label, y_label1, y_label2, plot_type='line'):
	   
    df1.index.name = ''
    df2.index.name = ''
    fig, ax = plt.subplots()
    df1_plot = df1.plot(ax=ax, kind=plot_type, figsize=(fig_width, fig_height),
                        fontsize=font_size_axis, legend=False)
    df1_plot.set_title(plot_name, fontsize=font_size_title, fontweight=font_title_weight)
			
    df1_plot.set_ylabel(y_label1, fontsize=font_size_axis)
    ax.set_xlabel(x_label, fontsize=font_size_axis)
    df2_plot = df2.plot(ax=ax, kind=plot_type, figsize=(fig_width, fig_height),
                        fontsize=font_size_axis, secondary_y=True, style='--', legend=False)
    df2_plot.set_ylabel(y_label2, fontsize=font_size_axis)
    plt.legend(*legend_helper(), loc=legend_loc, fontsize=font_size_legend)
    imgdata = BytesIO()
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=img_width*inch, height=img_height*inch)


def generate_ts_heatmap_by_month_plot(ps_raw, title_text, vmin, vmax, fmt='.2f', agg_method='mean'):
    year_list = list(set(ps_raw.index.year))
    year_list.sort(reverse=False)
    month_ps = pd.DataFrame(index=[i for i in range(1, 13)])
    for year in year_list:
        sliced = ps_raw.loc[str(year)]
        if agg_method == 'mean':
            month_ps[year] = sliced.groupby(sliced.index.month).mean()
        elif agg_method == 'sum':
            month_ps[year] = sliced.groupby(sliced.index.month).sum()
        else:
            raise NotImplementedError
    sns.set(font_scale=1.6)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    month_ps = month_ps.rename(index=month_mapper)
    month_ps.index.name = title_text
    month_ps.columns.name = ''
    plt.figure(figsize=(fig_width, fig_height))
    sns.heatmap(month_ps.T, vmin=vmin, vmax=vmax, linewidths=.5, cmap=cmap, annot=True, fmt=fmt)
    imgdata = BytesIO()
    plt.subplots_adjust(right=1, top=1)
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    plt.style.use('ggplot')
    return Image(imgdata, width=img_width*inch, height=img_height*inch)


def generate_heatmap_plot(ps_raw, title_text, vmin, vmax, font_scale=1.6,fmt='.2f'):
    sns.set(font_scale=font_scale)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    plt.figure(figsize=(fig_width, fig_height))
    sns.heatmap(ps_raw, vmin=vmin, vmax=vmax, linewidths=.5, cmap=cmap, annot=True, fmt=fmt)
    imgdata = BytesIO()
    plt.subplots_adjust(right=1, top=1)
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    plt.style.use('ggplot')
    return Image(imgdata, width=img_width*inch, height=img_height*inch)

def generate_ts_by_type_plot(ts, by='Month',x_label=None,ann_scale=False,vmin=-0.2,vmax=0.2,fmt='.2f'):
    if by == 'Month':
        grp_index = ts.index.month
        scale_num = 21
    elif by == 'Year':
        grp_index = ts.index.year
        scale_num = 252
    else:
        raise AssertionError
    grp_obj = ts.groupby(grp_index)
    grp_num = grp_obj.mean()
    if ann_scale:
        grp_num = grp_num*scale_num
    grp_num = grp_num.rename(index=month_mapper) if by == 'Month' else grp_num
    grp_num.index.name = x_label + ' by ' + by
    grp_num.columns.name = ''
    grp_num = grp_num.fillna(0)
    sns.set(font_scale=1.6)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    plt.figure(figsize=(fig_width, fig_height*1.8))
    sns.heatmap(grp_num.T, vmin=vmin, vmax=vmax, linewidths=.5, cmap=cmap, annot=True, fmt=fmt)
    plt.yticks(rotation=0)						  
    plt.tight_layout()
    imgdata = BytesIO()
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    plt.style.use('ggplot')
    return Image(imgdata, width=img_width*inch, height=img_height*inch*1.8)


def generate_bar_line_plot(df, title, bar_column, line_column,show_stats=False,show_format='pct2'):
    plt.figure(figsize=(fig_width, fig_height))
    plt.subplot(211)
    plt.bar(np.arange(len(df)), df[bar_column])
    if show_stats:
        df_avg,df_pct = df[bar_column].mean(),calc_percentile(df[bar_column].dropna()).iloc[-1]
        title = title+' - Avg: %s - Current Pct: %s'%(num2str(df_avg,show_format),num2str(df_pct,'pct2'))
    plt.title(title, fontsize=font_size_title, fontweight=font_title_weight)
    plt.xticks([])
    plt.xticks(fontsize=font_size_axis)
    plt.yticks(fontsize=font_size_axis)
    plt.subplot(212)
    plt.plot(df[line_column])
    plt.title(line_column, fontsize=font_size_title, fontweight=font_title_weight)
    plt.xlabel('')
    plt.xticks(fontsize=font_size_axis)
    plt.yticks(fontsize=font_size_axis)
    imgdata = BytesIO()
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=img_width*inch, height=img_height*inch)


def generate_line_subplot(df):
    df.index.name = ''
    height_scaler = min(max_fig_height, fig_height*len(df.columns)*0.75) / fig_height
    df.plot(subplots=True, figsize=(fig_width, fig_height*height_scaler), fontsize=font_size_axis)
    [ax.legend(loc=legend_loc, fontsize=font_size_legend) for ax in plt.gcf().axes]
    plt.subplots_adjust(bottom=0.05, top=0.99, wspace=0, hspace=0.1)
    imgdata = BytesIO()
    plt.savefig(imgdata, format=img_format, dpi=img_dpi)
    imgdata.seek(0)
    plt.close()
    return Image(imgdata, width=img_width*inch, height=img_height*inch*height_scaler)


def get_year_month_list(sdate,edate):
    # sdate,edate = 20180431,20180911
    n2s = lambda i: str(i) if i>9 else '0%d'%(i)
    sdate_dt = pd.Timestamp(sdate)
    edate_dt = pd.Timestamp(edate)
    s_year,e_year = str(sdate_dt.year), str(edate_dt.year)
    s_month,e_month = n2s(sdate_dt.month), n2s(edate_dt.month)
    s_year_month,e_year_month = s_year+s_month,e_year+e_month
    year_list = [str(i) for i in range(int(s_year),int(e_year)+1)]
    month_list = []
    for i in range(1,12+1):
        cm = n2s(i)
        month_list.append(cm) 
    year_month_list = [str(y)+str(m) for m in month_list for y in year_list 
                                         if str(y)+str(m)<=e_year_month and str(y)+str(m)>=s_year_month]
    year_month_list.sort()
    return year_month_list


def num2str(data, data_type):
    # take number and change format, return list of string
    round_num = int(data_type[-1])
    number_type = data_type[:-1]
    if isinstance(data,np.float):
        if number_type == 'pct':
            data = ('{:' + ('.%d' % round_num) + '%'+ '}').format(data) if not pd.isnull(data) else 'NaN'
        elif number_type == 'dcm':
            data = ('{:' + ('.%d' % round_num) + 'f'+ '}').format(data) if not pd.isnull(data) else 'NaN'
        elif number_type == 'str':
            data = str(data)            
    else:
        if number_type == 'pct':
            data = [('{:' + ('.%d' % round_num) + '%' + '}').format(i) if not pd.isnull(i) else 'NaN' for i in data]
        elif number_type == 'dcm':
            data = [('{:' + ('.%d' % round_num) + 'f' + '}').format(i) if not pd.isnull(i) else 'NaN' for i in data]
        elif number_type == 'str':
            data = [i for i in data]
    return data

def generate_ts_backtest_report(backtest_root,fac_lib_date,type_list = ['orig','scale'],
                                trade_contract_list = ['IC.CFE','IF.CFE'],version_notes=''):
    str_replace = {'累积净值':'cum_ret',
        '夏普比率':'sharpe',
        '年化收益':'ret',
        '最大回撤':'mdd',
        '最大回撤开始时间':'mdd_start',
        '最大回撤结束时间':'mdd_end',
        '年化收益/回撤比':'calmar',
        '总交易笔数':'trade_cnt',
        '平均每天交易笔数':'trade/day',
        '亏损笔数':'loss_cnt',
        '盈利笔数':'win_cnt',
        '胜率':'hit_rate',
        '做多笔数':'long_cnt',
        '做多胜率':'long_hit_rate',
        '做空笔数':'short_cnt',
        '做空胜率':'short_hit_rate',
        '每笔交易平均盈亏':'avg_ret',
        '盈亏收益比':'wlr',
        '单笔最大盈利':'max_gain',
        '单笔最大亏损':'max_loss',
        '单笔最长持有时间':'holding_time_max',
        '单笔最短持有时间':'holding_time_min',
        '平均持仓周期':'hold_time',
        '最大连续盈利笔数':'cum_win_max',
        '最大连续亏损笔数':'cum_loss_max',
        '平均每日杠杆':'leverage',
        '止损次数':'stop_loss_cnt'}
    order_list_all = ['pred_comb2', 'pred_comb','lgbm_cla','lgbm_reg','mlp_reg','lstm_cla',
                  'et_cla','lasso_reg', 'lr_cla', 'ew']
    current_time = datetime.datetime.today()

    path_info = {i:{} for i in trade_contract_list}
    for trade_contract in trade_contract_list:
        ticker_ini = trade_contract[:2].lower()
        save_path_bkt = os.path.join(backtest_root,fac_lib_date,ticker_ini)
        dict_tmp = {}
        for type_itr in type_list:
            csv_path_stats = os.path.join(save_path_bkt,'prod',type_itr,'model_stats.csv')
            csv_path_return = os.path.join(save_path_bkt,'prod',type_itr,'model_cumret.csv')
            path_info_itr = {type_itr:{'stats':csv_path_stats,
                                       'return':csv_path_return}}
            path_info[trade_contract].update(path_info_itr)

    trade_contract_list = list(path_info.keys())
    type_list =  list(path_info[trade_contract_list[0]].keys())
    path_ex = path_info[trade_contract_list[0]][type_list[0]] 
    path_ex = list(path_ex.values())[0] if isinstance(path_ex,dict) else path_ex
    output_folder = os.path.dirname(os.path.dirname(os.path.dirname(path_ex)))
    report_name = 'ts_backtest_%s' %(current_time.strftime('%Y%m%d_%H%M%S'))
    pdf_name = os.path.join(output_folder,report_name + '.pdf')
    version_notes = os.path.basename(backtest_root) if version_notes=='' else version_notes
    versiont_str = ' - '+str(version_notes) if version_notes != '' else ''
    h_sum = Paragraph('TS Stratey Monitor%s'%(versiont_str), heading_size)
    h_stats = Paragraph('Model Performance', heading_size)

    # set path   
    doc = SimpleDocTemplate(pdf_name,
                            pagesize=letter,
                            topMargin=0.8 * inch,
                            bottomMargin=0.8 * inch)
    elements = []
    elements.append(h_sum)

    for trade_contract in trade_contract_list:
        for type_itr in type_list:
            csv_path_stats = path_info[trade_contract][type_itr]['stats']
            csv_path_return = path_info[trade_contract][type_itr]['return']
            h_itr = Paragraph('%s - %s'%(trade_contract,type_itr), heading_size)
        
            stats_df = pd.read_csv(csv_path_stats,encoding='gbk',index_col=0,header=0)
            return_df = pd.read_csv(csv_path_return,index_col=0,header=0)
            order_list = [i for i in order_list_all if i in return_df.columns]
            return_df = return_df[order_list]
            return_df.index = [pd.Timestamp(i) for i in return_df.index]
            stats_df = stats_df.rename(index=str_replace)
            stats_df = stats_df.applymap(lambda x:x.replace('分钟',''))
            sdate_bkt,edate_bkt = return_df.index[0],return_df.index[-1]
            take_list = [ 'ret','sharpe','calmar','mdd','mdd_start', 'mdd_end',
            'cum_ret','trade/day','hit_rate','wlr','hold_time']
            stats_df = stats_df.loc[take_list]
            stats_df = stats_df[order_list]

            if type_itr == 'orig':
                corr_df = return_df.corr() 
                corr_df[corr_df==1] = np.nan
                title_port_corr = '%s: %s - %s'%(trade_contract,sdate_bkt,edate_bkt)
                g_corr_df = generate_heatmap_plot(ps_raw=corr_df, title_text=title_port_corr,
                                                  font_scale=1.2,
                                                  vmin=-0.3, vmax=1,fmt='.2%')
                # rolling trail
                daily_ret = return_df - return_df.shift(1)
                roll_list = [1,5,10,15,20,40]
                valid_num = len(return_df)
                rl = [i for i in roll_list if i<=valid_num]
                rl.append(valid_num)

                ret_roll = pd.DataFrame([daily_ret.iloc[-i:,:].sum() for i in rl],
                                        index=['last %d d'%(i) for i in rl])
                title_ret_roll= 'Recent Performance (%s - %s)'%(sdate_bkt,edate_bkt)
                title_corr_df = 'Correlation (%s - %s)'%(sdate_bkt,edate_bkt)
                title_ret_by_month = 'Return by Month (%s - %s)'%(sdate_bkt,edate_bkt)
                h_ret_roll = Paragraph(title_ret_roll, heading_size)
                h_corr_df = Paragraph(title_corr_df, heading_size)
                h_ret_by_month = Paragraph(title_ret_by_month, heading_size)

                year_month_list = get_year_month_list(sdate_bkt,edate_bkt)
                ret_by_month = daily_ret.groupby(daily_ret.index.month).sum()
                ret_by_month.index = year_month_list
                ret_by_month = ret_by_month.T
                g_ret_roll = generate_plot(df=ret_roll, plot_name=title_ret_roll, x_label='', y_label='ret', 
                                           plot_type='bar', rot=90) 
                g_ret_by_month = generate_heatmap_plot(ps_raw=ret_by_month, title_text=title_ret_by_month, 
                                                       font_scale=1.5,vmin=-0.03, vmax=0.03,
                                                       fmt='.2%')

            h_time_itr = Paragraph('Period: %s - %s'%(sdate_bkt,edate_bkt), heading_size)

            index_list = stats_df.index.tolist()
            col_type_stats = ['str0' for i in range(len(index_list))]
            t_stats_df = generate_table(stats_df.T, col_type_stats, axis=1, reformat_type=False)

            plt.ioff()
            g_return_df = generate_plot(return_df, plot_name='Cum Ret', x_label='', 
                                            y_label='Cummulative Return')

            plt.ioff()

            elements.append(h_itr)
            elements.append(h_time_itr)
        
            elements.append(h_stats)
            elements.append(t_stats_df)
            elements.append(g_return_df)

            if type_itr == 'orig':
                elements.append(PageBreak())

                elements.append(h_corr_df)
                elements.append(g_corr_df)
                elements.append(h_ret_roll)                
                elements.append(g_ret_roll)
                elements.append(h_ret_by_month)
                elements.append(g_ret_by_month)
                
            elements.append(PageBreak())
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages, canvasmaker=NumberedCanvas)
    print(pdf_name)
    return

import pickle,dill
import time
import datetime as dt


def print_current_time():
        return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def show_time_spent(ts):
        if ts>60:
                time_spent = (str((round((ts)/60,2)))+' minutes')
        else:
                time_spent = (str((round((ts),2)))+' seconds')
        return time_spent

def print_time(toc,tic,show_time=True,remain_iter=None):
        ts = toc-tic
        time_spent = show_time_spent(ts)
        if remain_iter is not None:
                time_spent_total = '/ remain %s'%(show_time_spent(ts*remain_iter))
        else:
                time_spent_total = ''
        time_str = ' (used %s%s) '%(time_spent,time_spent_total)
        if show_time:
                time_str = time_str +'- '+ print_current_time()
        return time_str

def save_pickle(save_dict,save_path):
        print ('saving data to:\n',save_path)
        folder= os.path.dirname(save_path)
        if not os.path.exists(folder):
                os.makedirs(folder)
        if os.path.exists(save_path):
                print ('remove existing one')
                os.remove(save_path)
        with open(save_path, 'wb') as input:
                pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
        return 

def read_pickle(save_path=None,verbose=True):
        tic = time.time()
        with open(save_path, 'rb') as input:
                save_dict = pickle.load(input)
        toc = time.time()
        if verbose:
                print('loading done - %s - %s   '%(print_time(toc,tic),save_path))
        return save_dict




def generate_ts_signal_report(edate,prod_save_base = '/data/user/012315/prod/ts/daily/open2open',
                              output_folder = '/data/user/012315/prod/ts/signal_report',                             
                              trade_contract_list = ['IC.CFE','IF.CFE','IH.CFE','TF.CFE','T.CFE'],
                              sdate_track='2021',report_name_prefix='ts_signal',version_str=''):
    order_list =  ['IC.CFE','IF.CFE','IH.CFE','TF.CFE','T.CFE',
                   'J.DCE','JM.DCE','I.DCE','RB.SHF','HC.SHF',
                   'FG.CZC','ZC.CZC','RM.CZC','MA.CZC','AL.SHF',
                   'CF.CZC','CS.DCE','JD.DCE','L.DCE','M.DCE','PB.SHF','PP.DCE',
                   'RU.SHF','SF.CZC','SM.CZC','SN.SHF','SR.CZC','TA.CZC','ZN.SHF']
                   
    current_time = datetime.datetime.today()
    current_time_str = current_time.strftime('%Y%m%d_%H%M%S')
    last_day = 5
    num_cut = 10

    print('generating ts signal report for %s'%(str(edate)))
    if output_folder is not None:
        output_folder = output_folder
    else:
        output_folder = os.path.join(prod_save_base,str(edate))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)            

    report_name = '%s_%s_%s' %(report_name_prefix,str(edate),current_time_str)
    pdf_name = os.path.join(output_folder,report_name + '.pdf')
    h_sum = Paragraph('%s TS Signal Report --- %s %s'%(' '*10,version_str,str(edate)), heading_size)
    h_report_time = Paragraph('Report time: %s'%(current_time_str),heading_size)

    # set path   
    doc = SimpleDocTemplate(pdf_name,
                            pagesize=letter,
                            topMargin=0.8 * inch,
                            bottomMargin=0.8 * inch)
    elements = []
    elements.append(h_report_time)
    elements.append(h_sum)

    if trade_contract_list is None:
        trade_contract_list_raw = os.listdir(os.path.join(prod_save_base,str(edate),'score'))
        trade_contract_list = [cmty_mapper[i.split('.')[0]] for i in trade_contract_list_raw]
        trade_contract_list = [i for i in order_list if i in trade_contract_list]
        print(trade_contract_list)

    res_prod_dict = {}
    pkl_fail_list = []
    trade_contract_list_use = []
    for trade_contract in trade_contract_list:
        try:
            score_path = os.path.join(prod_save_base,str(edate),'score','%s.pkl'%(trade_contract[:-4]))
            res_dict = read_pickle(score_path)
            res_prod_dict[trade_contract] = res_dict
            trade_contract_list_use.append(trade_contract)
        except:
            pkl_fail_list.append(trade_contract)
    if len(pkl_fail_list)>0:
        h_pkl_fail_list = Paragraph('Product Failed: %s'%(str(pkl_fail_list)),heading_size)
        elements.append(h_pkl_fail_list)
    trade_contract_list = trade_contract_list_use
    score_signal_list = []
    score_list,price_list = [],[]
    for trade_contract in trade_contract_list:
        score_signal_itr = res_prod_dict[trade_contract]['score_signal'].tail(1)
        score_signal_list.append(score_signal_itr)
        score_list.append(res_prod_dict[trade_contract]['score_signal']['score'])
        price_list.append(res_prod_dict[trade_contract]['score_signal']['price'])
    score_signal = pd.concat(score_signal_list,axis=0)
    score_signal.index = trade_contract_list
    score_signal.columns = [i.lower() for i in score_signal.columns]
    score_df = pd.concat(score_list,axis=1)
    score_df.columns = trade_contract_list
    price_df = pd.concat(price_list,axis=1)
    price_df.columns = trade_contract_list
    try:
        col_list = ['trade','signal','score','price','days2switch','ticker']
        score_signal = score_signal[col_list]
        score_signal['score'] = score_signal['score'].round(2)
        col_type_stats = ['str0', 'dcm0', 'dcm0','dcm2','str0','str0']
    except:
        col_list = ['trade','signal','score','price','days2switch']
        score_signal = score_signal[col_list]
        score_signal['score'] = score_signal['score'].round(2)
        col_type_stats = ['str0', 'dcm0', 'dcm0','dcm2','str0']
    t_score_signal = generate_table(score_signal, col_type_stats, axis=1, reformat_type=False)
    score_df_last = score_df.iloc[-last_day:,:].T
    score_df_last.columns = [dt.datetime.strftime(i,'%Y%m%d') for i in score_df_last.columns]
    col_type_stats = ['dcm4' for i in range(last_day)]
    t_score_df_last = generate_table(score_df_last, col_type_stats, axis=1, reformat_type=True)

    elements.append(t_score_signal)
    elements.append(PageBreak())
    elements.append(t_score_df_last)

    elements.append(PageBreak())
    contract_num = len(trade_contract_list)
        
    for trade_contract in trade_contract_list:
        ret_trade = res_prod_dict[trade_contract]['backtest_res']['ret_trade'].fillna(0)
        trade_stats = res_prod_dict[trade_contract]['backtest_res']['trade_stats']
        ret_trade_by_year = res_prod_dict[trade_contract]['backtest_res']['ret_trade_by_year']
        
        h_trade_contract = Paragraph('%s ~ %s ~ %s'%(trade_contract,version_str,edate), heading_size)

        h_trade_stats = Paragraph('Full History Trade Stats', heading_size)
        col_type_stats = ['pct2','pct2','dcm2','pct2','dcm2','dcm2','dcm2']
        t_trade_stats = generate_table(trade_stats, col_type_stats, axis=1, reformat_type=True)

        h_ret_trade_by_year = Paragraph('Trade Stats by Year', heading_size)
        if 'Sharpe' in ret_trade_by_year.columns:
            col_type_stats = ['pct2','pct2','pct2','dcm2','pct2','dcm2','dcm2','dcm2']            
        else:
            col_type_stats = ['pct2' for i in range(len(ret_trade_by_year))]
        #t_ret_trade_by_year = generate_table(ret_trade_by_year.T, col_type_stats, axis=1, reformat_type=True)
        ret_trade_by_year = ret_trade_by_year.iloc[-5:,:]
        t_ret_trade_by_year = generate_table(ret_trade_by_year, col_type_stats, axis=1, reformat_type=True)
        
        plt_title = '%s ~ CumRet (%s - %s) '%(trade_contract,sdate_track,edate)
        h_cum_ret = Paragraph(plt_title, heading_size)
        cum_ret = ret_trade.loc[sdate_track:].cumsum()
        g_cum_ret = generate_plot_with_secondary(df1=cum_ret[['long','short','long_short','benchmark']],
                                     df2=cum_ret[['relative']], 
                                     plot_name=plt_title, 
                                     x_label='Date', 
                                     y_label1='Total Return(%)', 
                                     y_label2='Relative Return(%)',
                                     plot_type='line')
        sdate_full = ret_trade.index[0]
        plt_title_cum_ret_full = '%s ~ CumRet Full History (%s - %s)'%(trade_contract,sdate_full,edate)
        h_cum_ret_full = Paragraph(plt_title_cum_ret_full, heading_size)
        cum_ret_full = ret_trade.cumsum()
        g_cum_ret_full = generate_plot_with_secondary(df1=cum_ret_full[['long','short','long_short','benchmark']],
                                     df2=cum_ret_full[['relative']], 
                                     plot_name=plt_title_cum_ret_full, 
                                     x_label='Date', 
                                     y_label1='Total Return(%)', 
                                     y_label2='Relative Return(%)',
                                     plot_type='line')
        
        plt_title_price_score = '%s ~ Price vs Score (%s - %s) '%(trade_contract,sdate_track,edate)
        g_price_score = generate_plot_with_secondary(df1=price_df[trade_contract].loc[sdate_track:],
                                 df2=score_df[trade_contract].loc[sdate_track:], 
                                 plot_name=plt_title_price_score, 
                                 x_label='Date', 
                                 y_label1='Price', 
                                 y_label2='Score',
                                 plot_type='line')        

        price = res_prod_dict[trade_contract]['score_signal']['price'].loc[sdate_track:]
        label = res_prod_dict[trade_contract]['score_signal']['signal'].loc[sdate_track:].shift(1)
        g_price_label = generate_price_with_label(price,label,show_week=False,plot_return=False)

        price_full = res_prod_dict[trade_contract]['score_signal']['price'].loc[sdate_full:]
        label_full = res_prod_dict[trade_contract]['score_signal']['signal'].loc[sdate_full:].shift(1)
        g_price_label_full = generate_price_with_label(price_full,label_full,show_week=False,plot_return=False)

        
        plt.ioff()
        elements.append(h_trade_contract)
        elements.append(h_trade_stats)
        elements.append(t_trade_stats)
        #elements.append(h_ret_trade_by_year)
        elements.append(t_ret_trade_by_year)
        #elements.append(h_cum_ret)        
        elements.append(g_cum_ret)
        elements.append(g_cum_ret_full)
        elements.append(PageBreak())
        """
        if contract_num<num_cut:
            elements.append(g_price_label)
            elements.append(g_price_score)
            #elements.append(h_cum_ret_full)        
            elements.append(g_price_label_full)
        elements.append(PageBreak())
        """
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages, canvasmaker=NumberedCanvas)
    print(pdf_name)
    return



"""
fac_lib_date = str(get_current_date())

backtest_root = '/data/user/012315/share/ts/strategy/minute/backtest'
generate_ts_backtest_report(backtest_root,fac_lib_date,type_list = ['orig','scale'],
                            trade_contract_list = ['IC.CFE','IF.CFE'])

"""


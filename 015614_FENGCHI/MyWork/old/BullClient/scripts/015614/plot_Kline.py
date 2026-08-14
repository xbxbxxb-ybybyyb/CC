############先画图，按股票名称和日期保存#################
import pandas as pd
import numpy as np
import gc
import sys, time, matplotlib
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.ticker as ticker
from matplotlib.pyplot import MultipleLocator

sys.path.append('/data/group/800319')
from dataApi import getData, tradeDate, stockList

myfont = matplotlib.font_manager.FontProperties(fname='STKAITI.TTF')


def Get_Data(day_deliver, date_list):
    ######第一步：先集成每日的日间dataframe######
    stock_deliver_today = day_deliver[['委托日期', '成交数量', '成交金额']].groupby('委托日期').sum()
    stock_deliver_today['当前持仓'] = stock_deliver_today['成交数量'].cumsum()
    # stock_deliver_today['均价']=stock_deliver_today['成交金额']/stock_deliver_today['成交数量']
    ##截取买卖前后20日走势##
    start_date = sorted(list(set(stock_deliver_today.index)))[0]
    end_date = sorted(list(set(stock_deliver_today.index)))[-1]
    date = date_list[date_list.index(start_date) - 20:date_list.index(end_date) + 20]
    Daily_price = getData.get_daily_1stock(stock, date_list=date, factor_list=['high', 'open', 'low', 'close'],
                                           type='stock', diy_address=None)
    Daily_price['当前持仓'] = stock_deliver_today['当前持仓']
    Daily_price.fillna(method='ffill', inplace=True)
    Daily_price.index.names = ['date']
    ######第二步：集成每日的日内dataframe#########
    min_price = getData.get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date, minute_interval=1,
                                           code_list=[stock], type='stock', diy_address=None)
    min_price.fillna(method='ffill', inplace=True)

    Inday_price = day_deliver[['委托日期', '成交时间', '成交数量', '成交金额']].groupby(['委托日期', '成交时间']).sum()
    Inday_price['成交均价'] = Inday_price['成交金额'] / Inday_price['成交数量']
    Inday_price['当前持仓'] = Inday_price['成交数量'].cumsum()

    min_price[['成交数量', '当前持仓']] = Inday_price[['成交数量', '当前持仓']]
    min_price['当前持仓'] = min_price['当前持仓'].fillna(method='ffill')
    min_price['当前持仓'] = min_price['当前持仓'].apply(lambda x: max(x, 0))
    min_price.index.set_levels(
        pd.Series(min_price.index.levels[1]).apply(lambda x: time.strftime("%H:%M", time.strptime(str(x), "%H%M"))),
        level=1, inplace=True)

    return Daily_price, min_price, start_date, end_date


def draw_Picture(Daily_price, min_price, start_date, end_date):
    #######第三步：画图——上面是日间###########################
    def format_date(x, pos=None):
        if x < 0 or x > len(date_tickers) - 1:
            return ''
        return date_tickers[int(x)]

    data = Daily_price.reset_index().fillna(0)
    data = data[['date', 'open', 'close', 'high', 'low', '当前持仓']]
    date_tickers = data.date.values
    weekday_quotes = [tuple([i] + list(quote[1:])) for i, quote in enumerate(data.values)]

    fig = plt.figure(figsize=(30, 20))
    ax = fig.add_subplot(4, 1, 1)
    big = 3
    if len(data) > 100 and len(data) < 150:
        big = 5
    elif len(data) > 150 and len(data) < 200:
        big = 10
    elif len(data) > 200:
        big = 10
    ax.xaxis.set_major_locator(ticker.MultipleLocator(big))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax.grid(True)

    mpf.candlestick_ochl(ax, weekday_quotes, width=0.8, colorup='r', colordown='green', alpha=1)
    plt.title(stockList.trans_int2windcode(stock) + '  ' + stock_deliver['证券名称'].iloc[0], fontproperties=myfont,
              fontsize=20, x=0.5)
    plt.ylabel('股价', fontproperties=myfont)

    ax2 = fig.add_subplot(4, 1, 2)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(big))
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax2.grid(True)
    plt.bar(data.index, data['当前持仓'].values, width=0.7)
    plt.ylabel('当前持仓', fontproperties=myfont)

    #######第四步：画图——下面是日间###########################
    indaydate = date_list[date_list.index(start_date):date_list.index(end_date) + 1]
    for i in range(1, len(indaydate) + 1):
        #######先绘制函数图象##########
        today = indaydate[i - 1]
        today_result = min_price.loc[today].fillna(0)

        def format_indaydate(x, pos=None):
            if x < 0 or x > len(today_result) - 1:
                return ''
            return today_result.index[int(x)]

        big = 30
        if len(indaydate) > 6 and len(indaydate) < 10:
            big = 60
        elif len(indaydate) > 10:
            big = 120
        exec('ax1' + str(i) + ' = plt.subplot(4,len(indaydate), ' + str(i + 2 * len(indaydate)) + ')')
        # exec('ax1'+str(i)+'.xaxis.set_major_locator(ticker.MultipleLocator(big))')
        # exec('ax1'+str(i)+'.xaxis.set_major_formatter(ticker.FuncFormatter(format_indaydate))')

        exec('ax1' + str(i) + '.plot(today_result.index,today_result[stock],\'\')')
        exec('ax1' + str(i) + '.set_title(today)')

        exec('ax1' + str(i) + '.set_autoscaley_on(False)')
        exec('ax1' + str(i) + '.set_ylim(min_price[stock].min()-0.1, min_price[stock].max()+0.1)')
        if i == 1:
            exec('ax1' + str(i) + '.set_ylabel(\'分钟收盘价\',fontproperties=myfont),')
        else:
            exec('ax1' + str(i) + '.set_yticks([])')
            ########再绘制成交量图像##########
        exec('ax2' + str(i) + ' = ax1' + str(i) + '.twinx()')
        exec('ax2' + str(
            i) + '.bar(today_result.index,abs(today_result[\'成交数量\']),color=today_result[\'成交数量\'].apply(lambda x:\'r\' if x>0 else \'g\').to_list(),width= 1.1)')
        exec('ax2' + str(i) + '.set_ylim(0, min_price[\'成交数量\'].max())')
        exec('ax2' + str(i) + '.set_yticks([])')

        exec('ax2' + str(i) + '.xaxis.set_major_locator(ticker.MultipleLocator(big))')
        exec('ax2' + str(i) + '.xaxis.set_major_formatter(ticker.FuncFormatter(format_indaydate))')

        ########再绘制持仓数量图像##########
        exec('ax3' + str(i) + ' = plt.subplot(4,len(indaydate), ' + str(i + 3 * len(indaydate)) + ')')
        exec('ax3' + str(i) + '.xaxis.set_major_locator(ticker.MultipleLocator(big))')
        exec('ax3' + str(i) + '.xaxis.set_major_formatter(ticker.FuncFormatter(format_indaydate))')

        exec('ax3' + str(i) + '.bar(today_result.index,today_result[\'当前持仓\'],color=\'grey\',width= 1)')

        # exec('ax3'+str(i)+'.set_title(today)')
        exec('ax3' + str(i) + '.set_ylim(0, min_price[\'当前持仓\'].max())')

        if i == 1:
            exec('ax3' + str(i) + '.set_ylabel(\'当前持仓\',fontproperties=myfont)')
        else:
            exec('ax3' + str(i) + '.set_yticks([])')

    plt.subplots_adjust(left=0.00, top=0.88, right=0.65, bottom=0.08, wspace=0.00)
    plt.savefig('/data/user/fengchi/BullClient/产品分析/' + str(stock) + '_startdate_' + str(start_date) + '.jpg',
                dpi=200, bbox_inches='tight')
    plt.show()


######先获取个股每日的交易数据###########
root_path = '/data/user/fengchi/BullClient/'
deliver = pd.read_excel(root_path + 'OneManDeal/交易记录.xlsx', index_col=0)
stock_list = list(set(deliver['证券代码']))
date_list = tradeDate.get_date_range(20190711, 20200831)
min_price = getData.get_minute_1factor('close', start_datetime=date_list[0], end_datetime=date_list[-1],
                                       minute_interval=1, code_list=stock_list, type='stock', diy_address=None)
#######处理分钟数据，使得委托日期和成交能够对应上#######
deliver['成交时间'] = deliver['成交时间'].apply(lambda x: int(x / 100))
deliver['成交金额'] = deliver['成交数量'] * deliver['成交价格']  # 把金额修改一下方向

######第一步：先选出一笔交易##########
for stock in stock_list:
    gc.collect()
    stock_deliver = deliver[deliver['证券代码'] == stock]
    #####先清洗数据，从剩余股数=成交数量的时间开始统计#########
    for index in stock_deliver.index:
        if stock_deliver.loc[index, '剩余股数'] != stock_deliver.loc[index, '成交数量']:
            stock_deliver.drop(index, inplace=True)
        else:
            break
    if len(stock_deliver) == 0:
        print(str(stock) + '缺失')
        continue
    j = 0
    for i in range(0, len(stock_deliver)):
        if i == len(stock_deliver) - 1:
            day_deliver = stock_deliver[j:]
            Daily_price, min_price, start_date, end_date = Get_Data(day_deliver, date_list)
            if min_price[stock].isna().sum() <= len(min_price) / 2:
                draw_Picture(Daily_price, min_price, start_date, end_date)

        elif stock_deliver.iloc[i, -1] == 0:
            day_deliver = stock_deliver[j:i + 1]
            j = i + 1
            Daily_price, min_price, start_date, end_date = Get_Data(day_deliver, date_list)
            if min_price[stock].isna().sum() <= len(min_price) / 2:
                draw_Picture(Daily_price, min_price, start_date, end_date)
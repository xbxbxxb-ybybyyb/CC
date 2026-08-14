import datetime as dt

import pandas as pd
from xquant.factordata import FactorData
from xquant.textdata import NewsData

import IO

nd = NewsData()
s = FactorData()
path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'
# 延期回复黑名单：当前年度的年度报告问询函，延期回复超过3次。
defer_param = 3

date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]

lastdate = s.tradingday(date, -2)[0]  # 上一交易日
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 1)  # 上一年度
last_year_period = last_year + '1231'  # 上一年度报告期
last_year_start_date = last_year + '0101'

# 读取年报公布日期
issuing_stock = IO.read_data([last_year_period, last_year_period],
                             alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIssuingDatePredict/AShareIssuingDatePredict.h5')
issuing_stock = issuing_stock.dropna(subset=['S_STM_ACTUAL_ISSUINGDATE']).reset_index()
issuing_stock_list = issuing_stock['Ticker'].unique()  # 已发布年报的股票列表

issuing_stock['dt'] = issuing_stock['S_STM_ACTUAL_ISSUINGDATE'].apply(lambda x: s.tradingday(str(x)[:-2], 1)[0])
issuing_stock = issuing_stock.set_index(['dt', 'Ticker'])
issuing_stock['tag'] = 1

out = pd.DataFrame(columns=['证券代码', '证券名称'])
out_back = pd.DataFrame()
if len(issuing_stock_list) > 0:
    # 读取股票公告数据
    info_list = []
    for stock in issuing_stock_list:
        if stock[-2:] not in ['SZ', 'SH', 'BJ']:
            continue
        info = nd.getAnnouncement([stock], str(last_year_start_date), str(date))
        if len(info) == 0:
            continue

        info = info.rename(columns={'PUBDATE': 'dt'})
        info['Ticker'] = stock
        info = info[['dt', 'Ticker', 'TEXTTITLE']]
        info_list.append(info)
    news_info = pd.concat(info_list, ignore_index=True)

    news_info = news_info.loc[~news_info['TEXTTITLE'].isna()]   # 剔除其中公告为空的部分

    # 处理公告数据
    news_info['tag'] = 1
    # 延期回复公告
    news_info_defer = news_info[news_info['TEXTTITLE'].apply(
        lambda x: '问询函' in x and '延期' in x and '回复' in x and ('年报' in x or '年度报告' in x) and '半年' not in x)].copy()
    news_info_defer['dt'] = news_info_defer['dt'].apply(lambda x: s.tradingday(x.strftime('%Y%m%d'), 1)[0])
    news_info_defer = news_info_defer.groupby(['dt', 'Ticker']).first()
    # 回复公告
    news_info_reply = news_info[news_info['TEXTTITLE'].apply(
        lambda x: '问询函' in x and '延期' not in x and ('回复' in x or '回函' in x or '复函' in x) and (
                    '年报' in x or '年度报告' in x) and '半年' not in x)].copy()
    news_info_reply['dt'] = news_info_reply['dt'].apply(lambda x: s.tradingday(x.strftime('%Y%m%d'), 1)[0])
    news_info_reply = news_info_reply.groupby(['dt', 'Ticker']).first()

    # 日期列表:年报发布列、延期列和回复列
    date_list = s.tradingday(last_year_period, date)
    index = pd.MultiIndex.from_tuples([(d, stock) for stock in issuing_stock_list for d in date_list],
                                      names=['dt', 'Ticker'])
    date_df = pd.DataFrame(index=index, columns=['issuing', 'defer', 'reply', 'cum_num'])
    date_df['issuing'] = issuing_stock['tag']
    date_df['defer'] = news_info_defer['tag']
    date_df['reply'] = news_info_reply['tag']
    date_df = date_df.fillna(0)

    # 进行筛选：有过3次延迟回复的股票
    defer_time = date_df.groupby('Ticker')['defer'].sum()
    defer_time3 = defer_time[defer_time >= defer_param]
    defer_stock_list = defer_time3.reset_index()['Ticker'].unique()
    defer_date_df = date_df.loc[[(d, stock) for stock in defer_stock_list for d in date_list]]

    # 计算累计延期回复次数（每次回复则清零）
    for stock in defer_stock_list:
        cum_num = 0
        issuing = 0
        for d in date_list:
            if issuing == 1 or defer_date_df.loc[(d, stock), 'issuing'] == 1:  # 年报已经发布
                issuing = 1
                if defer_date_df.loc[(d, stock), 'defer'] == 1:
                    cum_num += 1
                if defer_date_df.loc[(d, stock), 'reply'] == 1:
                    cum_num = 0
            defer_date_df.loc[(d, stock), 'cum_num'] = cum_num

    if defer_date_df['cum_num'].max() >= defer_param:
        # 输出名单
        res = defer_date_df[defer_date_df['cum_num'] >= defer_param].reset_index()
        res['dt'] = pd.to_datetime(res['dt'])
        res['证券代码'] = res['Ticker'].apply(lambda x: x[:~2])
        name_data = IO.read_data([last_year_period, lastdate], universe=list(res['Ticker'].unique()),
                                 columns=['STOCK_NAME'],
                                 alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
        name_data = name_data.groupby(['dt', 'Ticker']).first()
        for stock in res['Ticker'].unique():
            if (pd.to_datetime(lastdate), stock) in name_data.index:
                name_data.loc[(pd.to_datetime(date), stock), 'STOCK_NAME'] = name_data.loc[
                    (pd.to_datetime(lastdate), stock), 'STOCK_NAME']
        res = res.set_index(['dt', 'Ticker'])
        res['证券名称'] = name_data['STOCK_NAME']
        res['证券名称'] = res['证券名称'].astype(str)

        date_dt = pd.to_datetime(date)
        res_today = res.query('dt==@date_dt')
        if len(res_today) > 0:
            out = res_today[['证券代码', '证券名称']]
        else:
            out = pd.DataFrame(columns=['证券代码', '证券名称'])

        # 备选检查
        out_back = defer_date_df[defer_date_df.sum(axis=1) > 0].reset_index()


def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return


excel_saver({'黑名单': out,
             '备选检查': out_back}
            , path_user + 'defer_reply_list_%s.xlsx' % lastdate, index=False)
excel_saver({'黑名单':out,
             '备选检查':out_back}
            ,path_group+'defer_reply_list/defer_reply_list_%s.xlsx'%lastdate,index = False)


from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '延期回复上传成功：' + str(len(out)) + '只股票'
lm.sendMessage(message)
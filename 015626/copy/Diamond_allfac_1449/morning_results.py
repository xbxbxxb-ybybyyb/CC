with open('/dfs/user/015626/JupyterNotebooks/utils/imports.txt', 'r') as file:
    code = file.read()
    exec(code)
plt.rcParams['figure.figsize'] = [20, 5]
# import mplfinance as mpf
# from xdb.stockdata import StockData
import json

now_day = datetime.datetime.now().date().strftime('%Y%m%d')
pre_day = str(check_update_date()[0])

if not os.path.exists(f'/data/user/011477/Trade_Docs/{now_day}/Diamond_{now_day}/morning_Diamond_{now_day}.xlsx'):
    exit()

while True:
    if os.path.exists(f'/data/user/011477/Arrow/DiamondSummary_{now_day}.xlsx'):
        break
    if datetime.datetime.now().hour >= 11:
        send_link('diamond morning results is not exist!!!')
        break
    time.sleep(60)
    
now_df = pd.read_excel(f'/data/user/011477/Arrow/DiamondSummary_{now_day}.xlsx')
now_order_type = now_df['委托方向'].iloc[0]
now_df = now_df.set_index('证券代码').add_suffix('_now')

pre_df = pd.read_excel(f'/data/user/011477/order/tradingReport/tradingStat_{pre_day}.xlsx', sheet_name = 'Diamond_5160604')
pre_order_type = '买入开仓' if now_order_type == '卖出平仓' else '卖出开仓'
pre_df = pre_df[pre_df['委托方向'] == pre_order_type]
pre_df = pre_df.set_index('证券代码').add_suffix('_pre')

deal = now_df.join(pre_df)
deal.index = [x+'.CFE' for x in deal.index]

settle = IO.read_data([pre_day], columns = ['settle'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5')
settle = settle.reset_index(level = 0, drop = True)

deal = deal.join(settle, how = 'left')

deal['交易方向'] = 1 if pre_order_type == '买入开仓' else -1
deal['交易日'] = pd.to_datetime(pre_day)
deal = deal.reset_index()

send_link(str(deal[['交易日', 'index', '交易方向', '成交价格_pre', 'settle', '成交价格_now', '成交数量_now']].set_index('交易日')))
print(deal[['交易日', 'index', '交易方向', '成交价格_pre', 'settle', '成交价格_now', '成交数量_now']])
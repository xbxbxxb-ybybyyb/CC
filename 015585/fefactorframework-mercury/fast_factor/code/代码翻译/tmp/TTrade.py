factor_name = '930_allbs_allp_small_all_alldf_gbuy_vwappct_std_minus'


list_name = factor_name.split('_')
res = []

x0 = list_name[0]
dic0 = {
    '1m': '''max_time = trade_df['MDTime'].max()
    time_start = fun_get_time(max_time,-60)
    trade_df = trade_df[trade_df['MDTime'] >= time_start]
''',
    '930': '',
}
res.append(dic0[x0])

x4 = list_name[4]
dic4 = {
    'all': '',

    't50': '''trade_df = trade_df.tail(50)''',

    't100': '''trade_df = trade_df.tail(100)''',

    't300': '''trade_df = trade_df.tail(300)''',
}
res.append(dic4[x4])

x1 = list_name[1]
dic1 = {
    'allbs': '''''',
    'buy': '''trade_df = trade_df[trade_df['TradeBSFlag'] == 1]'''
}
res.append(dic1[x1])

x2 = list_name[2]
dic2 = {
    'allp': '''''',
    'up9': '''price9 = trade_df['pre_close'] * 1.09
    trade_df = trade_df[trade_df['TradePrice'] >= price9]''',
}
res.append(dic2[x2])

x3 = list_name[3]
dic3 = {
    'allamt': '',

    'big': '''groupby_buy = trade_df.groupby('TradeBuyNo')['TradeAmt'].sum()
    groupby_buy = groupby_buy[groupby_buy >= 200000]
    big_buy_list = list(groupby_buy.index)
    trade_df = trade_df[trade_df['TradeBuyNo'].isin(big_buy_list)]''',

    'small': '''groupby_buy = trade_df.groupby('TradeBuyNo')['TradeAmt'].sum()
    groupby_buy = groupby_buy[groupby_buy < 50000]
    small_buy_list = list(groupby_buy.index)
    trade_df = trade_df[trade_df['TradeBuyNo'].isin(small_buy_list)]'''
}
res.append(dic3[x3])



x7 = list_name[7]
dic7 = {
    'amt': '''trade_df['factor'] = trade_df['TradeAmt']''',

    'amt2mv': '''trade_df['factor'] = trade_df['TradeAmt'] / trade_df['pre_close'] / trade_df['ff_shares']''',

    'vol': '''trade_df['factor'] = trade_df['TradeQty']''',

    'pct': '''trade_df['factor'] = trade_df['TradePrice'] / trade_df['pre_close'] - 1''',

    'vwappct': '''trade_df['factor'] = trade_df['TradeAmt'].cumsum() / trade_df['TradeQty'].cumsum() / trade_df['pre_close'] - 1''',

    'buypctdiff': '''trade_df['max_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('max')
    trade_df['min_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('min')
    trade_df['factor'] = (trade_df['max_price'] - trade_df['min_price'])/trade_df['pre_close']''',

    'amt2buypctdiff': '''trade_df['max_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('max')
    trade_df['min_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('min')
    trade_df['factor'] = trade_df['TradeAmt'] / ((trade_df['max_price'] + 1e-2 - trade_df['min_price'])/trade_df['pre_close'])'''

}
res.append(dic7[x7])

x5 = list_name[5]
dic5 = {
    'alldf': '',

    'bsdf': '''trade_df1 = trade_df[trade_df['TradeBSFlag'] == 1]
    trade_df2 = trade_df[trade_df['TradeBSFlag'] == 2]''',

    'lendf1': '''trade_df1 = trade_df.tail(100) if len(trade_df) > 100 else trade_df
    trade_df2 = trade_df.iloc[:-100] if len(trade_df) > 100 else trade_df''',

    'lendf2': '''trade_df1 = trade_df.tail(100) if len(trade_df) > 100 else trade_df
    trade_df2 = trade_df.tail(1000) if len(trade_df) > 1000 else trade_df''',

    'pricedf1': '''trade_df1 = trade_df[trade_df['TradePrice'] / trade_df['pre_close'] >= 1.09]
    trade_df2 = trade_df[trade_df['TradePrice'] / trade_df['pre_close'] < 1.09]'''
}
res.append(dic5[x5])


x6 = list_name[6]
dic6 = {
    'calc': '''''',

    'calcbuybs': '''trade_df = trade_df.groupby('TradeBuyNo')['factor','TradeMoney'].sum()
    trade_df1 = trade_df[trade_df['TradeMoney'] >= 200000]
    trade_df2 = trade_df[trade_df['TradeMoney'] < 50000]''',

    'gbuy': '''trade_df1 = trade_df1.groupby('TradeBuyNo')['factor'].sum().to_frame(name = 'factor')
    trade_df2 = trade_df2.groupby('TradeBuyNo')['factor'].sum().to_frame(name = 'factor')''',

    'gsell': '''trade_df1 = trade_df1.groupby('TradeSellNo')['factor'].sum().to_frame(name = 'factor')
    trade_df2 = trade_df2.groupby('TradeSellNo')['factor'].sum().to_frame(name = 'factor')''',
}
if x5 == 'alldf':
    dic6['gbuy'] = '''trade_df = trade_df.groupby('TradeBuyNo')['factor'].sum().to_frame(name = 'factor')'''
    dic6['gsell'] = '''trade_df = trade_df.groupby('TradeSellNo')['factor'].sum().to_frame(name = 'factor')'''
res.append(dic6[x6])

x8 = list_name[8]
x9 = list_name[9]
def get_y9(x8, x6, x5, x9):
    if 'trade_df1' in dic5[x5] or 'trade_df1' in dic6[x6]:
        if x9 == 'minus':
            y9 = f'''res1 = f_calc_{x8}(trade_df1['factor'])
    res2 = f_calc_{x8}(trade_df2['factor'])
    res = res1 - res2'''
        elif x9 == 'div':
            y9 = f'''res1 = f_calc_{x8}(trade_df1['factor'])
    res2 = f_calc_{x8}(trade_df2['factor'])
    res = res1 / res2 if abs(res2) > 1e-8 else np.nan'''
        else:
            print('calculate not in minus or dive!!!')
            raise TypeError
    else:
        y9 = f'''res = f_calc_{x8}(trade_df['factor'])'''
    return y9
res.append(get_y9(x8, x6, x5, x9))

### ============嵌入到模板============
def read_py_file_to_string(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_string = file.read()
        return code_string
    except FileNotFoundError:
        return "文件未找到，请检查路径是否正确。"
    except Exception as e:
        return f"读取文件时发生错误: {e}"

file_path = "/data/user/015585/fefactorframework-mercury/fast_factor/code/代码翻译/tmp/factor_ttrade_sample.py"  # 替换为你的 .py 文件路径
code_content = read_py_file_to_string(file_path)
res_text = ''''''
for i in res:
    if i != '':
        res_text += i
        res_text += '\n'
        res_text += '    '
code_content = code_content.replace('factor_logic',res_text)
code_content = code_content.replace('factor_explain = ""',f'factor_explain = "{factor_name}"')
print(code_content)
# ### ==============保存===============
# file_name = '/data/user/015585/fefactorframework-mercury/fast_factor/code/代码翻译/结果文件/test.py'
#
# with open(file_name, 'w', encoding='utf-8') as file:
#     file.write(code_content)
# print(f"代码已保存到 {file_name}")

factor_name = 'amp_amtstd_nofilter_60_max_amtdiv'


list_name = factor_name.split('_')
res = []



x0 = list_name[0]
dic0 = {
    'high': '''df_ori['factor'] = df_ori['high'] / df_ori['pre_close']''',
    'open': '''df_ori['factor'] = df_ori['open'] / df_ori['pre_close']''',
    'low': '''df_ori['factor'] = df_ori['low'] / df_ori['pre_close']''',
    'close': '''df_ori['factor'] = df_ori['close'] / df_ori['pre_close']''',
    'highori': '''df_ori['factor'] = df_ori['high']''',
    'openori': '''df_ori['factor'] = df_ori['open']''',
    'lowori': '''df_ori['factor'] = df_ori['low']''',
    'closeori': '''df_ori['factor'] = df_ori['close']''',
    'vwapori': '''df_ori['factor'] = df_ori['vwap']''',
    'pct': '''df_ori['factor'] = df_ori['pct_chg']''',
    'pctturn': '''df_ori['factor'] = df_ori['pct_chg'] * df_ori['turn']''',
    'abspct': '''df_ori['factor'] = abs(df_ori['pct_chg'])''',
    'abspctturn': '''df_ori['factor'] = abs(df_ori['pct_chg']) * df_ori['turn']''',
    'logabspct': '''df_ori['factor'] = np.log(abs(df_ori['pct_chg'])+1e-3)''',
    'amt': '''df_ori['factor'] = df_ori['amt']''',
    'turn': '''df_ori['factor'] = df_ori['turn']''',
    'vwap': '''df_ori['factor'] = df_ori['vwap']/df_ori['pre_close']''',
    'syx1': '''df_ori['factor'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']''',
    'syx2': '''df_ori['max_open_close'] = df_ori[['open','close']].max(axis=1)
    df_ori['factor'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']''',
    'xyx1': '''df_ori['factor'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']''',
    'xyx2': '''df_ori['min_open_close'] = df_ori[['open','close']].min(axis=1)
    df_ori['factor'] = (df_ori['min_open_close'] - df_ori['low']) / df_ori['pre_close']''',
    'syx2xyx1': '''df_ori['syx1'] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xyx1'] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = df_ori['syx1'] - df_ori['xyx1']''',
    'syx2xyx2': '''df_ori['max_open_close'] = df_ori[['open', 'close']].max(axis=1)
    df_ori['min_open_close'] = df_ori[['open', 'close']].min(axis=1)
    df_ori['syx2'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']
    df_ori['xyx2'] = (df_ori['min_open_close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['factor'] = df_ori['syx2'] - df_ori['xyx2']''',
    'lengthk': '''df_ori['factor'] = abs(df_ori['open'] - df_ori['close']) / df_ori['pre_close']''',
    'c2v': '''df_ori['factor'] = df_ori['close'] / df_ori['vwap']''',
    'h2v': '''df_ori['factor'] = df_ori['high'] / df_ori['vwap']''',
    'l2v': '''df_ori['factor'] = df_ori['low'] / df_ori['vwap']''',
    'amp': '''df_ori['factor'] = (df_ori['high'] - df_ori['low']) / df_ori['pre_close']''',

    'corrv2c20': '''x = 'vwap'
    y = 'close'
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)''',

    'corramt2c20': '''x = 'amt'
    y = 'close'
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x : 1 if x > 1.0001 else -1 if x < -1.0001 else x)''',

    'corramt2syx20': '''x = 'amt'
    y = 'syx1'
    df_ori[y] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)''',

    'corramt2xyx20': '''x = 'amt'
    y = 'xyx1'
    df_ori[y] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)''',

    'corrpct2syx20': '''x = 'pct_chg'
    y = 'syx1'
    df_ori[y] = (df_ori['high'] - df_ori['close']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)''',

    'corrpct2xyx20': '''x = 'pct_chg'
    y = 'xyx1'
    df_ori[y] = (df_ori['close'] - df_ori['low']) / df_ori['pre_close']
    df_ori['xy'] = df_ori[x] * df_ori[y]
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])\
                       /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)''',

    'pctnew1': '''df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['high'] + df_ori['low'])*2''',
    'pctnew2': '''df_ori['factor'] = (df_ori['close'] - df_ori['pre_close'])/(df_ori['vwap'])''',
    'o2a': '''df_ori['factor'] = df_ori['open'] / df_ori['amt']''',
    'c2a': '''df_ori['factor'] = df_ori['close'] / df_ori['amt']''',
    'pre2vol': '''df_ori['factor'] = df_ori['pre_close'] / df_ori['volume']''',}
res.append(dic0[x0])

x1 = list_name[1]
dic1 = {
    'amtstd': '''df_ori['factor'] = df_ori['factor'] * df_ori['amt']''',
    'noamtstd': '''df_ori['max_open_close'] = df_ori[['open','close']].max(axis=1)
    df_ori['factor'] = (df_ori['high'] - df_ori['max_open_close']) / df_ori['pre_close']'''
}
res.append(dic1[x1])

x2 = list_name[2]
dic2 = {
    'nofilter': ''
}
res.append(dic2[x2])

x3 = list_name[3]
x4 = list_name[4]
x5 = list_name[5]
def get_code(x3, x4, x5):
    if x5 == 'amtdiv':
        y5 = \
f'''df_ori[factor_name] = df_ori['factor'].unstack().rolling({x3}).apply(f_calc_{x4}).stack()
    df_ori[factor_name] = df_ori[factor_name] / df_ori['amt'].unstack().rolling({x3}).apply(f_calc_{x4}).stack()'''
    elif x5 == 'noamtdiv':
        y5 = \
f'''df_ori[factor_name] = df_ori['factor'].unstack().rolling({x3}).apply(f_calc_{x4}).stack()'''
    else:
        y5 = \
f'''df_ori[factor_name] = df_ori['factor'].unstack().rolling({x3}).apply(f_calc_{x4}).stack() / df_ori['factor'].unstack().rolling({x5}).apply(f_calc_{x4}).stack().replace(0,np.nan)'''
    return y5
res.append(get_code(x3,x4,x5))

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

file_path = "/data/user/015585/fefactorframework-mercury/fast_factor/code/代码翻译/tmp/factor_md_sample.py"  # 替换为你的 .py 文件路径
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
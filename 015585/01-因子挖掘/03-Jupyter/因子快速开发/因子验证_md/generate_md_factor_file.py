import pandas as pd

factor_name_logic = 'abspct_amtstd_nofilter_120_sum_amtdiv'
def generate_tick_factor(factor_name_logic):
    list_name = factor_name_logic.split('_')
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

        'logabspct': '''df_ori['factor'] = np.log(abs(df_ori['pct_chg'])+0.001)''',

        'amt': '''df_ori['factor'] = df_ori['amt']''',

        'turn': '''df_ori['factor'] = df_ori['turn']''',

        'vwap': '''df_ori['factor'] = df_ori['vwap']''',

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
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
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
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
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
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
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
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
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
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
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
    df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
        /(df_ori['stdx'] * df_ori['stdy'])
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)'''
    }
    res.append(dic0[x0])

    x1 = list_name[1]
    dic1 = {
        'amtstd': '''df_ori['factor'] = df_ori['factor'] * df_ori['amt']''',
        'noamtstd': '''''',
    }
    res.append(dic1[x1])

    x2 = list_name[2]
    dic2 = {
        'nofilter': '''''',

        'up1': '''df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']''',

        'down1': '''df_ori['down'] = np.sign(df_ori['pct_chg'])
    df_ori['down'] = df_ori['down'].apply(lambda x : -1 if x <= -0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['down']''',

        'up2': '''df_ori['up'] = np.sign(df_ori['pct_chg'])
    df_ori['up'] = df_ori['up'].apply(lambda x : 1 if x >= 0.5 else -1 if x <=-0.5 else 0)
    df_ori['factor'] = df_ori['factor'] * df_ori['up']''',

        'amtup201': '''df_ori['amt20'] = df_ori['amt'].unstack().rolling(20,1).mean().stack()
    df_ori['amtup20'] = np.sign(df_ori['amt'] - df_ori['amt20'])
    df_ori['amtup20'] = df_ori['amtup20'].apply(lambda x :  1 if x >= 0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['amtup20']''',

        'amtdown201': '''df_ori['amt20'] = df_ori['amt'].unstack().rolling(20,1).mean().stack()
    df_ori['amtup20'] = np.sign(df_ori['amt'] - df_ori['amt20'])
    df_ori['amtup20'] = df_ori['amtup20'].apply(lambda x :  -1 if x <= -0.5 else np.nan)
    df_ori['factor'] = df_ori['factor'] * df_ori['amtup20']''',

        'amtup202': '''df_ori['amt20'] = df_ori['amt'].unstack().rolling(20,1).mean().stack()
    df_ori['amtup20'] = np.sign(df_ori['amt'] - df_ori['amt20'])
    df_ori['factor'] = df_ori['factor'] * df_ori['amtup20']''',
    }
    res.append(dic2[x2])
    if list_name[5] == 'amtdiv':
        y2 = dic2[x2].replace('factor','amt')
        res.append(y2)

    x3 = list_name[3]
    x4 = list_name[4]
    y4 = f'''df_ori[factor_name] = df_ori['factor'].unstack().rolling({x3},1).apply(lambda x : f_calc_{x4}(x)).stack()'''
    res.append(y4)
    if list_name[5] == 'amtdiv':
        y4 = y4.replace('factor_name','"amt"').replace('factor','amt')
        res.append(y4)
        y41 = '''df_ori[factor_name] = df_ori[factor_name] / df_ori['amt'].replace(0,np.nan)'''
        res.append(y41)

    x5 = list_name[5]
    if x5 != 'nodiv' and x5 != 'amtdiv':
        y5 = f'''df_ori[factor_name] = df_ori[factor_name] / df_ori['factor'].unstack().rolling({x5},1).apply(lambda x : f_calc_{x4}(x)).stack()'''
        res.append(y5)

    return res

### ============嵌入到模板============
def generate_tick_factor_file(factor_name_file, factor_name_logic):
    def read_py_file_to_string(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code_string = file.read()
            return code_string
        except FileNotFoundError:
            return "文件未找到，请检查路径是否正确。"
        except Exception as e:
            return f"读取文件时发生错误: {e}"

    file_path = "/data/user/015585/fefactorframework-mercury/fast_factor/code/代码翻译/tmp/factor_md_sample.py"
    code_content = read_py_file_to_string(file_path)
    res = generate_tick_factor(factor_name_logic)
    res_text = ''''''
    for i in res:
        if i != '':
            res_text += i
            res_text += '\n'
            res_text += '    '
    code_content = code_content.replace('factor_logic',res_text)
    code_content = code_content.replace('factor_explain = ""',f'factor_explain = "{factor_name_logic}"')
    code_content = code_content.replace('qyh_md_sample', factor_name_logic)
    code_content = code_content.replace('md_sample', factor_name_logic)
    return code_content
def save_factor_file(save_path, code_content):
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(code_content)
    print(f"代码已保存到 {save_path}")

if __name__ == "__main__":
    df_factor_info = pd.read_csv('/data/user/015585/fefactorframework-mercury/fast_factor/code/europa/因子整合/res_f_name_import.csv')
    df_factor_info = df_factor_info[(df_factor_info['factor_type'] == 'md') & (~df_factor_info['name'].str.contains('qyh')) & (~df_factor_info['name'].str.contains('zwh'))]
    factor_list = list(df_factor_info['name'])
    for factor_name in factor_list:
        code_content = generate_tick_factor_file(factor_name, factor_name)
        # print(code_content)
        save_factor_file(f'/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/因子验证_md/factor/factor_{factor_name}.py', code_content)

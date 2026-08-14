import pandas as pd

factor_name_logic = '930_after_all_all_0_bigger_t500_vwap2p_nostd_cv_nocompare'
def generate_tick_factor(factor_name_logic):
    list_name = factor_name_logic.split('_')
    res = []

    x0 = list_name[0]
    dic0 = {
        '930': '',
    }
    res.append(dic0[x0])

    x2 = list_name[2]
    dic2 = {
        'all': '''''',
        'amt25': '''limit = tick_df['ValueTrade'].quantile(0.25)
    tick_df = tick_df[tick_df['ValueTrade'] <= limit]''',
        'amt75': '''limit = tick_df['ValueTrade'].quantile(0.75)
    tick_df = tick_df[tick_df['ValueTrade'] >= limit]''',
    }
    res.append(dic2[x2])

    x3 = list_name[3]
    dic3 = {
        'all': '',

        'up': '''tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]''',

        'down': '''tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]'''
    }
    res.append(dic3[x3])

    x4 = list_name[4]
    dic4 = {
        '0': '',

        'p25': '''p = tick_df['LastPx'].quantile(0.25)''',

        'p75': '''p = tick_df['LastPx'].quantile(0.75)'''
    }
    res.append(dic4[x4])


    x5 = list_name[5]
    dic5 = {
        'bigger': '''tick_df = tick_df[tick_df['LastPx'] > p]''',

        'smaller': '''tick_df = tick_df[tick_df['LastPx'] < p]''',
    }
    if x4 != '0':
        res.append(dic5[x5])

    x6 = list_name[6]
    dic6 = {
        'all': '''''',
        'h500': '''tick_df = tick_df.head(20) if len(tick_df) > 20 else tick_df''',
        't500': '''tick_df = tick_df.tail(20) if len(tick_df) > 20 else tick_df''',
    }
    res.append(dic6[x6])

    x7 = list_name[7]
    dic7 = {
        'rcleanb': '''tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])''',

        'cleanb2ttran': '''tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['ValueTrade'].sum()+1)''',

        'cleanb2tran': '''tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['ValueTrade']+1)''',

        'b2tran': '''tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['factor'] = (tick_df['buy_amt'])/(tick_df['ValueTrade']+1)''',

        'b2ttran': '''tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['factor'] = (tick_df['buy_amt'])/tick_df['ValueTrade'].sum()''',

        'b2transtd': '''tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['factor'] = (tick_df['buy_amt'])/tick_df['ValueTrade'].std()''',

        's2tran': '''tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/(tick_df['ValueTrade']+1)''',

        's2ttran': '''tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/tick_df['ValueTrade'].sum()''',

        's2transtd': '''tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/tick_df['ValueTrade'].std()''',

        'amt': '''return tick_df['ValueTrade']''',

        'corrb2b1': '''res = pd.concat([tick_df['TotalBidQty'],tick_df['Buy1OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrpv': '''res = pd.concat([tick_df['ValueTrade'],tick_df['LastPx']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrb12s1': '''res = pd.concat([tick_df['Sell1OrderQty'],tick_df['Buy1OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrb2s': '''res = pd.concat([tick_df['TotalBidQty'],tick_df['TotalOfferQty']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrb2t': '''res = pd.concat([tick_df['TotalBidQty'],tick_df['VolumeTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrbp2bv': '''res = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['TotalBidQty']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrbp2t': '''res = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['ValueTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'corrb2tp': '''res = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['ValueTrade']/tick_df['VolumeTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]''',

        'rlength': '''res = len(tick_df)''',

        'abspchange': '''tick_df['factor'] = abs(tick_df['LastPx'] - tick_df['LastPx'].shift(1))
    tick_df['factor'] = tick_df['factor'] / (tick_df['pre_close'])''',

        'bp': '''tick_df['factor'] = tick_df['WeightedAvgBidPx']/(tick_df['pre_close'])''',

        'sp': '''tick_df['factor'] = tick_df['WeightedAvgOfferPx']/(tick_df['pre_close'])''',

        'b12b': '''tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'])''',

        'b1delb': '''tick_df['factor'] = (tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx'])''',

        's12s': '''tick_df['factor'] = (tick_df['Sell1Price'] - tick_df['WeightedAvgOfferPx'])/(tick_df['pre_close'])''',

        'b12s1': '''tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['Sell1Price'])/(tick_df['pre_close'])''',

        'b2s': '''tick_df['factor'] = (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgOfferPx']) / (tick_df['pre_close'])''',

        'tran2b': '''tick_df['factor'] = (tick_df['ValueTrade']/tick_df['VolumeTrade'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'])''',

        'vwap2p': '''tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    tick_df['factor'] = tick_df['vwap']/tick_df['LastPx']''',

        'syx1': '''tick_df['pcummax'] = tick_df['LastPx'].cummax()
    tick_df['pcummin'] = tick_df['LastPx'].cummin()
    tick_df['amp'] = tick_df['pcummax'] - tick_df['pcummin']
    tick_df['amp'] = tick_df['amp'].apply(lambda x: np.nan if abs(x)<0.0001 else x)
    tick_df['factor'] = (tick_df['pcummax'] - tick_df['LastPx'])/ tick_df['amp']''',

        'xyx1': '''tick_df['pcummax'] = tick_df['LastPx'].cummax()
    tick_df['pcummin'] = tick_df['LastPx'].cummin()
    tick_df['amp'] = tick_df['pcummax'] - tick_df['pcummin']
    tick_df['amp'] = tick_df['amp'].apply(lambda x: np.nan if abs(x)<0.0001 else x)
    tick_df['factor'] = (tick_df['LastPx'] - tick_df['pcummin'])/ tick_df['amp']''',

        'tpmin': '''tick_df = tick_df[tick_df['LastPx'] == tick_df['LastPx'].min()].head(1)
    res = tick_df['MDTime'].mean()''',

        'tvwap2pmin': '''tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    tick_df = tick_df[(tick_df['vwap']/tick_df['LastPx']) == (tick_df['vwap']/tick_df['LastPx']).min()].head(1)
    res = tick_df['MDTime'].mean()''',

        'ratiob': '''tick_df['factor'] = tick_df['TotalBidQty']/(tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])''',

        'ratiob2': '''tick_df['factor'] = tick_df['Buy2OrderQty']/tick_df['Buy1OrderQty'] - tick_df['Sell2OrderQty']/tick_df['Buy1OrderQty']''',

        'diffb12tran': '''tick_df['factor'] = (tick_df['Buy1OrderQty'] - tick_df['Buy1OrderQty'].shift(1)) / tick_df['VolumeTrade']''',

        'b1': '''tick_df['factor'] = tick_df['Buy1OrderQty']''',

        'pb1': '''tick_df['factor'] = tick_df['Buy1Price']/(tick_df['pre_close'])''',

        'b': '''tick_df['factor'] = tick_df['WeightedAvgBidPx'] * tick_df['TotalBidQty']1000''',

        'ratiob1thans1': '''tick_df['factor'] = np.sign(abs(tick_df['Sell1Price'] - tick_df['LastPx']) - abs(tick_df['Buy1Price'] - tick_df['LastPx']))''',

        'amt2newamt': '''tick_df['factor'] = tick_df['ValueTrade'] / (tick_df['ValueTrade'].tail(1))''',

        'bdiff': '''tick_df['factor'] = (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgBidPx'].shift(1)) / tick_df['pre_close']''',

        'sdiff': '''tick_df['factor'] = (tick_df['WeightedAvgOfferPx'] - tick_df['WeightedAvgOfferPx'].shift(1))/tick_df['pre_close']''',

        'pdiff': '''tick_df['factor'] = (tick_df['LastPx'] - tick_df['LastPx'].shift(1)) / tick_df['pre_close']''',

        'pv': '''tick_df['factor'] = (tick_df['LastPx']/tick_df['pre_close']-1) * tick_df['VolumeTrade']''',

        'pa': '''tick_df['factor'] = (tick_df['LastPx']/tick_df['pre_close']-1) * tick_df['ValueTrade']''',

        'pricev': '''if tick_df['ValueTrade'].sum() > 10:
        p = tick_df['ValueTrade'].sum() / tick_df['VolumeTrade'].sum()
    else:
        p = np.nan
    pre_close = tick_df['pre_close'].mean()
    if pre_close > 0.1:
        pct = p / pre_close - 1
        dt, ticker = tick_df.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        if zcz == 1:
            pct = pct / 2
        res = pct
    else:
        res = np.nan''',

        't': '''def inttime2deltamls(itime):
        mls = int(str(int(itime))[-3:])
        s = int(str(int(itime))[-5:-3])
        m = int(str(int(itime))[-7:-5])
        h = int(str(int(itime))[:-7])
        time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
        time_mls_930 = 9 * 3600 * 1000
        if int(itime) > 120000000:
            time_delta = time_mls - time_mls_930 - 5400000
        else:
            time_delta = time_mls - time_mls_930
        return time_delta
    tick_df['factor'] = tick_df['MDTime'].apply(lambda x : inttime2deltamls(x))''',

        'hp': '''tick_df['factor'] = tick_df['HighPx'] / tick_df['pre_close']''',

        'lpcummax': '''tick_df['factor'] = tick_df['LastPx'].cummax() / tick_df['pre_close']''',

        'h2l': '''tick_df['factor'] = (tick_df['HighPx'] - tick_df['LowPx']) / tick_df['pre_close']''',

        'h2l2': '''tick_df['factor'] = (tick_df['LastPx'].cummax() - tick_df['LastPx'].cummin()) / tick_df['pre_close']''',

        'hlmid': '''tick_df['factor'] = 0.5 * (tick_df['HighPx'] + tick_df['LowPx']) / tick_df['pre_close']''',

        'hlmid2lp': '''tick_df['factor'] = (0.5 * (tick_df['HighPx'] + tick_df['LowPx']) - tick_df['LastPx']) / tick_df['pre_close']''',

        'numtradesdiff': '''tick_df['factor'] = tick_df['NumTrades'] - tick_df['NumTrades'].shift(1).fillna(0)''',

        'bias5': '''tick_df = tick_df[tick_df['LastPx']>0]
    tick_df['ma5'] = tick_df['LastPx'].rolling(5,1).mean()
    tick_df['factor'] = (tick_df['LastPx'] - tick_df['ma5'].shift(1)) / tick_df['pre_close']''',

        'pctturn': '''tick_df['factor'] = (tick_df['LastPx'] / tick_df['pre_close'] - 1) * tick_df['VolumeTrade'] / tick_df['ff_shares']'''
    }
    res.append(dic7[x7])

    x9 = list_name[9]
    y9 = f'''res = f_calc_{x9}(tick_df['factor'])''' if 'res = ' not in dic7[x7] else ''
    res.append(y9)
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

    file_path = "/data/user/015585/fefactorframework-mercury/fast_factor/code/代码翻译/tmp/factor_ttick_sample.py"
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
    code_content = code_content.replace('qyh_ttick_sample', factor_name_logic)
    code_content = code_content.replace('ttick_sample', factor_name_logic)
    return code_content
def save_factor_file(save_path, code_content):
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(code_content)
    print(f"代码已保存到 {save_path}")

if __name__ == "__main__":
    df_factor_info = pd.read_csv('/data/user/015585/fefactorframework-mercury/fast_factor/code/europa/因子整合/res_f_name_import.csv')
    df_factor_info = df_factor_info[df_factor_info['factor_type'] == 'tick']
    factor_list = list(df_factor_info['name'])
    for factor_name in factor_list:
        code_content = generate_tick_factor_file(factor_name, factor_name)
        print(code_content)
        save_factor_file(f'/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/因子验证_ttick/factor/factor_{factor_name}.py', code_content)



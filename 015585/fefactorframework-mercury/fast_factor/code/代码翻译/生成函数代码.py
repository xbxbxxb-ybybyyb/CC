
def get_func_code(name):
    x = \
f'''
def f_pro_{name.replace('_','').lower()}(fin_df):
    fin_df['factor'] = fin_df['{name}']
    return fin_df
'''
    return x

def get_func_name(name):
    x = f"'{name.replace('_','').lower()}' : f_pro_{name.replace('_','').lower()},"
    return x
name_list = ['ACCT_RCV',
'OTH_RCV',
'PREPAY',
'INVENTORIES',
'TOT_CUR_ASSETS',
'LONG_TERM_EQY_INVEST',
'FIX_ASSETS',
'INTANG_ASSETS',
'DEFERRED_TAX_ASSETS',
'TOT_NON_CUR_ASSETS',
'TOT_ASSETS',
'ST_BORROW',
'ACCT_PAYABLE',
'EMPL_BEN_PAYABLE',
'TAXES_SURCHARGES_PAYABLE',
'TOT_CUR_LIAB',
'TOT_NON_CUR_LIAB',
'TOT_LIAB',
'CAP_RSRV',
'SURPLUS_RSRV',
'UNDISTRIBUTED_PROFIT',
'TOT_SHRHLDR_EQY_EXCL_MIN_INT',
'TOT_SHRHLDR_EQY_INCL_MIN_INT',
'TOT_LIAB_SHRHLDR_EQY',
'ACCOUNTS_RECEIVABLE_BILL',
'ACCOUNTS_PAYABLE',
'OTH_RCV_TOT',
'STM_BS_TOT',
'OTH_PAYABLE_TOT',]

for name in name_list:
    print(get_func_code(name))

for name in name_list:
    print(get_func_name(name))
from dataApi.getData import get_daily_1factor, get_quarter_1factor, get_single_quarter, get_ttm_quarter, get_qoq, \
    get_yoy, fill_quarter2daily_by_fixed_date, fill_quarter2daily_by_issue_date
from dataApi.stockList import trans_int2windcode
import pandas as pd
# from tqdm import tqdm

address = '/data/group/800442/800319/BigDataFactor/BasicFactor/'

# 1 Common Factors
ffmv = get_daily_1factor('free_float_shares') * get_daily_1factor('close')
mv = get_daily_1factor('mkt_cap_ard')
ev = get_daily_1factor('ev')

sales = get_ttm_quarter('tot_oper_rev')
asset = get_quarter_1factor('tot_assets')
equity = get_quarter_1factor('tot_shrhldr_eqy_incl_min_int')

# 2 Flow TTM Data
op = get_ttm_quarter('oper_profit')
impair = get_ttm_quarter('less_impair_loss_assets')
expense = get_ttm_quarter('less_selling_dist_exp').add(get_ttm_quarter('less_gerl_admin_exp'), fill_value=0).add(
    get_ttm_quarter('less_fin_exp'), fill_value=0).add(impair, fill_value=0)
gp = op.add(expense, fill_value=0)
nrlp = get_ttm_quarter('less_selling_dist_exp').sub(get_ttm_quarter('less_selling_dist_exp'), fill_value=0)
tp = op.add(nrlp, fill_value=0)
tax = get_ttm_quarter('inc_tax')
np = get_ttm_quarter('net_profit_incl_min_int_inc')

np0parent = get_ttm_quarter('net_profit_excl_min_int_inc')
np0minor = get_ttm_quarter('minority_int_inc')
np0other = get_ttm_quarter('other_compreh_inc')
np3nrlp = get_ttm_quarter('net_profit_after_ded_nr_lp')
np3nrlp0parent = np3nrlp * np0parent / np
ebit = get_ttm_quarter('ebit')
ebitda = get_ttm_quarter('ebitda')
dps2eps = get_ttm_quarter('s_fa_eps_diluted') / get_ttm_quarter('s_fa_eps_basic')

ocf = get_ttm_quarter('net_cash_flows_oper_act')
icf = get_ttm_quarter('net_cash_flows_inv_act')
fcf = get_ttm_quarter('net_cash_flows_fnc_act')
tcf = get_ttm_quarter('net_incr_cash_cash_equ')
capex = get_ttm_quarter('cash_pay_acq_const_fiolta').add(get_ttm_quarter('net_cash_pay_aquis_sobu'), fill_value=0)
eqyf = get_ttm_quarter('cash_recp_cap_contrib')
debf = get_ttm_quarter('cash_recp_borrow').add(get_ttm_quarter('proc_issue_bonds'), fill_value=0)

eq = ocf.sub(op, fill_value=0)

# 3 Flow Single Quarter Data
sales1q = get_single_quarter('tot_oper_rev')

op1q = get_single_quarter('oper_profit')
impair1q = get_single_quarter('less_impair_loss_assets')
expense1q = get_single_quarter('less_selling_dist_exp').add(get_single_quarter('less_gerl_admin_exp'), fill_value=0).add(
    get_single_quarter('less_fin_exp'), fill_value=0).add(impair1q, fill_value=0)
gp1q = op1q.add(expense1q, fill_value=0)
nrlp1q = get_single_quarter('less_selling_dist_exp').sub(get_single_quarter('less_selling_dist_exp'), fill_value=0)
tp1q = op1q.add(nrlp1q, fill_value=0)
tax1q = get_single_quarter('inc_tax')
np1q = get_single_quarter('net_profit_incl_min_int_inc')

np0parent1q = get_single_quarter('net_profit_excl_min_int_inc')
np0minor1q = get_single_quarter('minority_int_inc')
np0other1q = get_single_quarter('other_compreh_inc')
np3nrlp1q = get_single_quarter('net_profit_after_ded_nr_lp')
np3nrlp0parent1q = np3nrlp1q * np0parent1q / np1q
ebit1q = get_single_quarter('ebit')
ebitda1q = get_single_quarter('ebitda')
dps2eps1q = get_single_quarter('s_fa_eps_diluted') / get_single_quarter('s_fa_eps_basic')

ocf1q = get_single_quarter('net_cash_flows_oper_act')
icf1q = get_single_quarter('net_cash_flows_inv_act')
fcf1q = get_single_quarter('net_cash_flows_fnc_act')
tcf1q = get_single_quarter('net_incr_cash_cash_equ')
capex1q = get_single_quarter('cash_pay_acq_const_fiolta').add(get_single_quarter('net_cash_pay_aquis_sobu'), fill_value=0)
eqyf1q = get_single_quarter('cash_recp_cap_contrib')
debf1q = get_single_quarter('cash_recp_borrow').add(get_single_quarter('proc_issue_bonds'), fill_value=0)

eq1q = ocf1q.sub(op1q, fill_value=0)

# 4 Stock Data
asset0current = get_quarter_1factor('tot_cur_assets')
asset0fix = asset.sub(asset0current, fill_value=0)
asset0inv = get_quarter_1factor('inventories')
asset0ar = get_quarter_1factor('notes_rcv').add(get_quarter_1factor('acct_rcv'), fill_value=0).add(
    get_quarter_1factor('oth_rcv'), fill_value=0).add(get_quarter_1factor('prepay'), fill_value=0)

liab = get_quarter_1factor('tot_liab')
liab0current = get_quarter_1factor('tot_cur_liab')
liab0fix = liab.sub(liab0current, fill_value=0)
liab0ap = get_quarter_1factor('notes_payable').add(get_quarter_1factor('acct_payable'), fill_value=0).add(
    get_quarter_1factor('adv_from_cust'), fill_value=0)

eqy0capital = get_quarter_1factor('cap_stk').add(get_quarter_1factor('cap_rsrv'), fill_value=0)
eqy0rtdearn = get_quarter_1factor('surplus_rsrv').add(get_quarter_1factor('undistributed_profit_b'), fill_value=0).sub(
    get_quarter_1factor('less_tsy_stk'), fill_value=0)

wc = asset0current.sub(liab0current, fill_value=0)

# 5 Method One
base_list = [
 'asset',
 'asset0ar',
 'asset0current',
 'asset0fix',
 'asset0inv',
 'capex',
 'capex1q',
 'debf',
 'debf1q',
 'dps2eps',
 'dps2eps1q',
 'ebit',
 'ebit1q',
 'eq',
 'eq1q',
 'equity',
 'eqy0capital',
 'eqy0rtdearn',
 'eqyf',
 'eqyf1q',
 'expense',
 'expense1q',
 'fcf',
 'fcf1q',
 'gp',
 'gp1q',
 'icf',
 'icf1q',
 'impair',
 'impair1q',
 'liab',
 'liab0ap',
 'liab0current',
 'liab0fix',
 'np0minor',
 'np0minor1q',
 'np0other',
 'np0other1q',
 'np0parent',
 'np0parent1q',
 'np1q',
 'np3nrlp',
 'np3nrlp0parent',
 'np3nrlp0parent1q',
 'np3nrlp1q',
 'ocf',
 'ocf1q',
 'op',
 'op1q',
 'sales',
 'sales1q',
 'tax',
 'tax1q',
 'tcf',
 'tcf1q',
 'tp',
 'tp1q',
 'wc',
]

def trans_bd_df(df, address):

    df1 = df.loc[20140630 : 20200630]
    df1.index = df1.index.map(str)
    df1.columns = df1.columns.map(trans_int2windcode)
    df1.to_pickle(address)

for x in tqdm(base_list):

    trans_bd_df(fill_quarter2daily_by_fixed_date(eval(x) / asset), '%s%s2asset8fix.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_fixed_date(eval(x) / equity), '%s%s2equity8fix.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_fixed_date(eval(x) / sales), '%s%s2sales8fix.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(eval(x) / asset), '%s%s2asset8issue.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(eval(x) / equity), '%s%s2equity8issue.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(eval(x) / sales), '%s%s2sales8issue.pkl' % (address, x))

# 6 Method Two
for x in tqdm(base_list):

    trans_bd_df(fill_quarter2daily_by_fixed_date(get_yoy(eval(x))), '%s%s8yoy8fix.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(get_yoy(eval(x))), '%s%s8yoy8issue.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_fixed_date(get_qoq(eval(x))), '%s%s8qoq8fix.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(get_qoq(eval(x))), '%s%s8qoq8issue.pkl' % (address, x))

# 7 Method Three
gp3op8yoy = gp * get_yoy(op)
op3op8yoy = op * get_yoy(op)
tp3op8yoy = tp * get_yoy(op)
gp3op1q8yoy = gp * get_yoy(op1q)
op3op1q8yoy = op * get_yoy(op1q)
tp3op1q8yoy = tp * get_yoy(op1q)

base_list += ['gp3op8yoy', 'op3op8yoy', 'tp3op8yoy', 'gp3op1q8yoy', 'op3op1q8yoy', 'tp3op1q8yoy']

for x in tqdm(base_list):

    trans_bd_df(fill_quarter2daily_by_fixed_date(eval(x)) / mv, '%s%s8fix2mv.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_fixed_date(eval(x)) / ffmv, '%s%s8fix2ffmv.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_fixed_date(eval(x)) / ev, '%s%s8fix2ev.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(eval(x)) / mv, '%s%s8issue2mv.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(eval(x)) / ffmv, '%s%s8issue2ffmv.pkl' % (address, x))
    trans_bd_df(fill_quarter2daily_by_issue_date(eval(x)) / ev, '%s%s8issue2ev.pkl' % (address, x))


#special select
special_road = address + 'SpecialSelect/'
special_pos_list = [
    'ebit1q2asset8fix',
    'np3nrlp1q8issue2mv',
    'np0parent1q8issue2mv',
    'np3nrlp1q2equity8issue',
    'np3nrlp0parent1q8issue2mv',
    'np3nrlp0parent1q2equity8issue',
    'ebit1q2equity8fix',
    'np1q8issue2mv',
    'ebit1q2asset8issue',
    'np1q2equity8issue',
    'np0parent1q2equity8issue',
    'np3nrlp1q2asset8issue',
    'op1q8issue2mv',
    'np0parent1q8issue2ffmv',
    'np3nrlp1q8issue2ffmv',
    'op1q2equity8issue',
    'op1q2asset8issue',
    'np1q8issue2ffmv',
    'np0parent1q2asset8issue',
    'op1q8issue2ffmv',
    'np1q2asset8issue',
    'ebit1q8fix2mv',
    'np3nrlp0parent1q8issue2ffmv',
    'np3nrlp1q8fix2mv',
    'np3nrlp0parent1q2asset8issue',
    'ebit2sales8fix',
    'op2equity8issue',
    'np0parent1q8fix2mv',
    'np3nrlp0parent1q8fix2mv',
    'np3nrlp2equity8issue',
    'gp1q2asset8issue',
    'op1q8fix2mv',
    'ocf2asset8issue',
    'tax1q8issue2mv',
    'tax1q2asset8fix',
    'np3nrlp0parent1q2equity8fix',
    'np1q8fix2mv',
    'np3nrlp1q2equity8fix',
    'np3nrlp1q2asset8fix',
    'ebit1q8fix2ffmv',
    'np3nrlp1q8fix2ffmv',
    'np3nrlp0parent2equity8issue',
    'op1q2equity8fix',
    'tax1q2asset8issue',
    'gp1q8issue2ffmv',
    'np3nrlp0parent1q2asset8fix',
    'op1q2asset8fix',
    'np3nrlp8qoq8issue',
    'eqy0rtdearn2equity8issue',
    'tax1q8issue2ffmv',
    'ocf2asset8fix',
    'gp1q8issue2mv',
    'op2equity8fix',
    'np3nrlp2equity8fix',
    'ebit1q2equity8issue',
    'eqy0rtdearn8issue2mv',
    'np3nrlp0parent1q8fix2ffmv',
    'op2asset8issue',
    'gp1q2equity8issue',
    'np3nrlp0parent2equity8fix',
    'eqy0rtdearn8fix2mv',
    'ebit1q8issue2ffmv',
    'tax1q2equity8issue',
    'np0parent2equity8issue',
    'np3nrlp8issue2mv',
    'equity8issue2mv',
    'ebit1q8issue2mv',
    'gp1q2equity8fix',
    'np3nrlp2asset8issue',
    'gp8issue2mv',
    'gp1q8fix2ffmv',
    'np0parent1q8fix2ffmv',
    'np3nrlp8issue2ffmv',
    'np1q2equity8fix',
    'np3nrlp0parent8issue2mv',
    'eqy0rtdearn8issue2ffmv',
    'np0parent1q2equity8fix',
    'op8issue2mv',
    'gp8issue2ffmv',
    'op1q8fix2ffmv',
    'np3nrlp0parent8issue2ffmv',
    'np0parent8issue2mv',
    'eqy0rtdearn8fix2ffmv',
    'tax1q8fix2mv',
    'gp1q8fix2mv',
    'np1q8fix2ffmv',
    'ocf8issue2mv',
    'tax1q2equity8fix',
    'np3nrlp0parent8qoq8issue',
    'ocf8issue2ffmv',
    'np0parent8issue2ffmv',
    'eqy0rtdearn2equity8fix',
    'np0parent2asset8issue',
    'tax1q8fix2ffmv',
    'np3nrlp0parent2asset8issue',
    'ebit2asset8issue',
    'np0parent2equity8fix',
    'np3nrlp2asset8fix',
    'op8issue2ffmv',
    'np3nrlp8fix2ffmv',
    'np3nrlp8fix2mv',
    'ocf1q8issue2ffmv',
    'gp8fix2ffmv',
    'ocf1q2asset8fix',
    'ocf8fix2mv',
    'ocf1q8fix2ffmv',
    'np0parent8fix2ffmv',
    'ocf2equity8issue',
    'np3nrlp0parent2asset8fix',
    'tax8issue2ffmv',
    'expense8issue2ffmv',
    'ocf2equity8fix',
    'op8qoq8issue',
    'tax8issue2mv',
    'gp8fix2mv',
    'np3nrlp0parent8fix2ffmv',
    'op8fix2ffmv',
    'np0parent8fix2mv',
    'ebit1q2sales8fix',
    'np3nrlp0parent8fix2mv',
    'expense8issue2mv',
    'op8fix2mv',
    'expense8fix2ffmv',
    'ocf8fix2ffmv',
    'np0parent8qoq8issue',
    'gp2equity8issue',
    'ocf1q8issue2mv',
    'expense8fix2mv',
    'expense1q8fix2ffmv',
    'expense1q8fix2mv',
    'tax8fix2ffmv',
    'gp8qoq8issue',
    'tax8fix2mv',
    'expense1q8issue2mv',
    'eq8fix2mv',
    'ocf1q8fix2mv',
    'tax2asset8fix',
    'expense1q8issue2ffmv',
    'ocf1q2asset8issue',
    'np3nrlp8qoq8fix',
    'np0minor1q8fix2mv',
    'tax2equity8issue',
    'ocf1q2equity8fix',
    'np3nrlp0parent1q8yoy8issue',
    'np0minor1q8issue2ffmv',
    'np3nrlp1q8yoy8issue',
    'eq8issue2mv',
    'eq8issue2ffmv',
    'capex8issue2ffmv',
    'sales1q8fix2mv',
    'sales1q8issue2ffmv',
    'tax2equity8fix',
    'eqy0rtdearn2asset8fix',
    'sales1q8issue2mv',
    'ebit1q2sales8issue',
    'op1q2sales8issue',
    'sales1q2sales8issue',
    'sales1q8fix2ffmv',
    'np3nrlp0parent8qoq8fix',
    'capex1q8issue2mv',
    'capex8fix2ffmv',
    'np0minor8fix2mv',
    'ebit8issue2ffmv',
    'capex8issue2mv',
    'tax1q2sales8issue',
    'sales8issue2mv',
    'sales8issue2ffmv',
    'capex1q2asset8fix',
    'gp2equity8fix',
    'np3nrlp1q2sales8issue',
    'np3nrlp0parent1q2sales8fix',
    'equity8qoq8issue',
    'eq8fix2ffmv',
    'sales8fix2mv',
    'liab0ap8issue2mv',
    'np3nrlp1q2sales8fix',
    'np3nrlp0parent1q2sales8issue',
    'np0parent8qoq8fix',
    'np0parent1q2sales8issue',
    'ocf1q2equity8issue',
    'capex1q8issue2ffmv',
    'np1q2sales8issue',
    'sales8qoq8issue',
    'gp1q2sales8issue',
    'tax1q2sales8fix',
    'np0minor8fix2ffmv',
    'capex1q8fix2mv',
    'tcf8fix2mv',
    'sales1q2asset8fix',
    'tcf8issue2mv',
    'sales1q2asset8issue',
    'ebit1q8yoy8fix',
    'liab8qoq8issue',
    'tax8qoq8fix',
    'asset8qoq8issue',
    'liab0current8qoq8issue',
    'capex2equity8fix',
    'tcf8fix2ffmv',
    'sales1q2sales8fix',
    'expense1q2equity8issue',
    'ebit8qoq8issue',
    'ebit1q8qoq8issue',
    'sales1q2equity8issue',
    'eq1q8fix2mv',
    'capex1q8fix2ffmv',
    'np0minor1q2sales8fix',
    'ebit8issue2mv',
    'tax8qoq8issue',
    'liab0ap8qoq8issue',
    'ocf1q2sales8fix',
    'asset0current8qoq8fix',
]

special_neg_list = [
    'icf1q8fix2mv',
    'icf1q8fix2ffmv',
    'icf1q2equity8fix',
    'debf1q2sales8issue',
    'debf2sales8fix',
    'icf1q2asset8fix',
    'icf8issue2mv',
    'debf2sales8issue',
    'icf8fix2ffmv',
    'asset0current2sales8issue',
    'dps2eps2equity8fix',
    'dps2eps1q2equity8fix',
    'eqy0capital2asset8issue',
    'expense8yoy8fix',
    'dps2eps2equity8issue',
    'expense8yoy8issue',
    'dps2eps1q2equity8issue',
    'eqy0capital2asset8fix',
    'asset0ar2sales8issue',
    'dps2eps2sales8fix',
    'eqy0capital2equity8fix',
    'dps2eps2sales8issue',
    'asset0ar2sales8fix',
    'eqy0capital2equity8issue',
]

for name in special_pos_list:
    pd.read_pickle('%s%s.pkl' % (address, name)).to_pickle('%s%s.pkl' % (special_road, name))

for name in special_neg_list:
    pd.read_pickle('%s%s.pkl' % (address, name)).to_pickle('%s%s.pkl' % (special_road, name))


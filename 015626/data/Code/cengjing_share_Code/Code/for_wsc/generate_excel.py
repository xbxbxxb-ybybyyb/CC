account_number = {'IC': 5161001, 'IF': 5160501, 'IH': 5162003}
security_account = '00000004'
afternoon_trade_direction = 'buy_open'
morning_trade_direction = 'sell_close'
afternoon_system_start_time = datetime.time(14,54)
afternoon_system_end_time = datetime.time(14,59)
morning_system_start_time = datetime.time(9,30)
morning_system_end_time = datetime.time(9,35)
num_per_order = 1
max_contracts_total = 500
max_contracts_perseconds = 50



print('-' * 60)
# dump factor
trade_date = inst.__trade_date__.strftime('%Y%m%d')
# dump trading plan
trading_plan_savepath = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')))
if not os.path.exists(trading_plan_savepath):
    os.makedirs(trading_plan_savepath)
generate_para_excel(trade_date, trading_plan_1_0.reset_index())
trading_plan_1_0.to_csv(os.path.join(trading_plan_savepath, '%s_%s_1_0.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))
trading_plan_2_0.to_csv(os.path.join(trading_plan_savepath, '%s_%s_2_0.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))
# dump factor
factor_savepath = os.path.join(inst.savepath, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')))
if not os.path.exists(factor_savepath):
    os.makedirs(factor_savepath)
factor_score.to_csv(os.path.join(factor_savepath, '%s_%s.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))



def generate_para_excel(trade_date, trading_plan):
    plan = trading_plan[['Contract','Contract_Num','Account_Num']]
    plan['Contract'] = plan.Contract.apply(lambda x:x+'.CF')
    plan = plan.rename(columns = {'Contract':'合约代码','Contract_Num':'合约张数','Account_Num':'买入交易账户'})
    plan = plan[plan['合约张数'] > 0]
    if len(plan) == 0:
        print('today has no trading plan!')
        lm.sendMessage('today has no trading plan!')
        return
    plan['买入交易账户'] = plan['买入交易账户'].apply(lambda x:str(x)+'_ff')
    plan['卖出交易账户'] = plan['买入交易账户']
    plan['买卖方向'] = afternoon_trade_direction
    plan['下单开始时间'] = afternoon_system_start_time.strftime('%H:%M:%S')
    plan['下单结束时间'] = afternoon_system_end_time.strftime('%H:%M:%S')
    plan['每次下单数量'] = num_per_order
    plan['买入证券账户'] = security_account
    plan['卖出证券账户'] = security_account
    plan = plan[['合约代码', '合约张数', '买卖方向', '下单开始时间', '下单结束时间', '每次下单数量', '买入交易账户', '卖出交易账户', '买入证券账户', '卖出证券账户']]

    InitialBasicParam = pd.DataFrame([trade_date, max_contracts_total, max_contracts_perseconds], index = ['交易日','当日所有合约开仓数量上限','过去1s所有合约开仓成交数量与挂单数量上限']).T

    writer = pd.ExcelWriter(os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'Diamond_%s_afternoon.xlsx' % (trade_date)))
    InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
    plan.to_excel(writer, '交易参数列表', index = False)
    writer.save()
    lm.sendMessage('para excel generate done!')
    
    # generate morning sell close excel
    next_trade_date = udt.get_trading_day_offset(trade_date,1)[0].strftime('%Y%m%d')
    next_InitialBasicParam = InitialBasicParam.copy()
    next_InitialBasicParam['交易日'] = next_trade_date
    
    next_plan = plan.copy()
    next_plan['买卖方向'] = morning_trade_direction
    next_plan['下单开始时间'] = morning_system_start_time.strftime('%H:%M:%S')
    next_plan['下单结束时间'] = morning_system_end_time.strftime('%H:%M:%S')
    next_trading_plan_savepath = os.path.join(trading_plan_path, '%s_%s' % (next_trade_date, trade_stop_time.strftime('%H%M')))
    if not os.path.exists(next_trading_plan_savepath):
        os.makedirs(next_trading_plan_savepath)
    writer = pd.ExcelWriter(os.path.join(next_trading_plan_savepath, 'Diamond_%s_morning.xlsx' % (next_trade_date)))
    next_InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
    next_plan.to_excel(writer, '交易参数列表', index = False)
    writer.save()
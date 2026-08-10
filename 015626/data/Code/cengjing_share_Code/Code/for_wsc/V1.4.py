# naming_config
min_order_interval = 3

# factor_generator
InitialBasicParam = pd.DataFrame([trade_date, max_contracts_total, max_contracts_perseconds, min_order_interval], index = ['交易日','当日所有合约开仓数量上限','过去1s所有合约开仓成交数量与挂单数量上限','最小下单间隔']).T

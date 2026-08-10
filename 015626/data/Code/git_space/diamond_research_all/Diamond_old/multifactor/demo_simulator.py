# normal usage


# normal usage
import multifactor.simulator.stock as sim
import cvxpy as cvx

h5_path = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
trader = sim.Trader()
trader.logger_mode = 'w'
trader.oxidant('/data/user/013160/test.ini')
trader.md_func = sim.md_func
trader.opt_func = sim.opt_func(h5_path)
trader.verbose = False
trader.run()
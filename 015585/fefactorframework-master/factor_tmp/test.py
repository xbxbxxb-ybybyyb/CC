# 初始化参数
spot_price = 248  # 标的价格
strike_price = 230  # 行权价格
risk_free_rate = 0.05261  # 年化无风险利率
time_to_maturity = (0 + 1 - 0.5/6.5)/365  # 期权到期时间（以年为单位）,futu“距离天数”+1 - 过掉的小时数/6.5
volatility = 0.8428  # 波动率
import numpy as np
from scipy.stats import norm
# 计算期权价值
def calc_price(spot_price,strike_price,risk_free_rate,time_to_maturity,volatility):
    d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_maturity) / (volatility * np.sqrt(time_to_maturity))
    d2 = d1 - volatility * np.sqrt(time_to_maturity)

    call_price = spot_price * norm.cdf(d1) - strike_price * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
    put_price = strike_price * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) - spot_price * norm.cdf(-d1)
    return '看涨价格：{}，看跌价格：{}'.format(call_price,put_price)
print(
calc_price(
spot_price = 247,  # 标的价格
strike_price = 260,  # 行权价格
risk_free_rate = 0.05261,  # 年化无风险利率
time_to_maturity = (0 + 1 - 1/6.5)/365,  # 期权到期时间（以年为单位）,futu“距离天数”+1 - 过掉的小时数/6.5
volatility = 0.75  # 波动率
)
)
'''
1、

'''
import numpy as np
from scipy.stats import norm

def black_scholes(S0, K, r, sigma, T, put_call='call'):
    """
    计算欧式期权价格（看涨或看跌）

    参数:
    S0 (float): 标的资产当前价格
    K (float): 行权价
    r (float): 无风险利率（年化）
    sigma (float): 波动率（年化）
    T (float): 到期时间（以年为单位）
    put_call (str): 期权类型，'call' 表示看涨，'put' 表示看跌

    返回:
    float: 期权价格
    """
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if put_call == 'call':
        price = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif put_call == 'put':
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)
    else:
        raise ValueError("put_call 必须为 'call' 或 'put'")

    return price

black_scholes(402.18, 395, 0.042082, 0.485255, (3)/365, 'put')

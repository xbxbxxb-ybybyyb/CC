import pandas as pd
suffix = '_zz500'
df = pd.Dataframe()


# ws
factor = factor * df['weight' + suffix]
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# s
factor = factor[df['weight_boolean' + suffix]]
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# vs
factor = factor * df['stk_volatility' + suffix]
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# sc
factor = factor * df['stk_index_corr' + suffix]
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# as
a = df['amount' + suffix][df['weight_boolean' + suffix]]
factor = factor * a
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# ts
t = df['turnover' + suffix][df['weight_boolean' + suffix]]
factor = factor * t
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# ar
a = df['amount' + suffix][df['weight_boolean' + suffix]]
ar = (2 * a.rank(axis=1, pct=True) - 1)
factor = factor * ar
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# tr
t = df['turnover_zz500' + suffix][df['weight_boolean' + suffix]]
tr = (2 * t.rank(axis=1, pct=True) - 1)
factor = factor * tr
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# wr
wr = (2 * df['weight'+suffix].rank(axis=1, pct=True) - 1)
factor = factor * wr
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# vr
vr = (2 * df['stk_volatility'+suffix].rank(axis=1, pct=True) - 1)
factor = factor * vr
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]

# cr
cr = (2 * df['stk_index_corr'+suffix].rank(axis=1, pct=True) - 1)
factor = factor * cr
factor = factor.sum(axis = 1).to_frame()

factor = ts_rank_bk(factor, )
factor = ts_mean(factor, )
factor = rolling_normalize(factor, 5 * 242)
factor.columns = [columnname]
import pandas as pd

df = pd.DataFrame({'pct':[i for i in range (100)]})
df['20_mean'] = df['pct'].rolling(20).mean()

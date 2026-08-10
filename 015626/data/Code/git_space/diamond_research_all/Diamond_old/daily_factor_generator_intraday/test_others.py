import os
import pandas as pd

ticker_list = ['IC2105', 'IF2105', 'IH2105']
position_list = [12.0, 10.0, 15.0]
df_for_cyx = pd.DataFrame([ticker_list, [str(int(i))+ '张' for i in position_list], [str(int(240/i)) + '秒' for i in position_list]]).T
print(position_list)
print('\n')
print(df_for_cyx)
import numpy as np
import pandas as pd
from copulas.multivariate import GaussianMultivariate
# 设置随机种子
np.random.seed(0)
copula = GaussianMultivariate()
a = pd.DataFrame({'a':[1,2,3,4,5,6],'b':[2,4,5,7,2,1]})
copula.fit(a)
df_copula = copula.sample(10)
print(df_copula)
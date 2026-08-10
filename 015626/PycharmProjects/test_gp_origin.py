import numpy as np
import pandas as pd
import pickle
from gplearn_super.genetic import SymbolicTransformer, SymbolicRegressor
from multifactor.IO import IO
pd.set_option('display.max_columns', None)
from gplearn_super.utils import *


origindata = IO.read_data([20160101,20170101], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
origindata = origindata.xs('IC.CFE', level = 1)
origindata = origindata.drop(['WIND_CODE','trading_day','EXCHANGE'], axis = 1)

origindata['pct'] = origindata['close'].pct_change(periods=1).shift(-1)
origindata = origindata.fillna(method='ffill')
fields = list(set(origindata.columns.tolist()) - set(['pct']))
data = origindata[fields].values
target = origindata['pct'].values

test_size = 0.2
test_num = int(len(data)*test_size)
X_train = data[:-test_num]
X_test = data[-test_num:]
y_train = np.nan_to_num(target[:-test_num])
y_test = np.nan_to_num(target[-test_num:])

init_function = ['add', 'sub', 'mul', 'div', 'sqrt', 'log', 'abs', 'neg']

generations = 6
function_set = init_function
# metric = my_metric
population_size = 1000
random_state = 0
n_components = 10
hall_of_fame = 100
est_gp = SymbolicTransformer(function_set=function_set,
                             generations=generations,
                             metric='pearson',
                             population_size=population_size,
                             tournament_size=100,
                             random_state=random_state,
                             n_components = n_components,
                             hall_of_fame = hall_of_fame,
                             n_jobs=23)
est_gp.fit(X_train, y_train)

# 将模型保存到本地
with open('gp_model.pkl', 'wb') as f:
    pickle.dump(est_gp, f)

# 获取较优的表达式
namedict = {}
for i in range(len(fields)):
    namedict['X' + str(i)] = fields[i]

best_programs = est_gp._best_programs
best_programs_dict = {}

for p in best_programs:
    factor_name = 'alpha_' + str(best_programs.index(p) + 1)
    expresstion = str(p)
    for key in namedict.keys():
        expresstion = expresstion.replace(key, namedict[key])
    best_programs_dict[factor_name] = {'fitness': p.fitness_, 'expression': expresstion, 'depth': p.depth_,
                                       'length': p.length_}

best_programs_dict = pd.DataFrame(best_programs_dict).T
best_programs_dict = best_programs_dict.sort_values(by='fitness')
best_programs_dict.to_csv('./test_gp.csv')
print(best_programs_dict)
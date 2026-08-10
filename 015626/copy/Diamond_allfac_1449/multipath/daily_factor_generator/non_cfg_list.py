import sys
sys.path.insert(4, '/data/user/017024/share/overnight/factors/overnight_prod_20210127_76/ic/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import importlib
import warnings
warnings.filterwarnings('ignore')

from factor_generator_complex import FactorGeneratorComplex




fs = [f for f in os.listdir('/data/user/017024/share/overnight/factors/overnight_prod_20210127_76/ic/') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])        
subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
non_cfg_list = []
for i in subclass_list_cfg:
    non_cfg_list.append(str(i).split("'")[-2].split('.')[0])
print(non_cfg_list)





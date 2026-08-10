from factor_generator_complex import FactorGeneratorComplex
import warnings
warnings.filterwarnings('ignore')

import os, importlib
fs = [f for f in os.listdir('.') if f.endswith('.py')]
for f in fs:
    if 'CC' in f:
        importlib.import_module(f[:-3])

if __name__ == '__main__':
    FactorGeneratorComplex().prepare_hot_data(20190101, 20200901)
    print('data done')

    # subclass_list = FactorGeneratorComplex.__subclasses__()

    for subclass in FactorGeneratorComplex.__subclasses__():
        print(subclass().__class__.__name__)
        inst = subclass()
        inst.__callback__(20170101, 20200901)


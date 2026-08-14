# coding: utf-8
# Author：fengchi863
# Date ：2021/3/29 11:24

from hyperopt import fmin, tpe, Trials
from numpy.random import RandomState
import warnings
warnings.filterwarnings("ignore")

def hyperopt_wrapper(hyperopt_objective, params_space, max_evals=150, algo=tpe.suggest, verbose=False):
    trials = Trials()
    best = fmin(
        hyperopt_objective,
        space=params_space,
        max_evals=max_evals,
        algo=algo,
        trials=trials,
        rstate=RandomState(2021)
    )
    if verbose:
        for t in trials.trials:
            print('iter %d: loss: %.4g' % (t['tid'], t['result']['loss']))
        print('best', best)
    return best
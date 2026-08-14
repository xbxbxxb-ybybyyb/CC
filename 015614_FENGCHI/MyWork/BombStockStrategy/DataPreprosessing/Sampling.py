# coding: utf-8
# Author：fengchi863
# Date ：2021/11/16 14:26

import numpy as np


class Sampling:
    def __init__(self):
        pass

    def sample(self, train_samples, test_samples, params):
        train = train_samples.copy()
        test = test_samples.copy()
        # 剔除掉前后有停牌的个股，因为label中这部分计算出来是nan
        train_samples = train[~np.isnan(train['label'])]
        predict_samples = test[~np.isnan(test['label'])]

        train_samples = train_samples.query(f'LenZtMin > %d' % params['min_zt_time'])
        predict_samples = predict_samples.query(f'LenZtMin > %d' % params['min_zt_time'])
        train_samples = train_samples.query(f'Close > %d' % params['min_close'])
        predict_samples = predict_samples.query(f'Close > %d' % params['min_close'])
        train_samples = train_samples.query(f'UpperShadowPct > %d' % params['max_upper_shadow_pct'])
        predict_samples = predict_samples.query(f'UpperShadowPct > %d' % params['max_upper_shadow_pct'])
        train_samples = train_samples.query(f'HighDownPct > %d' % params['min_high_down_pct'])
        predict_samples = predict_samples.query(f'HighDownPct > %d' % params['min_high_down_pct'])
        train_samples = train_samples.query(f'OpenVsClose == 1')
        predict_samples = predict_samples.query(f'OpenVsClose == 1')

        return train_samples, predict_samples


Sampling = Sampling()

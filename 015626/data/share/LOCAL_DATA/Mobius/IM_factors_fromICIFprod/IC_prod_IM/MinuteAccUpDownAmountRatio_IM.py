import numpy as np
from future_factor import FutureFactor


class MinuteAccUpDownAmountRatio_IM(FutureFactor):

    def __init__(self):
        super().__init__()
        self.acc_up_amount = 0
        self.acc_down_amount = 0
        self.acc_up_amount_list = []
        self.acc_down_amount_list = []

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH': ['close', 'amount']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):

        close = data['close_000852.SH'].values
        amount = data['amount_000852.SH'].values

        if len(self.acc_up_amount_list) == 0:
            for i in range(15):
                idx = -(15-i)
                if close[idx] < close[idx-1]:
                    self.acc_up_amount = amount[idx]
                    self.acc_down_amount += amount[idx]
                else:
                    self.acc_up_amount += amount[idx]
                    self.acc_down_amount = amount[idx]

                self.acc_up_amount_list.append(self.acc_up_amount)
                self.acc_down_amount_list.append(self.acc_down_amount)
        else:

            if close[-1] < close[-2]:
                self.acc_up_amount = amount[-1]
                self.acc_down_amount += amount[-1]
            else:
                self.acc_up_amount += amount[-1]
                self.acc_down_amount = amount[-1]

            self.acc_up_amount_list.append(self.acc_up_amount)
            self.acc_down_amount_list.append(self.acc_down_amount)

        ratio_array = np.array(self.acc_up_amount_list[-15:]) / np.array(self.acc_down_amount_list[-15:])
        ratio_array[np.isinf(ratio_array)] = 1
        factor_value = np.nanmean(ratio_array)

        return factor_value
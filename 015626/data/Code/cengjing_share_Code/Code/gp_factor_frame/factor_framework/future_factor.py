class FutureFactor(object):

    days_past = 0
    data_dict = dict()
    data_type = 'Future'
    instrument_type = 'main'
    ts_lookback = 20

    def __init__(self):
        self.factor_name = self.__class__.__name__


    def calculate(self, data):

        factor_result = None

        return factor_result


class FutureFactor(object):

    days_past = 0
    required_columns = ['close', 'volume', 'low']
    instrument_type = 'main'
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'

    def __init__(self):
        self.factor_name = self.__class__.__name__

    def calculate(self, data):

        factor_result = None

        return factor_result


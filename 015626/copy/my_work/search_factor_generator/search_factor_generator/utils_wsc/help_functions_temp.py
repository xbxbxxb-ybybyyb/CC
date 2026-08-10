import pandas as pd


class DatetimeConvert:
    """
    一系列datetime格式之间的转换函数
    """

    def __init__(self, datetime_input):
        """
        类初始化函数
        :param datetime_input: {pd.Times}
            输入的datetime格式
        """
        self.datetime_input = datetime_input

    def timestamp_to_int(self):
        assert isinstance(self.datetime_input, pd.Timestamp), 'The input format does not meet the requirements.'
        datetime_output = int(
            self.datetime_input.year * 1e4 + self.datetime_input.month * 100 + self.datetime_input.day)
        return datetime_output

    def timestamp_to_str(self):
        assert isinstance(self.datetime_input, pd.Timestamp), 'The input format does not meet the requirements.'
        datetime_output = str(
            int(self.datetime_input.year * 1e4 + self.datetime_input.month * 100 + self.datetime_input.day))
        return datetime_output


def datetime_convert(datetime_input, type='str'):
    """
    将输入的datetime格式输出成需要的datetime格式
    :param datetime_input: int, str or datime.Timestamp
        输入的datetime
    :param type: str
        希望得到的输出datetime格式
    :return: int, str or pd.Timestamp
        输出的datetime
    """
    assert isinstance(datetime_input, int) or isinstance(datetime_input, str) or isinstance(datetime_input,
                                                                                            pd.Timestamp)
    if isinstance(datetime_input, int):
        if type == str:
            datetime_output = str(datetime_input)

    return datetime_output

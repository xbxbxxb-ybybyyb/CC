from IO import IO
import datetime as dt
import os
from pathlib import Path
from collections import Iterable
import time
import sys

class Semaphore:
    def __init__(self, flag_dir=r'Z:\warehouse\prod\LOCAL_DATA\FLAG'):
        self._flag_dir = flag_dir

    def chflagdir(self, flag_new_dir):
        self._flag_dir = flag_new_dir

    def check(self, ftype, dt):
        if os.path.exists(self._flag(ftype, dt)):
            return True
        else:
            return False

    def _flag(self, ftype, dt, flag = None):
        if flag is None:
            flag = self._flag_dir
        dt = IO.str_date_parser(dt).strftime('%Y%m%d')
        flag_str = dt + '_' + ftype.upper() + '.success'
        return os.path.join(flag, dt, flag_str)

    def wait(self, ftypes, dt, gap=600, expiration=None):
        assert not isinstance(ftypes, str) and isinstance(ftypes, Iterable)
        assert isinstance(gap, int)
        if expiration is not None:
            isinstance(expiration, int)
        total_seconds = 0
        while True:
            check_list = list()
            for ftype in ftypes:
                check_list.append(self.check(ftype, dt))
            if all(check_list):
                break
            print('check flag failed, wait for %d seconds to retry' % gap)
            time.sleep(gap)
            total_seconds += gap
            if expiration is not None and total_seconds >= expiration:
                sys.exit()

    def touch(self, ftype, dt):
        _file = self._flag(ftype, dt)
        if not os.path.exists(os.path.dirname(_file)):
            os.makedirs(os.path.dirname(_file))
        if os.path.exists(_file):
            os.remove(_file)
        Path(_file).touch(exist_ok=False)


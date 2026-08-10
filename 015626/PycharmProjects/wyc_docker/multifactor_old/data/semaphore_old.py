from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.common as ut
import multifactor.utility.dt as tdt
import subprocess
from multiprocessing import Process
import datetime as dt
import os
from pathlib import Path
from collections import Iterable
import time
import sys

flag_root_path = '/data/user/015626/data/share/LOCAL_DATA/temp_cronb'
private_log_path = '/data/user/015626/data/share/LOCAL_DATA/temp_cronb'
public_flag_root_path = '/data/user/015626/data/share/LOCAL_DATA/temp_cronb'
private_python_path = None

class Semaphore:
    def __init__(self, flag_dir=public_flag_root_path):
        self._flag_dir = flag_dir

    def check(self, ftype, dt, suffix='.success'):
        if os.path.exists(self._flag(ftype, dt, suffix)):
            return True
        else:
            return False

    def _flag(self, ftype, dt, suffix='.success'):
        dt = IO.str_date_parser(dt).strftime('%Y%m%d')
        flag_str = dt + '_' + ftype.upper() + suffix
        return os.path.join(self._flag_dir, dt, flag_str)

    def wait(self, ftypes, dt, gap=600, expiration=None,
             _success_suffix='.success', _failed_suffix='.failed'):
        assert not isinstance(ftypes, str) and isinstance(ftypes, Iterable)
        assert isinstance(gap, int)
        if expiration is not None:
            isinstance(expiration, int)
        total_seconds = 0
        while True:
            check_list = list()
            failed_list = list()
            for ftype in ftypes:
                check_list.append(self.check(ftype, dt, suffix=_success_suffix))
                failed_list.append(self.check(ftype, dt, suffix=_failed_suffix))
            if all(check_list):
                return True
            if any(failed_list):
                return False
            print('check flag failed, wait for %d seconds to retry' % gap)
            time.sleep(gap)
            total_seconds += gap
            if expiration is not None and total_seconds >= expiration:
                return False

    def touch(self, ftype, dt, suffix='.success'):
        _file = self._flag(ftype, dt, suffix)
        if not os.path.exists(os.path.dirname(_file)):
            os.makedirs(os.path.dirname(_file))
        Path(_file).touch(exist_ok=False)


def sub_run(python_file, python_location=None, process_type='subprocess'):
    # run python file in subprocess with cwd changed to file path
    file_path = os.path.dirname(os.path.abspath(python_file))
    if python_location is None:
        # use system python
        python_location = 'python3'
    if process_type == 'subprocess':
        return subprocess.run([python_location, python_file], shell=False, cwd=file_path)
    elif process_type == 'multiprocess':
        handler = Process(target=sub_run, kwargs={'python_file': python_file,
                                                  'python_location': python_location,
                                                  'process_type': 'subprocess'})
        handler.start()
        return handler
    else:
        raise AssertionError


class ZooKeeper:
    def __init__(self, date=None, base_flag_dir=public_flag_root_path,
                 log_name='cronb', log_file_name='cronb.log', auto_trading_date_flag=True):
        self.smp = Semaphore(base_flag_dir)
        self.logger = ut.add_file_logger(log_name, file_name=os.path.join(private_log_path, log_file_name))
        if date is not None:
            self.date = IO.str_date_parser(date)
        else:
            if auto_trading_date_flag:
                self.date = tdt.get_trading_day_offset(dt.date.today(), 0)[0]
            else:
                self.date = IO.str_date_parser(dt.date.today())
        self.logger.info('~' * 60)
        self.logger.info('preparing base data and factors for %s' % self.date)

    def fire(self, job_name, ftypes, python_file, process_type='subprocess', exit_failed=True, python_location=private_python_path):
        self.logger.info('*' * 30)
        self.logger.info('begin to init %s' % job_name)
        self.logger.info('checking base flags: %s' % ftypes)
        if self.smp.wait(ftypes, self.date):
            self.logger.info('check base complete, fire update program in subprocess')
            self.logger.info('init %s' % python_file)
            handler = sub_run(python_file, python_location=python_location, process_type=process_type)
            if process_type == 'subprocess':
                self.logger.info('%s finished' % job_name)
            else:
                self.logger.info('%s initiated' % job_name)
            return handler
        else:
            self.logger.warning('%s exited due to failed prerequisites' % job_name)
            if exit_failed:
                sys.exit()


if __name__ == '__main__':
    smp = Semaphore(public_flag_root_path)
    # smp.check('fdd', '20200101')
    # print(smp.wait([], '20200101'))


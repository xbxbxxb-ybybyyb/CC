import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import inspect
import re

from HFfactor.MinFactorSuper.RealTime.Operators import *

from HFfactor.MinFactorSuper.RealTime.UsefulList import MaterialList, OperatorList


def recover_number(s):
    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            return s


def formula2program(formula):
    program = formula.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    program = [recover_number(x) for x in program]
    return program


def get_factor_type(fac_name):
    if re.match('^ret_', fac_name):
        return 'ret'
    elif re.match('^num_', fac_name):
        return 'num'
    elif re.match('^turn_', fac_name):
        return 'turn'
    elif re.match('^p\w{1,2}_', fac_name):
        return 'val'
    elif re.match('^adj_', fac_name):
        return 'adj'
    else:
        return 'no'


class Operator(object):

    def __init__(self, func_name):

        if re.match('ts_', func_name):
            self.type = 'ts'
        elif re.match('ds_', func_name):
            self.type = 'ds'
        elif re.match('dt_', func_name):
            self.type = 'dt'
        elif func_name in ['max_min_ewm_dev2']:
            self.type = 'dt'
        elif re.match('cs_', func_name):
            self.type = 'cs'
        elif func_name in ['sign', 'time_condition', 'arr_condition2',
                           'brr_condition2', 'zero_condition2', 'pn_condition2']:
            self.type = 'if'
        else:
            self.type = 'no'

        params = inspect.getfullargspec(eval(func_name)).args
        var = [x for x in params if x in ('x', 'y', 'z')]
        const = [x for x in params if x not in ('x', 'y', 'z')]
        var_num = len(var)
        const_num = len(const)

        self.name = [func_name]
        self.params = params
        self.var = var
        self.const = const
        self.var_num = var_num
        self.const_num = const_num

    @property
    def code(self):

        return 'O' + self.type + str(self.var_num) + ''.join(self.const)


def get_program_factor(formula):
    program = formula.replace('*', ' ').replace('/', ' ').replace('+', ' ').replace(
        '-', ' ').replace('&', ' ').replace('|', ' ').replace('%', ' ').replace(
        ',', ' ').replace('(', ' ').replace(')', ' ').split()
    factors = sorted(list(set(program) & set(MaterialList)))
    return factors


def check_complete(formula):
    program = formula.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    program = [recover_number(x) for x in program]
    terminal_stack = []
    for item in program:

        if item in OperatorList:
            terminal_stack.append(1 if not item[-1].isdigit() else int(item[-1]))
        elif item in MaterialList:
            terminal_stack[-1] -= 1
            while terminal_stack[-1] == 0:
                terminal_stack.pop()
                if not terminal_stack:
                    return True
                terminal_stack[-1] -= 1
        elif isinstance(item, str):
            raise ValueError("Any basic factor or operator created without permission is not allowed.")
    return False

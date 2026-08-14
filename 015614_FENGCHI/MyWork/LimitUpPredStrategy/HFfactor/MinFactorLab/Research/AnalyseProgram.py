from HFfactor.MinFactorLab.RealTime.UsefulList import MaterialList, OperatorList
from HFfactor.MinFactorLab.RealTime.Operators import *
import pandas as pd
import inspect
import re

OperatorTime = pd.read_pickle('/arch1/group/800442/800319/MinFactor/Research/OperatorTime.pkl')


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


def analyse_program(program, freq=242):
    if isinstance(program, str):
        program = formula2program(program)

    program_formula = ''
    program_type = []
    program_depth = 0
    program_delay = 0
    program_length = len(program)

    factor_appear = sorted([x for x in program if x in MaterialList])
    factor_unique = sorted(list(set(factor_appear)))
    factor_appear_num = len(factor_appear)
    factor_unique_num = len(factor_unique)
    factor_duplicated = factor_appear_num > factor_unique_num
    factor_type = [get_factor_type(x) for x in factor_unique]
    factor_type = {x: len([y for y in factor_type if y == x])
                   for x in ['ret', 'turn', 'num', 'val', 'adj']}

    operator_unique = sorted(list(set(program) & set(OperatorList)))
    operator_unique_num = len(operator_unique)
    operator_duplicated = False
    operator_type = [Operator(x).type for x in operator_unique]
    operator_type = {x: len([y for y in operator_type if y == x])
                     for x in ['dt', 'ds', 'ts', 'cs', 'if', 'no']}

    terminals = []
    constants = []
    operator_main = []
    operators = []
    operator_sub = []
    delays = []
    delay = 1
    unit_time = 0.

    for node in program:

        if node in OperatorList:
            operator = Operator(node)
            operator_main.append([node])
            operator_sub.append([])
            operators.append(operator.name)
            terminals.append(operator.var_num)
            constants.append(operator.const)
            program_depth = max(len(terminals), program_depth)
            program_formula += node + '('
            program_type.append(operator.code)
            delays.append(0)
            if node in OperatorTime:
                unit_time += OperatorTime[node]
        elif node in MaterialList:
            program_formula += node
            program_type.append('F' + get_factor_type(node))
            terminals[-1] -= 1
        else:
            const_type = constants[-1][0]
            operator_specific = operators[-1][0]
            program_type.append(const_type)
            program_formula += str(node)
            constants[-1].remove(const_type)
            operators[-1].remove(operator_specific)
            if const_type[0] == 'd':
                delay += freq * (node - 1)
            elif const_type[0] == 'm':
                delay += node - 1
            if node:
                unit_time += OperatorTime[(operator_specific, node)]
            else:
                unit_time += OperatorTime[operator_specific]

        while terminals:
            if (terminals[-1] == 0) & (constants[-1] == []):
                program_formula += ')'
                constants.pop()
                operators.pop()
                delay += delays[-1]
                delays.pop()
                if delays:
                    delays[-1] = max(delays[-1], delay)
                else:
                    program_delay = delay
                delay = 0
                operator_appear = operator_main[-1] + operator_sub[-1]
                operator_appear_set = set(operator_appear)
                operator_duplicated |= len(operator_appear) > len(operator_appear_set)
                operator_main.pop()
                operator_sub.pop()
                if operator_main:
                    operator_sub[-1] = list(operator_appear_set & set(operator_sub[-1])
                                            ) if operator_sub[-1] else list(operator_appear_set)
                terminals.pop()
                if terminals:
                    terminals[-1] -= 1
            else:
                if program_formula[-1] != '(':
                    program_formula += ', '
                break
    delay_days = (program_delay - 2) // 242 + 2
    no_dt = operator_type['dt'] == 0
    online_time = unit_time * delay_days / (no_dt + 1)

    analyse_result = dict(
        program=program,
        unit_time=unit_time,
        delay_days=delay_days,
        online_time=online_time,

        program_type=program_type,
        program_depth=program_depth,
        program_delay=program_delay,
        program_length=program_length,
        program_formula=program_formula,

        factor_type=factor_type,
        factor_appear=factor_appear,
        factor_unique=factor_unique,
        factor_appear_num=factor_appear_num,
        factor_unique_num=factor_unique_num,
        factor_duplicated=factor_duplicated,

        operator_type=operator_type,
        operator_unique=operator_unique,
        operator_duplicated=operator_duplicated,
        operator_unique_num=operator_unique_num,
    )
    return analyse_result


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


from FactorTest import FactorTest
from FactorList import OperatorList, FactorList, Params
from operators import *
from string import digits
from copy import deepcopy
import pandas as pd
import numpy as np
import random
import inspect
import pickle
import dask
import time
import gc
import re
import os

root_path = '/data/group/800442/800319/Afengchi/'
fold_success = root_path + '机器挖掘/success/'
fold_failure = root_path + '机器挖掘/fail/'


def corr_filter(limit, sample, metrics):
    metrics = np.array(metrics)
    sample = np.abs(np.corrcoef(sample))

    rank = (- metrics).argsort(axis=-1)
    corr = sample[rank[:, None], rank[None, :]]
    corr_triu = np.tril_indices(corr.shape[0])
    corr[corr_triu] = 0.

    corr_pool = corr.max(axis=0) < limit
    _corr_pool_num1 = 0
    _corr_pool_num2 = corr_pool.sum()
    while _corr_pool_num2 > _corr_pool_num1:
        _corr_pool_num1 = _corr_pool_num2
        corr[corr[corr_pool].max(axis=0) >= limit] = 0
        corr_pool = corr.max(axis=0) < limit
        _corr_pool_num2 = corr_pool.sum()

    return rank[corr_pool]

def summary_failure(sleep=0, once=False):

    while True:
        level0 = '/data/group/800442/800319/junkBigFactorPool/level0_unfinished/fail/'
        factors = os.listdir(level0)
        program_code = set()
        for factor in factors:
            dic = load_pickle(level0 + factor)
            if not dic['program_complex']:
                program_code.update([dic['program_code']])
        globals()['fold_failure'] = program_code
        if once:
            break
        time.sleep(sleep)

def summary_success(sleep=600, father_dict=None, once=False):

    default_father_dict = dict(
        str_eval='3 * ic_all_t + ic_all_dtc + ic_all_c + ic_all_dt',
        str_query='date_invalid_num < 99 & ' \
                  '0.03 < dtc_all_sign < 0.07 & ' \
                  'dtc_all_ret + t_dc_all_ret + tc_d_all_ret + t_c_d_all_ret > 0.003 & ' \
                  '"sign(" not in program_code',
        len_pre=500,
        len_pro=50,
        corr_limit=0.7,
    )

    if father_dict:
        default_father_dict.update(father_dict)

    while True:

        level0 = '/data/group/800442/800319/junkBigFactorPool/level0_unfinished/fail/'
        factors = os.listdir(level0)

        name = []
        program_code = []
        date_invalid_num = []
        dtc_all_sign = []
        ic_all_dtc = []
        ic_all_dt = []
        ic_all_c = []
        ic_all_d = []
        ic_all_t = []
        dtc_all_ret = []
        t_dc_all_ret = []
        tc_d_all_ret = []
        t_c_d_all_ret = []

        for factor in factors:
            dic = load_pickle(level0 + factor)
            if not dic['program_complex']:
                name.append(factor)
                program_code.append(dic['program_code'])
                date_invalid_num.append(dic['date_invalid_num'])
                dtc_all_sign.append(dic['dtc_all_sign'])
                ic_all_dtc.append(dic['ic_all_dtc'])
                ic_all_dt.append(dic['ic_all_dt'])
                ic_all_c.append(dic['ic_all_c'])
                ic_all_d.append(dic['ic_all_d'])
                ic_all_t.append(dic['ic_all_t'])
                dtc_all_ret.append(dic['dtc_all_ret'])
                t_dc_all_ret.append(dic['t_dc_all_ret'])
                tc_d_all_ret.append(dic['tc_d_all_ret'])
                t_c_d_all_ret.append(dic['t_c_d_all_ret'])

        df = pd.DataFrame({
            'name': name,
            'program_code': program_code,
            'date_invalid_num': date_invalid_num,
            'dtc_all_sign': dtc_all_sign,
            'ic_all_dtc': ic_all_dtc,
            'ic_all_dt': ic_all_dt,
            'ic_all_c': ic_all_c,
            'ic_all_d': ic_all_d,
            'ic_all_t': ic_all_t,
            'dtc_all_ret': dtc_all_ret,
            't_dc_all_ret': t_dc_all_ret,
            'tc_d_all_ret': tc_d_all_ret,
            't_c_d_all_ret': t_c_d_all_ret,
        })

        df = df.drop_duplicates(['program_code'])

        df.eval('score = %s' % default_father_dict['str_eval'], inplace=True)
        df.sort_values('score', ascending=False, inplace=True)
        df = df.query(default_father_dict['str_query'])
        df = df.head(default_father_dict['len_pre'])

        ic_all_dt_every_code = []
        for factor in df['name']:
            dic = load_pickle(level0 + factor)
            ic_all_dt_every_code.append(dic['ic_all_dt_every_code'])
        ic_all_dt_every_code = np.asanyarray(ic_all_dt_every_code)

        df = df.iloc[corr_filter(default_father_dict['corr_limit'], ic_all_dt_every_code, df['score'])]
        df = df.head(2 * default_father_dict['len_pro'])['program_code'].to_list()
        random.shuffle(df)
        df = df[:default_father_dict['len_pro']]
        globals()['fold_success'] = df
        if once:
            break
        time.sleep(sleep)

def p_choice(arr, random_state, method='ewm'):

    num = len(arr)
    if method == 'ewm':
        alpha = 0.5 ** (2 / num)
        weight = alpha ** np.arange(num).astype(float)
    elif method == 'lwm':
        weight = np.arange(num)[::-1].astype(float) + 1
    else:
        raise ValueError
    weight /= weight.sum()
    return random_state.choice(arr, p=weight)

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

def recover_number(s):

    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            return s

def formula2program(formula):

    program =  formula.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    program = [recover_number(x) for x in program]
    return program

def check_complete(formula):

    program =  formula.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    program = [recover_number(x) for x in program]

    terminal_stack = []

    for item in program:

        if item in OperatorList:
            terminal_stack.append(1 if not item[-1].isdigit() else int(item[-1]))
        elif item in FactorList:
            terminal_stack[-1] -= 1
            while terminal_stack[-1] == 0:
                terminal_stack.pop()
                if not terminal_stack:
                    return True
                terminal_stack[-1] -= 1
        elif isinstance(item, str):
            raise ValueError("Any basic factor or operator created without permission is not allowed.")
    return False

def save_pickle(file, data):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

def load_pickle(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
    return data

class Operator(object):

    def __init__(self, func_name):

        if re.match('ts_', func_name):
            self.type = 'ts'
        elif re.match('ds_', func_name):
            self.type = 'ds'
        elif re.match('dt_', func_name):
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

        self.params = params
        self.var = var
        self.const = const
        self.var_num = var_num
        self.const_num = const_num

    @property
    def code(self):

        return 'O' + self.type + str(self.var_num) + ''.join(self.const)

def analyse_program(program, factor_list, operator_list, freq=48):

    if isinstance(program, str):
        program = formula2program(program)

    program_formula = ''
    program_type = []
    program_depth = 0
    program_delay = 0
    program_length = len(program)

    factor_appear = sorted([x for x in program if x in factor_list])
    factor_unique = sorted(list(set(factor_appear)))
    factor_appear_num = len(factor_appear)
    factor_unique_num = len(factor_unique)
    factor_duplicated = factor_appear_num > factor_unique_num
    factor_type = [get_factor_type(x) for x in factor_unique]
    factor_type = {x: len([y for y in factor_type if y == x])
                   for x in ['ret', 'turn', 'num', 'val', 'adj']}

    operator_unique = sorted(list(set(program) & set(operator_list)))
    operator_unique_num = len(operator_unique)
    operator_duplicated = False
    operator_type = [Operator(x).type for x in operator_unique]
    operator_type = {x: len([y for y in operator_type if y == x])
                     for x in ['dt', 'ds', 'ts', 'cs', 'if', 'no']}


    terminals = []
    constants = []
    operator_main = []
    operator_sub = []
    delays = []
    delay = 0
    for node in program:

        if node in operator_list:
            operator = Operator(node)
            operator_main.append([node])
            operator_sub.append([])
            terminals.append(operator.var_num)
            constants.append(operator.const)
            program_depth = max(len(terminals), program_depth)
            program_formula += node + '('
            program_type.append(operator.code)
            delays.append(0)
        elif node in factor_list:
            program_formula += node
            program_type.append('F' + get_factor_type(node))
            terminals[-1] -= 1
        else:
            const_type = constants[-1][0]
            program_type.append(const_type)
            program_formula += str(node)
            constants[-1].remove(const_type)
            if const_type[0] == 'd':
                delay += freq * node
            elif const_type[0] == 'm':
                delay += node

        while terminals:
            if (terminals[-1] == 0) & (constants[-1] == []):
                program_formula += ')'
                constants.pop()
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

    analyse_result = dict(
        program = program,
        program_type = program_type,
        program_depth = program_depth,
        program_delay = program_delay,
        program_length = program_length,
        program_formula = program_formula,

        factor_type = factor_type,
        factor_appear = factor_appear,
        factor_unique = factor_unique,
        factor_appear_num = factor_appear_num,
        factor_unique_num = factor_unique_num,
        factor_duplicated = factor_duplicated,

        operator_type = operator_type,
        operator_unique = operator_unique,
        operator_duplicated = operator_duplicated,
        operator_unique_num = operator_unique_num,
    )
    return analyse_result

def check_program(analyse_result, check_dict=None):

    default_dict = dict(
        factor_unique=False,
        operator_unique=False,
        max_depth=7,
        max_delay=1440,
        max_factor_num=4,
        max_operator_num=None,
        max_factor_type=None,
        max_operator_type={'cs': 0, 'if': 2},
        min_depth=3,
        min_delay=None,
        min_factor_num=None,
        min_operator_num=None,
        min_factor_type=None,
        min_operator_type=None,
        factor_contains=None,
        operator_contains=None,
        factor_not_contains=None,
        operator_not_contains='sign',
    )

    if check_dict:
        default_dict.update(check_dict)

    program_valid = True

    if default_dict['factor_unique']:
        program_valid &= ~ analyse_result['factor_duplicated']
    if default_dict['operator_unique']:
        program_valid &= ~ analyse_result['operator_duplicated']
    if default_dict['max_depth']:
        program_valid &= analyse_result['program_depth'] <= default_dict['max_depth']
    if default_dict['min_depth']:
        program_valid &= analyse_result['program_depth'] >= default_dict['min_depth']
    if default_dict['max_delay']:
        program_valid &= analyse_result['program_delay'] <= default_dict['max_delay']
    if default_dict['min_delay']:
        program_valid &= analyse_result['program_delay'] >= default_dict['min_delay']
    if default_dict['max_factor_num']:
        program_valid &= analyse_result['factor_unique_num'] <= default_dict['max_factor_num']
    if default_dict['min_factor_num']:
        program_valid &= analyse_result['factor_unique_num'] >= default_dict['min_factor_num']
    if default_dict['max_operator_num']:
        program_valid &= analyse_result['operator_unique_num'] <= default_dict['max_operator_num']
    if default_dict['min_operator_num']:
        program_valid &= analyse_result['operator_unique_num'] >= default_dict['min_operator_num']
    if default_dict['max_factor_type']:
        dic = {k: default_dict['max_factor_type'][k] for k in default_dict[
            'max_factor_type'] if default_dict['max_factor_type'][k] is not None}
        for k in dic:
            program_valid &= analyse_result['factor_type'][k] <= dic[k]
    if default_dict['min_factor_type']:
        dic = {k: default_dict['min_factor_type'][k] for k in default_dict[
            'min_factor_type'] if default_dict['min_factor_type'][k] is not None}
        for k in dic:
            program_valid &= analyse_result['factor_type'][k] >= dic[k]
    if default_dict['max_operator_type']:
        dic = {k: default_dict['max_operator_type'][k] for k in default_dict[
            'max_operator_type'] if default_dict['max_operator_type'][k] is not None}
        for k in dic:
            program_valid &= analyse_result['operator_type'][k] <= dic[k]
    if default_dict['min_operator_type']:
        dic = {k: default_dict['min_operator_type'][k] for k in default_dict[
            'min_operator_type'] if default_dict['min_operator_type'][k] is not None}
        for k in dic:
            program_valid &= analyse_result['operator_type'][k] >= dic[k]
    if default_dict['factor_contains']:
        factor_contains = [default_dict['factor_contains']] if isinstance(
            default_dict['factor_contains'], str) else default_dict['factor_contains']
        for factor in factor_contains:
            program_valid &= factor in analyse_result['factor_unique']
    if default_dict['factor_not_contains']:
        factor_not_contains = [default_dict['factor_not_contains']] if isinstance(
            default_dict['factor_not_contains'], str) else default_dict['factor_not_contains']
        for factor in factor_not_contains:
            program_valid &= factor not in analyse_result['factor_unique']
    if default_dict['operator_contains']:
        operator_contains = [default_dict['operator_contains']] if isinstance(
            default_dict['operator_contains'], str) else default_dict['operator_contains']
        for operator in operator_contains:
            program_valid &= operator not in analyse_result['operator_unique']
    if default_dict['operator_not_contains']:
        operator_not_contains = [default_dict['operator_not_contains']] if isinstance(
            default_dict['operator_not_contains'], str) else default_dict['operator_not_contains']
        for operator in operator_not_contains:
            program_valid &= operator not in analyse_result['operator_unique']
    return program_valid

def evaluate_program(program_formula, ft):

    program = dict(
        program_code=program_formula,
        program_complex=False,
        program_manual=False,
        program_author='015836',
        program_class='机器挖掘',
        program_reference='无知无畏',
        program_logic='无知无畏',
    )
    ft.test_factor(program)

class Program(object):

    def __init__(self, random_state, head_operator=None,
                 factor_list=FactorList, operator_list=OperatorList, params=Params,
                 init_depth=(1, 6), init_method='half', const_method='ewm',
                 p_point_replace=0.1, p_crossover=0.2, p_subtree_mutation=0.3,
                 p_hoist_mutation=0.2, p_point_mutation=0.3,
                 operator_broad_mind=False, factor_broad_mind=False):

        method_probs = np.cumsum(np.abs(np.array([p_crossover, p_subtree_mutation,
                                                  p_hoist_mutation, p_point_mutation])))
        method_probs /= method_probs.max()

        self.params = params
        self.head_operator = head_operator
        self.init_depth = init_depth
        self.init_method = init_method
        self.factor_list = factor_list
        self.operator_list = operator_list
        self.random_state = random_state
        self.const_method = const_method
        self.factor_num = len(factor_list)
        self.operator_num = len(operator_list)
        self.method_probs = method_probs
        self.p_point_replace = p_point_replace
        self.p_crossover = p_crossover
        self.p_subtree_mutation = p_subtree_mutation
        self.p_hoist_mutation = p_hoist_mutation
        self.p_point_mutation = p_point_mutation
        self.operator_broad_mind = operator_broad_mind
        self.factor_broad_mind = factor_broad_mind

    def build_program(self):

        random_state = np.random.RandomState(np.random.RandomState(self.random_state).randint(1000))
        method = ('full' if random_state.randint(2) else 'grow'
                  ) if self.init_method == 'half' else self.init_method
        max_depth = random_state.randint(*self.init_depth)

        if isinstance(self.head_operator, list):
            operator = self.head_operator[random_state.randint(len(self.head_operator))]
        elif isinstance(self.head_operator, str):
            if self.head_operator[0] != '~':
                operator = self.head_operator
            else:
                operator_list = list(set(self.operator_list) - {self.head_operator[1:]})
                operator = operator_list[random_state.randint(self.operator_num)]
        else:
            operator = self.operator_list[random_state.randint(self.operator_num)]

        program = [operator]
        operator_ = Operator(operator)
        terminal_stack = [operator_.var_num]
        const_list = [operator_.const]

        while terminal_stack:
            depth = len(terminal_stack)
            choice = random_state.randint(self.factor_num + self.operator_num)
            if (depth < max_depth) & ((method == 'full') | (choice <= self.operator_num)):
                operator = self.operator_list[random_state.randint(self.operator_num)]
                program.append(operator)
                operator_ = Operator(operator)
                terminal_stack.append(operator_.var_num)
                const_list.append(operator_.const)
            else:
                factor = self.factor_list[random_state.randint(self.factor_num)]
                program.append(factor)
                terminal_stack[-1] -= 1
                while terminal_stack[-1] == 0:
                    for const in const_list[-1]:
                        program.append(p_choice(self.params[const],
                                                random_state, self.const_method))
                    const_list.pop()
                    terminal_stack.pop()
                    if not terminal_stack:
                        return program
                    terminal_stack[-1] -= 1

    def hard_build_program(self, choice):

        random_state = np.random.RandomState(np.random.RandomState(self.random_state).randint(1000))

        program = []
        terminal_stack = []
        const_list = []

        for obj in choice:
            obj = obj[random_state.randint(len(obj))] if isinstance(obj, list) else obj
            if obj in self.operator_list:
                operator = obj
                program.append(operator)
                operator_ = Operator(operator)
                terminal_stack.append(operator_.var_num)
                const_list.append(operator_.const)
            elif obj in self.factor_list:
                factor = obj
                program.append(factor)
                terminal_stack[-1] -= 1
                while terminal_stack[-1] == 0:
                    for const in const_list[-1]:
                        program.append(p_choice(self.params[const],
                                                random_state, self.const_method))
                    const_list.pop()
                    terminal_stack.pop()
                    if not terminal_stack:
                        return program
                    terminal_stack[-1] -= 1
            else:
                raise ValueError("Wrong choice value type.")

    def get_subtree(self, program):

        probability = np.array([0.9 if node in self.operator_list else (
            0.1 if node in self.factor_list else 0) for node in program])
        if len(program) > 1:
            probability[0] = 0
        probability = np.cumsum(probability / probability.sum())
        start = np.searchsorted(probability, np.random.uniform())

        stack = 1
        end = start
        while stack > end - start:
            node = program[end]
            if node in self.operator_list:
                operator = Operator(node)
                stack += operator.var_num + operator.const_num
            end += 1

        return start, end

    def reproduce(self, program):

        return deepcopy(program)

    def crossover(self, donor, program):

        start, end = self.get_subtree(program)
        removed = range(start, end)
        donor_start, donor_end = self.get_subtree(donor)
        donor_removed = list(set(range(len(donor))) -
                             set(range(donor_start, donor_end)))
        return (program[:start] +
                donor[donor_start:donor_end] +
                program[end:]), removed, donor_removed

    def subtree_mutation(self, program):

        chicken = self.build_program()
        return self.crossover(chicken, program)

    def hoist_mutation(self, program):

        start, end = self.get_subtree(program)
        subtree = program[start: end]
        sub_start, sub_end = self.get_subtree(subtree)
        hoist = subtree[sub_start: sub_end]
        removed = list(set(range(start, end)) -
                       set(range(start + sub_start, start + sub_end)))
        return program[:start] + hoist + program[end:], removed

    def point_mutation(self, program):

        program = deepcopy(program)
        mutate = np.where([True if (np.random.uniform() <
                                    self.p_point_replace)
                           else False
                           for _ in range(len(program))])[0]

        program_type = analyse_program(program, self.factor_list, self.operator_list, 48)['program_type']

        for node in mutate:

            if program[node] in self.operator_list:
                operator = Operator(program[node])
                var_x = operator.var_num
                code_x = operator.code
                code_x = code_x.translate(str.maketrans('', '', digits)
                                          ) if self.operator_broad_mind else code_x

                operator_list = [x for x in self.operator_list if
                                 (Operator(x).var_num == var_x) and
                                 ((Operator(x).code.translate(str.maketrans(
                                     '', '', digits)) if self.operator_broad_mind
                                   else Operator(x).code) == code_x)]

                replacement = np.random.randint(len(operator_list))
                replacement = operator_list[replacement]

            elif program[node] in self.factor_list:
                if self.factor_broad_mind:
                    replacement = np.random.randint(self.factor_num)
                    replacement = self.factor_list[replacement]
                else:
                    type_x = get_factor_type(program[node])
                    factor_list = [x for x in self.factor_list
                                   if get_factor_type(x) == type_x]
                    replacement = np.random.randint(len(factor_list))
                    replacement = factor_list[replacement]

            else:
                constants = self.params[program_type[node]]
                replacement = p_choice(constants, np.random.RandomState(), self.const_method)

            program[node] = replacement

        return program, list(mutate)

    def exclusion_evolution(self, fold_success, fold_failure):

        method = np.random.uniform()
        valid = False
        while not valid:
            program = formula2program(fold_success[np.random.randint(0, len(fold_success))])
            if method < self.method_probs[0]:
                donor = formula2program(fold_success[np.random.randint(0, len(fold_success))])
                program = self.crossover(donor, program)[0]
            elif method < self.method_probs[1]:
                program = self.subtree_mutation(program)[0]
            elif method < self.method_probs[2]:
                program = self.hoist_mutation(program)[0]
            else:
                program = self.point_mutation(program)[0]
            analyse = analyse_program(program, self.factor_list, self.operator_list)
            valid = check_program(analyse)
            valid &= analyse['program_formula'] not in fold_failure
        return analyse['program_formula']

    def independent_evolution(self, fold_success, fold_failure):

        valid = False
        while not valid:
            program = formula2program(fold_success[np.random.randint(0, len(fold_success))])
            if np.random.uniform() < self.p_crossover:
                donor = formula2program(fold_success[np.random.randint(0, len(fold_success))])
                program = self.crossover(donor, program)[0]
            if np.random.uniform() < self.p_subtree_mutation:
                program = self.subtree_mutation(program)[0]
            if np.random.uniform() < self.p_hoist_mutation:
                program = self.hoist_mutation(program)[0]
            if np.random.uniform() < self.p_point_mutation:
                program = self.point_mutation(program)[0]
            analyse = analyse_program(program, self.factor_list, self.operator_list)
            valid = check_program(analyse)
            valid &= analyse['program_formula'] not in fold_failure
        return analyse['program_formula']

def play_heredity(lines):

    ft = FactorTest()
    heredity = Program(random_state=345)


    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    summary_failure(once=True)
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    summary_success(once=True)
    print(time.strftime('%Y-%m-%d %H:%M:%S'))

    # for basic_factor in FactorList:
    #     if basic_factor not in globals():
    #         print(basic_factor)
    #         globals()[basic_factor] = np.load(
    #             '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)

    def _play_heredity(j):

        while True:
            program = heredity.exclusion_evolution(fold_success, fold_failure)
            evaluate_program(program, ft)
            fold_failure.update([program])
            print('line %s: ' % j, time.strftime('%Y-%m-%d %H:%M:%S'))

    batches = []
    batches.append(dask.delayed(summary_failure)(0))
    batches.append(dask.delayed(summary_success)(600))
    for j in range(lines):
        batches.append(dask.delayed(_play_heredity)(j))
    dask.compute(batches)

play_heredity(36)
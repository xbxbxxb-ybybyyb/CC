import pandas as pd
from gplearn_modify.functions import _function_map, _Function
from gplearn_modify.genetic import SymbolicTransformer
from gplearn_modify.fitness import information_coefficient, sharpe_ratio, fitness1, r_square, fitness2, fitness3
from gplearn_modify._program import _Program


def get_str(program, feature_names):
    """Overloads `print` output of the object to resemble a LISP tree."""
    terminals = [0]
    output = ''
    for i, node in enumerate(program[0]):
        if isinstance(node, _Function):
            terminals.append(node.arity)
            output += node.name + '('
        else:
            if isinstance(node, int):
                if feature_names is None:
                    output += 'X%s' % node
                else:
                    output += feature_names[node]
            else:
                output += '%.3f' % node
            terminals[-1] -= 1
            while terminals[-1] == 0:
                terminals.pop()
                terminals[-1] -= 1
                output += ')'
            if i != len(program[0]) - 1:
                output += ', '

    brackets_pair_list = _Program.get_y(output)
    for i, i_num in enumerate(program[1]):
        if i_num != 0:
            temp_num = brackets_pair_list[i][1]
            output = output[:temp_num] + ', ' + str(i_num) + output[temp_num:]
            brackets_pair_list = _Program.get_y(output)
    return output

    return output


if __name__ == '__main__':
    '''数据导入'''
    future_data_ic = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/5s/MD_IC_5S_MAIN.h5').xs('IC.CFE', level=1)
    future_data_ic = future_data_ic[['open_ic', 'close_ic', 'high_ic', 'low_ic', 'volume_ic', 'vwap_ic', 'value_ic', 'position_ic']]
    future_data_ic = future_data_ic['20190701': '20191231']
    # future_data_ic = future_data_ic.fillna(method='ffill')

    future_return = future_data_ic['vwap_ic'].shift(-2) / future_data_ic['vwap_ic'].shift(-1) - 1
    future_return.name = 'return'
    # future_return = future_return.fillna(0)

    '''导入gplearn module'''
    function_set = list(_function_map.keys())
    gp1 = SymbolicTransformer(population_size=3000, hall_of_fame=100, n_components=20, generations=20,
                              tournament_size=2, stopping_criteria=0.5, const_range=None, const_params_range=(3, 121),
                              init_depth=(1, 4), init_method='half and half', function_set=function_set,
                              metric=fitness3, parsimony_coefficient=0.005, p_crossover=0.87, p_subtree_mutation=0.02,
                              p_hoist_mutation=0.02, p_point_mutation=0.02, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(future_data_ic.columns), warm_start=False, low_memory=False, n_jobs=-1,
                              verbose=1, random_state=2)

    gp2 = SymbolicTransformer(population_size=30, hall_of_fame=6, n_components=3, generations=3, tournament_size=3,
                              stopping_criteria=1, const_range=None, const_params_range=(3, 241), init_depth=(1, 3),
                              init_method='half and half', function_set=function_set, metric=fitness2,
                              parsimony_coefficient=0.005, p_crossover=0.9, p_subtree_mutation=0.01,
                              p_hoist_mutation=0.01, p_point_mutation=0.01, p_point_replace=0.05, max_samples=1.0,
                              feature_names=list(future_data_ic.columns), warm_start=False, low_memory=False, n_jobs=1,
                              verbose=1, random_state=1)

    gp1.fit(future_data_ic, future_return)

    for i in gp1._best_programs:
        print(get_str(i.program, feature_names=list(future_data_ic.columns)))

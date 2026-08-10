import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.help_functions import read_pickle, rolling_norm, save_pickle
from factor_test.SIF_Factor_Test10_modify import SIF_Factor_Test
from multiprocessing.pool import Pool
from utils.help_functions_wsc import ts_sum, ts_mean, ts_argmax, ts_argmin, ts_rank

np.random.seed(1)


# 生成shape为[individuals, chromosome_length]的均匀分布
def create_starting_population(individuals, chromosome_length):
    return np.random.uniform(low=0.2, high=3, size=(individuals, chromosome_length))


def select_individual_by_tournament(population, scores):
    population_size = len(scores)  # Get population size

    # Pick individuals for tournament
    fighter_1 = np.random.randint(0, population_size)
    fighter_2 = np.random.randint(0, population_size)

    # Get fitness score for each
    fighter_1_fitness = scores[fighter_1]
    fighter_2_fitness = scores[fighter_2]

    # Identify undividual with highest fitness
    # Fighter 1 will win if score are equal
    if fighter_1_fitness >= fighter_2_fitness:
        winner = fighter_1
    else:
        winner = fighter_2

    # Return the chromsome of the winner
    return population[winner]


def breed_by_crossover(parent_1, parent_2):
    chromosome_length = len(parent_1)
    crossover_point = np.random.randint(1, chromosome_length - 1)  # Pick crossover point, avoding ends of chromsome
    child_1 = np.hstack((parent_1[0:crossover_point], parent_2[crossover_point:]))  # Create children
    child_2 = np.hstack((parent_2[0:crossover_point], parent_1[crossover_point:]))

    return child_1, child_2


# 把变异的单染色体置为0
def randomly_mutate_population(population, mutation_probability):
    # Apply random mutation
    random_mutation_array = np.random.random(size=population.shape)
    random_mutation_boolean = random_mutation_array <= mutation_probability
    population[random_mutation_boolean] = np.logical_not(population[random_mutation_boolean])

    return population


layers = 4
signal_lims = (-1, 1)
threshold = max(signal_lims) - 2 * max(signal_lims) / layers


def signal_reshaper(signals, signal_lims=signal_lims, threshold=threshold):
    assert isinstance(signals, pd.Series)
    assert isinstance(signal_lims, tuple)
    assert 0 < threshold < 1
    signals = signals.copy()
    signals.index.name = 'dt'
    signals.name = 'signals'
    signals.loc[signals >= threshold] = threshold
    signals.loc[signals <= -threshold] = -threshold
    signals.loc[(signals < threshold) & (signals > - threshold)] = 0
    signals = signals / threshold
    return signals


# *************************************
# ******** MAIN ALGORITHM CODE ********
# *************************************

# 读取期指收益率数据
future_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/FUTURE_DATA_insample.pkl')
vwap_recent_month = (future_data['vwap'][future_data['recent_month_mask']].sum(axis=1))
ret = vwap_recent_month.shift(-2) - vwap_recent_month.shift(-1)
ret = ret['2019-05':].to_frame()
ret.columns = ['return_points']
ret = ret.fillna(0)

# 数据导入，需导入因子值和收益两项数据
cfg_data = read_pickle('/data/user/017024/data/cache/IC_complex.pkl')
stk_close = cfg_data['close_zz500']
n = 30
arron_up = ts_argmax(stk_close, n) / n * 100  # 过去n分钟最高价出现时间与当前时间的距离占时间段长度的比例
arron_down = ts_argmin(stk_close, n) / n * 100  # 过去n分钟最低价出现时间与当前时间的距离占时间段长度的比例
arron_os = arron_up - arron_down
factor_init = arron_os
factor_mean = ts_mean(factor_init, 7)
factor = ts_rank(factor_mean, 1200)
X = factor.reindex(ret.index)
X = X.fillna(0)
XT = np.transpose(X)

# Set general parameters
Chromosome_length = XT.shape[0]
Population_size = 750
maximum_generation = 250
best_score_progress = []  # Tracks progress

# Create reference solution
# (this is used just to illustrate GAs)
# reference = create_reference_solution(chromosome_length)

# Create starting population
Population = create_starting_population(Population_size, Chromosome_length)
print('============================= Start ==================================')
# Display best score in starting population
weighted_matrix = np.dot(Population, XT)


def calc_ts1(i, weighted_matrix=weighted_matrix, ret=ret, layers=4, fee=1.5, layer_lims=(-1, 1)):
    w = weighted_matrix[i]  # 第i行
    w = rolling_norm(w, window=1200, method='bn_move_rank')
    w[np.isnan(w)] = 0
    raw = pd.Series(w)
    raw.index = ret.index
    df = pd.concat([raw, ret], axis=1)

    df_slice = SIF_Factor_Test.slice_by_minute(df)
    ps_raw = df_slice.iloc[:, 0]
    ps_return = df_slice.iloc[:, 1]

    pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)

    maxQ = layers - 1

    stats = SIF_Factor_Test.signal_stats(signal_reshaper(ps_raw))

    long_deal_num = stats['long_deal_num']
    short_deal_num = stats['short_deal_num']
    rp_long = magic['return_points'][magic['bins'] == maxQ].sum()
    rp_short = magic['return_points'][magic['bins'] == 0].sum() * (-1)

    return [i, rp_long + rp_short - (long_deal_num + short_deal_num) * fee]


with Pool(24) as pool:
    hholder = pool.map(calc_ts1, list(range(weighted_matrix.shape[0])))

hholder = sorted(hholder, key=lambda x: x[0])
scores = [item[1] for item in hholder]

best_score = np.max(scores)
print('Starting best score, % target: ', best_score)

# Add starting best score to progress tracker
best_score_progress.append(best_score)

# Now we'll go through the generations of genetic algorithm
for generation in range(maximum_generation):
    # Create an empty list for new population
    new_population = []

    # Create new popualtion generating two children at a time
    for i in range(int(Population_size / 2)):
        parent_1 = select_individual_by_tournament(Population, scores)
        parent_2 = select_individual_by_tournament(Population, scores)
        child_1, child_2 = breed_by_crossover(parent_1, parent_2)
        new_population.append(child_1)
        new_population.append(child_2)

    new_population = np.array(new_population)  # Replace the old population with the new one

    # Apply mutation
    mutation_rate = 0.005
    Population = randomly_mutate_population(new_population, mutation_rate)

    # Score best solution, and add to tracker
    weighted_matrix = np.dot(Population, XT)


    def calc_ts2(i, weighted_matrix=weighted_matrix, ret=ret, layers=4, fee=1.5, layer_lims=(-1, 1)):
        w = weighted_matrix[i]  # 第i行
        w = rolling_norm(w, window=1200, method='bn_move_rank')
        w[np.isnan(w)] = 0
        raw = pd.Series(w)
        raw.index = ret.index
        df = pd.concat([raw, ret], axis=1)

        df_slice = SIF_Factor_Test.slice_by_minute(df)
        ps_raw = df_slice.iloc[:, 0]
        ps_return = df_slice.iloc[:, 1]

        pd_res, magic = SIF_Factor_Test.ts_segment_test(ps_raw, ps_return, layers=layers, layer_lims=layer_lims)

        maxQ = layers - 1

        stats = SIF_Factor_Test.signal_stats(signal_reshaper(ps_raw))

        long_deal_num = stats['long_deal_num']
        short_deal_num = stats['short_deal_num']
        rp_long = magic['return_points'][magic['bins'] == maxQ].sum()
        rp_short = magic['return_points'][magic['bins'] == 0].sum() * (-1)

        return [i, rp_long + rp_short - (long_deal_num + short_deal_num) * fee]


    with Pool(24) as pool:
        hholder = pool.map(calc_ts2, list(range(len(weighted_matrix))))

    hholder = sorted(hholder, key=lambda x: x[0])
    scores = [item[1] for item in hholder]
    best_score = np.max(scores)
    best_score_progress.append(best_score)
    print('Generation ' + str(generation) + '  Best Score: ' + str(best_score))
# GA has completed required generation
print('End best score, % target: ', best_score)

# Plot progress
plt.plot(best_score_progress)
plt.xlabel('Generation')
plt.ylabel('Best score (% target)')
plt.show()

print(np.argmax(scores))
save_pickle(Population, '/data/user/017024/data/GA_CC_Population2_short_time.pkl')
save_pickle(weighted_matrix, '/data/user/017024/data/GA_CC2_wm_short_time.pkl')

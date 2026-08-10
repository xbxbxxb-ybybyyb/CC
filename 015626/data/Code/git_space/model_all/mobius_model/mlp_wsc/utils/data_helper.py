import pandas as pd
from config.base import *


def get_return(ticker, bgn_date, end_date, if_save=False):
    assert ticker in ['IH', 'IF', 'IC', 'IM']
    if ticker == 'IM':
        price_fake = pd.read_hdf(im_sim_path)
        assert isinstance(price_fake, pd.Series)
        price_fake = price_fake.loc[:'20220721']  # start date = 20220722
        data = pd.read_hdf(future_path)
        assert isinstance(data, pd.DataFrame)
        data = data.xs('{}.CFE'.format(ticker), level=1)
        price_real = data['twap']
        price_real = price_real.loc['20220722':]  # start date = 20220722
        price = pd.concat([price_fake, price_real], axis=0)
    else:
        data = pd.read_hdf(future_path)
        assert isinstance(data, pd.DataFrame)
        data = data.xs('{}.CFE'.format(ticker), level=1)
        price = data['vwap']

    price = price.loc[bgn_date:end_date]
    price = price.between_time(start_time='09:30', end_time='14:56')

    # calculate return
    return_all = {}
    for t in [1, 5, 10, 20, 30, 40, 50, 60]:
        return_all[t] = price.groupby(price.index.date).apply(lambda x: x.pct_change(t, fill_method=None).shift(-1 - t))
    return_all = pd.DataFrame(return_all)

    # check data
    assert (return_all.groupby(return_all.index.date).size() == 237).all()
    if if_save:
        return_all.to_hdf(os.path.join(returnlib_path, f'{ticker}_return_{bgn_date}_{end_date}.h5'), key='a')
        return
    else:
        return return_all


def get_factor(ticker, factor_root_name, factor_list_name, bgn_date, end_date, if_save=False):
    assert factor_root_name in factor_root_dict
    assert factor_list_name in factor_list_dict

    # read factor
    factor_root_path = factor_root_dict[factor_root_name]
    temp_factor_list_path = factor_list_dict[factor_list_name]
    factor_list = []
    for file_name in pd.read_pickle(temp_factor_list_path):
        factor_path = os.path.join(factor_root_path, file_name)
        factor = pd.read_hdf(factor_path)
        assert isinstance(factor, pd.DataFrame)
        factor = factor.loc[bgn_date:end_date]
        factor = factor.between_time(start_time='09:30', end_time='14:56')
        factor_list.append(factor)
    factor_all = pd.concat(factor_list, axis=1, join='outer')

    # sort columns
    assert factor_all.columns.is_unique
    factor_all = factor_all.sort_index(axis=1, ascending=True)

    # check data
    assert (factor_all.groupby(factor_all.index.date).size() == 237).all()
    if if_save:
        os.makedirs(os.path.join(factorlib_path, ticker), exist_ok=True)
        factor_all.to_hdf(
            os.path.join(factorlib_path, ticker,
                         f'{factor_list_dict[factor_list_name].split("/")[-1].split(".")[0]}_{bgn_date}_{end_date}.h5'),
            key='a')
        return
    else:
        return factor_all


def sig_value_concat(base_root):
    result_list = list()
    temp_root_1 = sorted(os.listdir(base_root))
    for i_fold in temp_root_1:
        temp_sig_root = os.listdir(os.path.join(base_root, i_fold))
        temp_h5 = pd.concat(
            [pd.DataFrame(pd.read_hdf(os.path.join(base_root, i_fold, i))) for i in temp_sig_root]).sort_index()
        result_list.append(temp_h5)
    result_df = pd.concat(result_list, axis=1)
    result_df.columns = temp_root_1
    return result_df


def get_sig_multiseed(base_root, obj, label):
    sig_root = os.path.join(base_root, obj, str(label))
    sig_root_all = os.listdir(sig_root)
    result_list = list()
    for i in sig_root_all:
        temp_result = sig_value_concat(os.path.join(sig_root, i, 'sig_value'))
        temp_result = temp_result.add_prefix(f'{i}_')
        result_list.append(temp_result)
    result_df = pd.concat(result_list, axis=1)
    return result_df

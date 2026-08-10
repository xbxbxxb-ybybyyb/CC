import os
import pandas as pd


def main():
    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm'
    select_keys = ['IF_linear', 'IF_nonlinear', 'IF_nonlinear_diff', 'IF_181']
    factor_base = 'IF_v7_116ad_181'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm'
    select_keys = ['IC_linear', 'IC_nonlinear', 'IC_nonlinear_diff',
                   'IF_linear', 'IF_nonlinear', 'IF_nonlinear_diff', 'IF_181']
    factor_base = 'IC_v7_116ad_IF_v7_116ad_181'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm'
    select_keys = ['IM_linear', 'IM_nonlinear', 'IM_nonlinear_diff',
                   'IF_linear', 'IF_nonlinear', 'IF_nonlinear_diff', 'IF_181']
    factor_base = 'IM_v1_116ad_IF_v7_116ad_181'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    # **************************************************

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm'
    select_keys = ['IF_linear', 'IF_nonlinear', 'IF_nonlinear_diff', 'IF_181', 'IF_181_diff']
    factor_base = 'IF_v7_116ad_181ad'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm'
    select_keys = ['IC_linear', 'IC_nonlinear', 'IC_nonlinear_diff',
                   'IF_linear', 'IF_nonlinear', 'IF_nonlinear_diff', 'IF_181', 'IF_181_diff']
    factor_base = 'IC_v7_116ad_IF_v7_116ad_181ad'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm'
    select_keys = ['IM_linear', 'IM_nonlinear', 'IM_nonlinear_diff', 'IM_181', 'IM_181_diff',
                   'IF_linear', 'IF_nonlinear', 'IF_nonlinear_diff', 'IF_181', 'IF_181_diff']
    factor_base = 'IM_v1_116ad_181ad_IF_v7_116ad_181ad'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    # **************************************************

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm'
    select_keys = ['IF_linear']
    factor_base = 'IF_linear_v7'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm'
    select_keys = ['IC_linear']
    factor_base = 'IC_linear_v7'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm'
    select_keys = ['IM_linear']
    factor_base = 'IM_linear_v1'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    # **************************************************

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm'
    select_keys = ['IC_linear', 'IF_linear']
    factor_base = 'IC_linear_v7_IF_linear_v7'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)

    factor_dict_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
    factor_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm'
    select_keys = ['IM_linear', 'IF_linear']
    factor_base = 'IM_linear_v1_IF_linear_v7'
    output_root = '/dfs/user/020529/mobius_product/data/config'
    make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root)
    return None


def make_factor_list(factor_dict_path, factor_root, select_keys, factor_base, output_root):
    # print factor dict info
    print(f'read {factor_dict_path}')
    factor_dict = pd.read_pickle(factor_dict_path)
    dict_keys = list(factor_dict.keys())
    dict_keys.sort()
    for k in dict_keys:
        v = factor_dict[k]
        n = len(v)
        print(f'{k}: {n}')

    # make factor list
    factor_list = []
    for k in select_keys:
        factor_list += factor_dict[k]
    factor_list = list(set(factor_list))
    factor_list.sort()
    print(f'select {len(factor_list)} factors')

    # print factor list info
    num_factors = 0
    factor_info = []
    for k in select_keys:
        v = factor_dict[k]
        n = len(v)
        num_factors += n
        factor_info.append(f'{n}({k})')
    factor_info = ' + '.join(factor_info) + f' = {num_factors}'
    print(factor_info)
    assert len(factor_list) == num_factors, 'find duplicated factors'

    # check factor file
    for factor_file in factor_list:
        factor_path = f'{factor_root}/{factor_file}'
        assert os.path.exists(factor_path), f'{factor_path}'

    # save factor list
    output_path = f'{output_root}/{factor_base}.pkl'
    print(f'save {output_path}')
    pd.to_pickle(factor_list, output_path)
    return None


if __name__ == '__main__':
    main()

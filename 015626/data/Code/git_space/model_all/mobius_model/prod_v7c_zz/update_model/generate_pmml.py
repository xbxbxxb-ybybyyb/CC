import sys

#pip install pypmml
#pip install tensorflow==1.4.0

import subprocess

def install_pypmml_tensorflow():
    try:
        # 使用当前环境的pip进行安装
        subprocess.run([sys.executable, "-m", "pip", "install", "pypmml"], 
                      check=True) 
                      #capture_output=True,
                      #text=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "tensorflow==1.4.0"], 
                      check=True)
                      #capture_output=True,
                      #text=True)
                    
        print("安装成功！")
    except subprocess.CalledProcessError as e:
        print(f"安装失败: {e}")
        print(f"错误输出: {e.stderr}")

# 调用函数安装
install_pypmml_tensorflow()

import os
import pandas as pd
import tensorflow as tf
from pypmml import Model
from sklearn2pmml import PMMLPipeline
from sklearn2pmml import sklearn2pmml
from keras.models import load_model

from strategy.fitting_model import create_config, h5_to_pb_helper, read_pb_model_helper, pred_helper_pb_model, pred_template, pred_helper
from strategy.strategy_utility import Path, copy_folder
from ts.utility.ts_utility import read_pickle, save_pickle, read_ts_fac_helper, find_file, send_msg_link

print('tensorflow version: %s' % (str(tf.__version__)), flush=True)
if tf.__version__ != '1.4.0':
    print('tensorflow version error', flush=True)
    raise Exception

####################################################################################################

model_date = '20250328'

version_list = ['if_v7c', 'if_v7c_spot']
# version_list = ['ic_v7unifac', 'ic_v7unifac_spot']
#version_list = ['im_v1unifac', 'im_v1unifac_spot']

minute_res_root = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz/strategy/minute'
pred_index_base = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz/pred_index'
base_path = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz/model_update'
base_path_desc = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz/model_trade'

####################################################################################################

full_list = [10, 20, 30]
short_list = [1, 5, 10]
long_list = [10, 20, 30]
model_date = str(model_date)
fac_lib_date = str(model_date)
ndate = fac_lib_date

roll_name = '_r720'

for version in version_list:
    print(version, flush=True)
    if version == 'if_v7c':
        trade_contract = 'IF.CFE'
        raw_src_path = os.path.join(minute_res_root, '%s_spec/res_%s/if/prod/raw' % (version, fac_lib_date))

        model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
        model_list_long = ['lstm_cla', 'et_cla']

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'
        suffix_spec_dict = {'if_v7': ['IF_linear'],
                            'if_v7nl_181': ['IF_linear', 'IF_nonlinear', 'IF_181'],
                            'if_v7nlad_181ad': ['IF_linear', 'IF_nonlinear', 'IF_181', 'IF_nonlinear_diff', 'IF_181_diff']}

        suffix_spec_list = suffix_spec_dict['if_v7nlad_181ad']
        linear_fac_name_list = ['IF_linear']

    elif version == 'if_v7c_spot':
        trade_contract = 'IF.CFE'
        raw_src_path = os.path.join(minute_res_root, '%s_102030/res_%s/if/prod/raw' % (version, fac_lib_date))

        model_list_short = []
        model_list_long = ['lstm_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'
        suffix_spec_dict = {'if_v7': ['IF_linear'],
                            'if_v7nl_181': ['IF_linear', 'IF_nonlinear', 'IF_181'],
                            'if_v7nlad_181ad': ['IF_linear', 'IF_nonlinear', 'IF_181', 'IF_nonlinear_diff', 'IF_181_diff']}

        suffix_spec_list = suffix_spec_dict['if_v7nlad_181ad']
        linear_fac_name_list = ['IF_linear']

    elif version == 'ic_v7unifac':
        trade_contract = 'IC.CFE'
        raw_src_path = os.path.join(minute_res_root, '%s_spec/res_%s/ic/prod/raw' % (version, fac_lib_date))

        model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
        model_list_long = ['lstm_cla', 'et_cla']

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'

        suffix_spec_dict = {'ic_v7_if_v7': ['IC_linear', 'IF_linear'],
                            'ic_v7nl_if_v7nl_181': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181'],
                            'ic_v7nlad_if_v7nlad_181ad': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181', 'IC_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['ic_v7nlad_if_v7nlad_181ad']
        linear_fac_name_list = ['IC_linear', 'IF_linear']

    elif version == 'ic_v7unifac_spot':
        trade_contract = 'IC.CFE'
        raw_src_path = os.path.join(minute_res_root, '%s_102030/res_%s/ic/prod/raw' % (version, fac_lib_date))

        model_list_short = []
        model_list_long = ['lstm_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'

        suffix_spec_dict = {'ic_v7_if_v7': ['IC_linear', 'IF_linear'],
                            'ic_v7nl_if_v7nl_181': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181'],
                            'ic_v7nlad_if_v7nlad_181ad': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181', 'IC_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff']}

        suffix_spec_list = suffix_spec_dict['ic_v7nlad_if_v7nlad_181ad']
        linear_fac_name_list = ['IC_linear', 'IF_linear']

    elif version == 'im_v1unifac':
        trade_contract = 'IM.CFE'
        raw_src_path = os.path.join(minute_res_root, '%s_spec/res_%s/im/prod/raw' % (version, fac_lib_date))

        model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
        model_list_long = ['lstm_cla', 'et_cla']

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm/'

        suffix_spec_dict = {'im_v1_if_v7_2': ['IM_linear', 'IF_linear'],
                            'im_v1nl_181_if_v7_2nl_181': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IM_181', 'IF_181'],
                            'im_v1nlad_181ad_if_v7_2nlad_181ad': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']}
        suffix_spec_list = ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']
        linear_fac_name_list = ['IM_linear', 'IF_linear']

    elif version == 'im_v1unifac_spot':
        trade_contract = 'IM.CFE'
        raw_src_path = os.path.join(minute_res_root, '%s_102030/res_%s/im/prod/raw' % (version, fac_lib_date))

        model_list_short = []
        model_list_long = ['lstm_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm/'

        suffix_spec_dict = {'im_v1_if_v7_2': ['IM_linear', 'IF_linear'],
                            'im_v1nl_181_if_v7_2nl_181': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IM_181', 'IF_181'],
                            'im_v1nlad_181ad_if_v7_2nlad_181ad': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']}
        suffix_spec_list = ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']
        linear_fac_name_list = ['IM_linear', 'IF_linear']

    else:
        raise RuntimeError('version error')

    with_desc = True

    trade_ini = trade_contract.split('.')[0].lower()
    model_date_use = '%s_%s_%s' % (model_date, trade_ini, version)
    model_list = model_list_long + model_list_short
    hpr_spec_dict = {**{i: long_list for i in model_list_long},
                     **{i: short_list for i in model_list_short}}

    fac_ref = read_pickle(fac_ref_path)
    sub_list = list(fac_ref.keys())
    sub_list.sort()
    for i in sub_list:
        print('%s : %d' % (i, len(fac_ref[i])), flush=True)

    fac_list, linear_fac_list = [], []
    for suffix_itr in suffix_spec_list:
        fac_list_itr = [i.replace('.h5', '') for i in fac_ref[suffix_itr]]
        fac_list = fac_list + fac_list_itr
        if suffix_itr in linear_fac_name_list:
            linear_fac_list = linear_fac_list + fac_list_itr
    print(len(linear_fac_list), len(fac_list), flush=True)
    fac_val = read_ts_fac_helper(path_ever, fac_list=fac_list).fillna(0)
    fac = fac_val[linear_fac_list]
    fac_num = fac_val.shape[1]
    fac_num_linear = len(linear_fac_list)
    fac_num_nl = fac_num - fac_num_linear
    print('total fac:%d | linear:%d | nonlinear:%d' % (fac_num, fac_num_linear, fac_num_nl), flush=True)

    print(version, flush=True)
    print(fac_val.shape, flush=True)
    print(fac_val.index[0], fac_val.index[-1], flush=True)

    prob_fac_list = ['MinuteIndexHighLowCorrMeanSharpeDiff']
    fac_list = fac_val.columns
    fac_list_use = [i for i in fac_val.columns if i not in prob_fac_list]
    print(version, len(fac_list), len(fac_list_use), flush=True)
    fac_val = fac_val[fac_list_use]

    model_list_dl = ['lstm_cla', 'mlp_reg', 'mlp_cla', 'crn_cla', 'crn_reg']
    slice_range_extra = [[931, 1129], [1300, 1456]]

    raw_dsc_path = os.path.join(base_path, '%s/model_value/model_raw/%s' % (model_date_use, fac_lib_date))
    pa_root = os.path.join(pred_index_base, 'minute/%s_prod/res_%s/%s/model_prod' % (version, model_date, trade_ini.upper()))

    mf_path = os.path.join(base_path, model_date_use, 'model_file')  # pkl path
    mt_path = os.path.join(base_path, model_date_use, 'model_trade', model_date_use)  # pb/pmml file
    mt_path_desc = os.path.join(base_path_desc, model_date_use)
    mv_path = os.path.join(base_path, model_date_use, 'model_value')
    factor_name_path = os.path.join(mt_path, 'factor_name_mapping.csv')
    config_path = os.path.join(mt_path, 'model_config.json')

    file_list = [base_path, raw_dsc_path, pa_root, mf_path, mt_path, mv_path, base_path_desc, mt_path_desc]

    print('*** create folder ***', flush=True)
    for file_root in file_list:
        print(file_root, flush=True)
        if not os.path.exists(file_root):
            os.makedirs(file_root)

    print('*** data from the following path ***', flush=True)
    print(pa_root, flush=True)

    print('*** migrate history raw ***', flush=True)
    
    raw_src_pd = find_file(raw_src_path, 'pkl')
    if len(raw_src_pd) != len(model_list):
        print(raw_src_path)
        print(raw_src_pd)
        print(model_list)
        raise Exception
    for k in raw_src_pd:
        print(k, flush=True)
        val_tmp = read_pickle(raw_src_pd[k])
        val_tmp.columns = [i.replace('_r240', '').replace('_r720', '') for i in val_tmp.columns]
        save_pickle(val_tmp, os.path.join(raw_dsc_path, '%s.pkl' % (k)))

    fold_list_dict = {**{i: [0, 1, 2, 3, 4] for i in ['lasso_reg', 'lr_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'lstm_cla', 'mlp_reg', 'mlp_cla']},
                      **{i: [0] for i in ['rff_cla', 'rfe_cla']},
                      **{i: [i for i in range(25)] for i in ['crn_cla', 'crn_reg']}}
    create_config(config_path, hpr_spec_dict, fold_list_dict)

    print('prep fitting x', flush=True)
    dummy_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
    dummy = read_ts_fac_helper(dummy_path)
    dummy2 = dummy.copy()
    dummy2.columns = [i + '.0' for i in dummy.columns]
    dummy_use = pd.concat([dummy, dummy2], axis=1)
    x_test = pd.concat([fac_val, dummy_use], axis=1)
    x_test = x_test.loc[ndate:].fillna(0)

    fi_meta = pd.DataFrame(['x%d' % (i) for i in range(1, x_test.shape[1] + 1)], index=x_test.columns)
    fi_meta.index.names = ['factor_name']
    fi_meta.columns = ['model_input_name']
    fi_meta.to_csv(factor_name_path)
    print(factor_name_path, flush=True)

    ####################################
    fi_format_new = True
    check_time = False
    return_itr = True
    get_prediction = True

    print(model_list, flush=True)
    for model in model_list:
        mt_path_itr = os.path.join(mt_path, model)
        mf_path_itr = os.path.join(mf_path, model)
        mv_path_itr = os.path.join(mv_path, 'model_raw_itr', model_date)
        file_list = [mt_path_itr, mf_path_itr]
        [os.makedirs(i, exist_ok=True) for i in file_list]
        pred = 'regression' if model.find('reg') >= 0 else 'classification'
        holding_period_list = hpr_spec_dict[model]
        for holding_period in holding_period_list:
            print(model, holding_period)
            pa_path = os.path.join(pa_root, model, '%s_%d%s.pkl' % (model, holding_period, roll_name))
            pkl_path = os.path.join(mf_path_itr, '%s_%d%s.pkl' % (model, holding_period, roll_name))
            raw_itr_path = os.path.join(mv_path_itr, '%s_%d.pkl' % (model, holding_period))

            md = read_pickle(pa_path)
            save_pickle(md, pkl_path)

            model_dict = md['model']
            tl = list(model_dict.keys())
            tl.sort()
            ts_itr = tl[-1]
            print('model trained on %s' % (ts_itr), flush=True)
            fi = md['feature_importance']
            kl = list(fi.keys())
            fold_list_itr = list(model_dict[ts_itr].keys())
            ll = []
            pred_raw_itr_list = []
            pred_raw_itr_list2 = []
            for fold in fold_list_itr:
                pmml_path = os.path.join(mt_path_itr, '%s_%d_%d.pmml' % (model, holding_period, fold))
                fi_path = os.path.join(mt_path_itr, '%s_%d_%d.csv' % (model, holding_period, fold))
                fi_itr = fi[ts_itr][fold].copy()
                if fi_format_new:
                    fi_itr.index.names = ['factor_name']
                    fi_itr.columns = ['model_input_name']
                    fi_itr['model_input_name'] = ['x%d' % (i) for i in range(1, len(fi_itr) + 1)]
                    fi_itr['mapping'] = [fi_meta.loc[i].values[0] for i in fi_itr.index]
                fi_itr.to_csv(fi_path)
                need_list = fi_itr.index.tolist()

                if model in model_list_dl:
                    pb_path = os.path.join(mt_path_itr, '%s_%d_%d.pb' % (model, holding_period, fold))
                    h5_path = os.path.join(mt_path_itr, '%s_%d_%d.h5' % (model, holding_period, fold))
                    h5_path_orig = model_dict[ts_itr][fold]
                    Path(h5_path).parent.mkdir(parents=True, exist_ok=True)
                    model_h5 = load_model(h5_path_orig)
                    model_h5.save(h5_path)  # should delete h5 / upward folder
                    h5_to_pb_helper(h5_path, pb_path)  # save keras model from h5 to pb
                    pb_obj = read_pb_model_helper(pb_path)  # read model from pb, create session
                    if get_prediction:
                        pred_raw_itr_fold = pred_helper_pb_model(pb_obj, x_test)  # keras model to predict
                        pred_raw_itr_list.append(pred_raw_itr_fold)
                else:
                    model_dict_itr = model_dict[ts_itr]
                    model_obj = model_dict_itr[fold]
                    model_pmml = PMMLPipeline([(model, model_obj)])
                    sklearn2pmml(model_pmml, pmml_path, with_repr=True)
                    print(pmml_path, flush=True)
                    if get_prediction:
                        mp_itr = Model.fromFile(pmml_path)
                        pred_pml_itr = pred_template(x_test[need_list], model_pmml, pred)
                        pred_pkl_itr = pred_template(x_test[need_list], model_obj, pred)
                        pred_raw_itr_list.append(pred_pml_itr)

            pred_res_itr_df_pml = pd.concat(pred_raw_itr_list, axis=1)
            pred_res_itr_df_pml.columns = fold_list_itr
            pred_raw_itr_pml = pred_res_itr_df_pml.mean(axis=1)

            pred_raw_itr, pred_res_itr_df = pred_helper(x_test, md, pred=pred,
                                                        check_time=check_time, return_itr=return_itr,
                                                        res_base_path=pa_path)
            pred_diff_pkl_pml = (pred_res_itr_df - pred_res_itr_df_pml).abs().sum().sum()
            if pred_diff_pkl_pml > 1e-5:
                print('error', flush=True)
                print(pred_diff_pkl_pml, flush=True)
                raise Exception
            else:
                print('%s ~ pml & pkl prediction matched' % (model), flush=True)

            save_pickle(pred_res_itr_df, raw_itr_path)
            print('moving history prediction to desc folder', flush=True)

    print('migrate to prod file', flush=True)
    print(mt_path, flush=True)
    print(mt_path_desc, flush=True)
    copy_folder(mt_path, mt_path_desc)
    print('all done', flush=True)
    send_msg_link('%s_%s done ' % (version, model_date))
send_msg_link('%s_%s all done ' % ('model pmml ', model_date))

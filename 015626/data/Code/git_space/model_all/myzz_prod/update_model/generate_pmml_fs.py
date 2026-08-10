import sys

sys.path.insert(0, '/data/user/015626/data/Code/git_space/model_all/mobius_model/myzz_prod/')

# pip install pypmml
# pip install tensorflow==1.4.0

import os
import pandas as pd
import tensorflow as tf
from shutil import copyfile
from pypmml import Model
from sklearn2pmml import PMMLPipeline
from sklearn2pmml import sklearn2pmml
from keras.models import load_model

from strategy.fitting_model import create_config, h5_to_pb_helper, read_pb_model_helper, pred_helper_pb_model, pred_template, pred_helper, change_h5_path_helper
from strategy.strategy_utility import Path, copy_folder
from ts.utility.ts_utility import read_pickle, save_pickle, prep_ps2df_save, slice_by_minute, read_ts_fac_helper, find_file, send_msg_link

print('tensorflow version: %s' % (str(tf.__version__)), flush=True)
if tf.__version__ != '1.4.0':
    print('tensorflow version error', flush=True)
    raise Exception

####################################################################################################

edate = '20250328'

# suffix = 'if_v7c'
# suffix = 'ic_v7unifac'
suffix = 'im_v1unifac'

version_list = ['%s_fs' % (suffix)]

minute_base = '/data/user/015626/model/mobius_prod_zz/strategy/minute'
pred_index_base = '/data/user/015626/model/mobius_prod_zz/pred_index'
base_path = '/data/user/015626/model/mobius_prod_zz/model_update'
base_path_desc = '/data/user/015626/model/mobius_prod_zz/model_trade'

####################################################################################################

long_list = [10, 20, 30]
short_list = [1, 5, 10]
model_list_dl = ['mlp_cla', 'mlp_reg', 'lstm_cla', 'lstm_reg']
update_date = edate
filter_date = 'prod'
model_date = edate
model_date = str(model_date)
fac_lib_date = str(model_date)
ndate = fac_lib_date

if suffix == 'if_v7c':
    trade_contract = 'IF.CFE'
elif suffix == 'ic_v7unifac':
    trade_contract = 'IC.CFE'
elif suffix == 'im_v1unifac':
    trade_contract = 'IM.CFE'
else:
    raise RuntimeError('suffix error')

model_list_long = ['lstm_cla', 'et_cla']
model_list_short = ['lgbm_cla', 'lgbm_reg', 'mlp_reg']
future_hpr_spec_dict = {**{i: long_list for i in model_list_long},
                        **{i: short_list for i in model_list_short}}

model_list_long = ['lstm_cla', 'et_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg']
model_list_short = []
model_list = model_list_long + model_list_short
spot_hpr_spec_dict = {**{i: long_list for i in model_list_long},
                      **{i: short_list for i in model_list_short}}
hpr_spec_dict = {'future': future_hpr_spec_dict, 'spot': spot_hpr_spec_dict}

suffix_save_dict = {'future': '%s_spec' % (suffix), 'spot': '%s_spot_102030' % (suffix), 'fs': '%s_fs' % (suffix)}
suffix_pred_index_dict = {'future': suffix, 'spot': '%s_spot' % (suffix), 'fs': '%s_fs' % (suffix)}

ticker_ini = trade_contract.split('.')[0].lower()
pdd = {}
for suffix_itr in suffix_save_dict:
    suffix = suffix_pred_index_dict[suffix_itr]

    suffix_save = suffix_save_dict[suffix_itr]
    backtest_root = os.path.join(minute_base, '%s' % (suffix_save))
    save_base = os.path.join(minute_base, '%s/res_%s/%s/%s' % (suffix_save, update_date, ticker_ini, filter_date))
    pred_res_base = os.path.join(pred_index_base, 'minute/%s_%s' % (suffix, filter_date))

    prod_save_path = os.path.join(save_base, 'norm', )
    prod_save_path_nd = os.path.join(save_base, 'norm_nd')
    prod_save_raw_path = os.path.join(save_base, 'raw')
    model_root_dict = {model: os.path.join(pred_res_base, 'res_%s/%s/model_%s/%s' % (model_date, trade_contract[:2], filter_date, model)) for model in model_list}

    pdd[suffix_itr] = {'prod_save_path_nd': prod_save_path_nd, 'prod_save_raw_path': prod_save_raw_path, 'pred_res_base': pred_res_base, 'model_root_dict': model_root_dict}

    if suffix_itr == 'fs':
        os.makedirs(prod_save_path_nd) if not os.path.exists(prod_save_path_nd) else None
        os.makedirs(prod_save_raw_path) if not os.path.exists(prod_save_raw_path) else None
        os.makedirs(pred_res_base) if not os.path.exists(pred_res_base) else None

ret_label_list = ['future', 'spot']
pad_raw = find_file(pdd['fs']['prod_save_raw_path'], 'pkl')

for ret_label in ret_label_list:
    print(ret_label, flush=True)

    pad_nd_itr = find_file(pdd[ret_label]['prod_save_path_nd'], 'h5')
    pad_raw_itr = find_file(pdd[ret_label]['prod_save_raw_path'], 'pkl')
    comb_list = ['pred_comb', 'pred_comb2']
    model_list2 = model_list + comb_list
    for model in model_list2:
        ## nd
        path_src_itr = pad_nd_itr[model]
        path_des_itr = os.path.join(pdd['fs']['prod_save_path_nd'], '%s_%s.h5' % (model, ret_label))
        os.remove(path_des_itr) if os.path.exists(path_des_itr) else None
        copy_folder(path_src_itr, path_des_itr)
        if model not in comb_list:
            ## raw
            pkl_des_itr = os.path.join(pdd['fs']['prod_save_raw_path'], '%s_%s.pkl' % (model, ret_label))
            res_itr = read_pickle(pad_raw_itr[model])
            res_itr.columns = [model + '_%s' % (ret_label) + i.split(model)[1] for i in res_itr.columns]
            save_pickle(res_itr, pkl_des_itr)

            pad_index_itr = pdd[ret_label]['model_root_dict']
            pad_index_desc_itr = pdd['fs']['model_root_dict']

            # pred_index
            hpr_list = hpr_spec_dict[ret_label][model]
            pdd_index_itr = find_file(pad_index_itr[model], 'pkl')
            for hp_itr in hpr_list:
                name_str = '%s_%s_r720' % (model, hp_itr)
                name_str_desc = '%s_%s_%s_r720' % (model, ret_label, hp_itr)
                path_pred_index_src_itr = pdd_index_itr[name_str]
                pred_index_root_desc_str = pad_index_desc_itr[model].replace(model, '%s_%s' % (model, ret_label))
                os.makedirs(pred_index_root_desc_str) if not os.path.exists(pred_index_root_desc_str) else None

                path_pred_index_des_itr = os.path.join(pred_index_root_desc_str, '%s.pkl' % (name_str_desc))
                os.remove(path_pred_index_des_itr) if os.path.exists(path_pred_index_des_itr) else None

                copy_folder(path_pred_index_src_itr, path_pred_index_des_itr)

                if model in model_list_dl:
                    copy_folder(path_pred_index_src_itr.replace('.pkl', ''), path_pred_index_des_itr.replace('.pkl', ''))

ret_label = 'future'
comb_name = 'pred_comb2'
path_des_itr1 = os.path.join(pdd['fs']['prod_save_path_nd'], '%s_%s.h5' % (comb_name, 'future'))
path_des_itr2 = os.path.join(pdd['fs']['prod_save_path_nd'], '%s_%s.h5' % (comb_name, 'spot'))
path_des_itr3_root = pdd['fs']['prod_save_path_nd']

pred_comb2_future = pd.read_hdf(path_des_itr1)
pred_comb2_spot = pd.read_hdf(path_des_itr2)
pred_comb2 = (pred_comb2_future + pred_comb2_spot) / 2
min_pct_tail = 0.8
pred_comb2 = prep_ps2df_save(pred_comb2, comb_name, save_path=path_des_itr3_root, min_pct=min_pct_tail)

#########################################################################################

model_list_onnx = ['crn_cla', 'crn_reg']
roll_name = '_r720'

model_list_dl_base = ['lstm_cla', 'mlp_reg', 'mlp_cla']
model_list_dl = [i + '_future' for i in model_list_dl_base] + [i + '_spot' for i in model_list_dl_base]
for version in version_list:
    print(version, flush=True)
    if version in ['if_v7c_fs']:
        trade_contract = 'IF.CFE'
        trade_ini = trade_contract.split('.')[0].lower()
        model_date_use = '%s_%s_%s' % (model_date, trade_ini, version)
        raw_src_path = os.path.join(minute_base, '%s/res_%s/if/prod/raw' % (version, fac_lib_date))
        with_desc = True
        model_list_short = ['lgbm_cla_future', 'lgbm_reg_future', 'mlp_reg_future']
        model_list_long = ['lstm_cla_future', 'et_cla_future', 'lstm_cla_spot', 'et_cla_spot', 'lgbm_cla_spot', 'lgbm_reg_spot', 'mlp_reg_spot']

        model_list = model_list_long + model_list_short
        hpr_spec_dict = {**{i: long_list for i in model_list_long},
                         **{i: short_list for i in model_list_short}}
        ###############
        # if 
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])))

        suffix_spec_dict = {'if_v7': ['IF_linear'],
                            'if_v7nl_181': ['IF_linear', 'IF_nonlinear', 'IF_181'],
                            'if_v7nlad_181ad': ['IF_linear', 'IF_nonlinear', 'IF_181', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['if_v7nlad_181ad']
        linear_fac_name_list = ['IF_linear']

    elif version in ['ic_v7unifac_fs']:
        trade_contract = 'IC.CFE'
        trade_ini = trade_contract.split('.')[0].lower()
        model_date_use = '%s_%s_%s' % (model_date, trade_ini, version)
        raw_src_path = os.path.join(minute_base, '%s/res_%s/ic/prod/raw' % (version, fac_lib_date))
        with_desc = True
        model_list_short = ['lgbm_cla_future', 'lgbm_reg_future', 'mlp_reg_future']
        model_list_long = ['lstm_cla_future', 'et_cla_future', 'lstm_cla_spot', 'et_cla_spot', 'lgbm_cla_spot', 'lgbm_reg_spot', 'mlp_reg_spot']

        model_list = model_list_long + model_list_short
        hpr_spec_dict = {**{i: long_list for i in model_list_long},
                         **{i: short_list for i in model_list_short}}

        #################
        # ic         
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])))

        suffix_spec_dict = {'ic_v7_if_v7': ['IC_linear', 'IF_linear'],
                            'ic_v7nl_if_v7nl_181': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181'],
                            'ic_v7nlad_if_v7nlad_181ad': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181', 'IC_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff']}
        suffix_spec_list = suffix_spec_dict['ic_v7nlad_if_v7nlad_181ad']
        linear_fac_name_list = ['IC_linear', 'IF_linear']

    elif version in ['im_v1unifac_fs']:
        trade_contract = 'IM.CFE'
        trade_ini = trade_contract.split('.')[0].lower()
        model_date_use = '%s_%s_%s' % (model_date, trade_ini, version)
        raw_src_path = os.path.join(minute_base, '%s/res_%s/im/prod/raw' % (version, fac_lib_date))
        with_desc = True
        model_list_short = ['lgbm_cla_future', 'lgbm_reg_future', 'mlp_reg_future']
        model_list_long = ['lstm_cla_future', 'et_cla_future', 'lstm_cla_spot', 'et_cla_spot', 'lgbm_cla_spot', 'lgbm_reg_spot', 'mlp_reg_spot']

        model_list = model_list_long + model_list_short
        hpr_spec_dict = {**{i: long_list for i in model_list_long},
                         **{i: short_list for i in model_list_short}}

        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm/'

        fac_ref = read_pickle(fac_ref_path)
        sub_list = list(fac_ref.keys())
        sub_list.sort()
        for i in sub_list:
            print('%s : %d' % (i, len(fac_ref[i])))

        suffix_spec_dict = {'im_v1_if_v7_2': ['IM_linear', 'IF_linear'],
                            'im_v1nl_181_if_v7_2nl_181': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IM_181', 'IF_181'],
                            'im_v1nlad_181ad_if_v7_2nlad_181ad': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']}
        suffix_spec_list = ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']
        linear_fac_name_list = ['IM_linear', 'IF_linear']

    ##############################################################################################################

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

    model_list_extra = ['rff_cla', 'rfe_cla']
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
        print(file_root)
        if not os.path.exists(file_root):
            os.makedirs(file_root)

    print('*** data from the following path ***', flush=True)
    print(pa_root, flush=True)

    print('*** migrate history raw ***', flush=True)
    raw_src_pd = find_file(raw_src_path, 'pkl')
    if len(raw_src_pd) != len(model_list):
        raise Exception
    for k in raw_src_pd:
        print(k, flush=True)
        val_tmp = read_pickle(raw_src_pd[k])
        val_tmp.columns = [i.replace('_r240', '').replace('_r720', '') for i in val_tmp.columns]
        save_pickle(val_tmp, os.path.join(raw_dsc_path, '%s.pkl' % (k)))

    fold_list_dict = {**{i: [0, 1, 2, 3, 4] for i in model_list},
                      **{i: [0] for i in ['rff_cla', 'rfe_cla']},
                      **{i: [i for i in range(25)] for i in ['crn_cla', 'crn_reg']}}
    create_config(config_path, hpr_spec_dict, fold_list_dict, model_list_dl=model_list_dl)

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
            print(model, holding_period, flush=True)
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
                    if model in model_list_onnx:
                        onnx_path = os.path.join(mt_path_itr, '%s_%d_%d.onnx' % (model, holding_period, fold))
                        onnx_path_srcs = change_h5_path_helper(h5_path_orig, pa_path)
                        copyfile(onnx_path_srcs, onnx_path)
                    else:
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
                    print(pmml_path)
                    if get_prediction:
                        mp_itr = Model.fromFile(pmml_path)
                        pred_pml_itr = pred_template(x_test[need_list], model_pmml, pred)
                        pred_pkl_itr = pred_template(x_test[need_list], model_obj, pred)
                        pred_raw_itr_list.append(pred_pml_itr)

            if model in model_list_onnx:
                if get_prediction:
                    pred_raw_itr_pml, pred_res_itr_df_pml = pred_helper(x_test, md, pred=pred, check_time=check_time, return_itr=return_itr, res_base_path=pa_path)
            else:
                pred_res_itr_df_pml = pd.concat(pred_raw_itr_list, axis=1)
                pred_res_itr_df_pml.columns = fold_list_itr
                pred_raw_itr_pml = pred_res_itr_df_pml.mean(axis=1)

            pred_raw_itr, pred_res_itr_df = pred_helper(x_test, md, pred=pred, check_time=check_time, return_itr=return_itr, res_base_path=pa_path)
            pred_diff_pkl_pml = (pred_res_itr_df - pred_res_itr_df_pml).abs().sum().sum()
            if pred_diff_pkl_pml > 1e-5:
                print('error', flush=True)
                print(pred_diff_pkl_pml, flush=True)
                raise Exception
            else:
                print('%s ~ pml & pkl prediction matched' % (model), flush=True)
            if model in model_list_extra:
                dt_list_orig = pred_raw_itr.index.tolist()
                pred_raw_itr = slice_by_minute(pred_raw_itr, slice_range_extra).reindex(dt_list_orig)
                dt_list_orig = pred_res_itr_df.index.tolist()
                pred_res_itr_df = slice_by_minute(pred_res_itr_df, slice_range_extra).reindex(dt_list_orig)

            save_pickle(pred_res_itr_df, raw_itr_path)
            print('moving history prediction to desc folder', flush=True)

    print('migrate to prod file', flush=True)
    print(mt_path, flush=True)
    print(mt_path_desc, flush=True)
    copy_folder(mt_path, mt_path_desc)
    print('all done', flush=True)
    send_msg_link('%s_%s done ' % (version, model_date))
send_msg_link('%s_%s all done ' % ('model pmml ', model_date))

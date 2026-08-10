import csv
import torch
import shutil
from config.dnn import *
from config.base import *
from models.runner import NNModelWSC
from utils.logger_wsc import LoggerMyself
from utils.help_functions_wsc import torch_seed_set, save_pickle


def train(rolling_range, ret_target_g, obj_name, cv_num_selected, random_seed,
          x_path, y_path, factorlib_name, model_name, sig_name, get_onnx=False):
    torch_seed_set(random_seed)
    train_range = rolling_range[0]
    predict_range = rolling_range[1]
    train_range_str = train_range[0].strftime('%Y%m%d') + '_' + train_range[1].strftime('%Y%m%d')
    predict_range_str = predict_range[0].strftime('%Y%m%d') + '_' + predict_range[1].strftime('%Y%m%d')

    save_root = os.path.join(model_save_path, factorlib_name, model_name, obj_name, str(ret_target_g), str(random_seed))
    save_root_factor_value = os.path.join(save_root, 'sig_value', str(cv_num_selected))
    save_root_model = os.path.join(save_root, 'model', str(cv_num_selected))
    save_root_log = os.path.join(save_root, 'log', str(cv_num_selected))
    os.makedirs(save_root, exist_ok=True)
    os.makedirs(save_root_factor_value, exist_ok=True)
    os.makedirs(save_root_model, exist_ok=True)
    os.makedirs(save_root_log, exist_ok=True)
    logger = LoggerMyself(f'log_{predict_range_str}.log', save_root_log)

    if not os.path.exists(os.path.join(save_root_factor_value, f'{predict_range_str}.h5')):
        model_temp = NNModelWSC(
            x_path=x_path, y_path=y_path, logger_used=logger, objective=obj_name, model=model_name,
            model_params=model_params, obj_params=obj_params, training_params=training_params,
            ret_target=ret_target_g, insample_range=train_range, outsample_range=predict_range,
            cv_num_selected=cv_num_selected, **processing_params)
        model_dict = vars(model_temp)

        logger.info(f'factorlib name: {factorlib_name}, model name: {model_name}, '
                    f'objective name: {obj_name}, ret target: {ret_target_g}, \n '
                    f'train_range: {train_range_str}, predict_range: {predict_range_str}, '
                    f'cv_num_selected: {cv_num_selected}, random_seed: {random_seed}', outputs='both')
        logger.info(f'model arguments: {model_dict}', outputs='file')
        model_temp.fit()
        y_predict = model_temp.predict()
        y_model = model_temp.model.cpu()
        y_predict.to_hdf(os.path.join(save_root_factor_value, f'{predict_range_str}.h5'), key='y_predict')
        save_pickle(y_model, os.path.join(save_root_model, f'{predict_range_str}.pth'), protocol_level='default')
        save_pickle(y_model.state_dict(), os.path.join(save_root_model, f'{predict_range_str}_state_dict.pkl'),
                    protocol_level='default')

        # get onnx&csv
        if get_onnx:
            y_model.eval()
            factor_list = model_temp.feature_names.tolist()
            temp_x = torch.randn(size=(1, len(factor_list)))
            onnx_root_1 = os.path.join(prod_share_path, 'model_trade',
                                       f'{sig_name}_{factorlib_name[:2]}_{factorlib_name}', f'{model_name}_{obj_name}')
            onnx_root_2 = os.path.join(prod_share_path, 'model_update',
                                       f'{sig_name}_{factorlib_name[:2]}_{factorlib_name}', 'model_trade',
                                       f'{sig_name}_{factorlib_name[:2]}_{factorlib_name}', f'{model_name}_{obj_name}')
            os.makedirs(onnx_root_1, exist_ok=True)
            os.makedirs(onnx_root_2, exist_ok=True)
            onnx_csv_name = f'{model_name}_{obj_name}_{ret_target_g}_' \
                f'{random_seed_dict[random_seed] * processing_params["cv_num"] + cv_num_selected}'
            onnx_path_1 = os.path.join(onnx_root_1, onnx_csv_name + '.onnx')
            onnx_path_2 = os.path.join(onnx_root_2, onnx_csv_name + '.onnx')
            csv_path_1 = os.path.join(onnx_root_1, onnx_csv_name + '.csv')
            csv_path_2 = os.path.join(onnx_root_2, onnx_csv_name + '.csv')
            torch.onnx.export(y_model, temp_x, onnx_path_1)
            with open(csv_path_1, mode='w', encoding='utf-8') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(['factor_name', 'model_input_name'])
                for idx, fac in enumerate(factor_list):
                    csv_writer.writerow([fac, f'x{idx}'])
            shutil.copy(onnx_path_1, onnx_path_2)
            shutil.copy(csv_path_1, csv_path_2)
        del model_temp

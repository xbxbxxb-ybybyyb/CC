import sys, json, os, importlib
import concurrent.futures
import logging
import numpy as np
import onnx, copy, time
import onnxruntime as ort
import pandas as pd

def add_file_logger(name, level=None, file_name=None, mode='a',
                    format_str ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    lazy_mode=False, void_flag=False):
    if void_flag:  # multiprocessing dummy
        return VoidLogger()
    logger = logging.getLogger(name)
    if lazy_mode:
        return logger
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.DEBUG)
    if file_name is not None:
        # if not logger.hasHandlers():
        _dirname = os.path.dirname(file_name)
        if len(_dirname) != 0 and not os.path.exists(_dirname):
            os.makedirs(_dirname)
        file_handler = logging.FileHandler(file_name, mode=mode)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)
    else:
        # if not logger.hasHandlers():
            # default to screen
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(stream_handler)
    return logger
    
def concurrent_apply_func(func, input_list, max_workers, logger=None, debug_mode=False,
                          process_type='multiprocess', logger_callback=None,
                          collect_results=True, void_log_flag=False, **kwargs):
    # apply func to input list as first argument in a concurrent way
    assert callable(func)
    assert isinstance(max_workers, int)
    assert isinstance(input_list, list) or isinstance(input_list, tuple)
    total_jobs = len(input_list)
    result_collector = dict()
    if process_type == 'multithread':
        _executor = concurrent.futures.ThreadPoolExecutor
    elif process_type == 'multiprocess':
        _executor = concurrent.futures.ProcessPoolExecutor
    else:
        raise NotImplementedError
    if logger is None:
        logger = add_file_logger('concurrent', void_flag=void_log_flag)  # dummy logger to stream to screen
    if debug_mode:
        # pdb into func source code should work
        for _file in input_list:
            data = func(_file, **kwargs)
            if data is not None and collect_results:
                result_collector[_file] = data
    else:
        with _executor(max_workers=max_workers) as executor:
            future_dict = {executor.submit(func, _file, **kwargs): _file for _file in input_list}
            logger.info('executor submit finish')
            for _future in concurrent.futures.as_completed(future_dict):
                _file = future_dict[_future]
                current_job = input_list.index(_file) + 1
                try:
                    data = _future.result()
                except Exception as _exp:
                    logger.warning(f'worker raised {_exp}, the input is {_file}')
                    data = None
                del future_dict[_future]
                del _future
                # load results into collector
                if data is not None and collect_results:
                    try:
                        result_collector[_file] = data
                    except TypeError:
                        result_collector[pd.Timestamp.now()] = data
                if logger_callback is not None:
                    assert callable(logger_callback)
                    msg = logger_callback(_file, data)
                    if data is not None:
                        logger.info('%d/%d - %s' % (current_job, total_jobs, msg))
                    else:
                        logger.warning('%d/%d - %s' % (current_job, total_jobs, msg))
                else:
                    # logger.info('%d/%d - processed' % (current_job, total_jobs))
                    pass
        logger.info('executor finished')
    if collect_results:
        return result_collector

def calc_norm(blist, window, method = 'ts_rank'):
    alist = np.array(blist[-1 * window:])
    if np.count_nonzero(~np.isnan(alist)) < window // 2:
        return np.nan
    if method == 'calc_zscore':
        _mean = np.nanmean(alist)
        _std = np.nanstd(alist, ddof = 1)
        return (alist[-1] - _mean) / _std
    elif method == 'ts_rank':
        x = alist[-1]
        n = len(alist)
        L = np.sum(alist < x)  
        E = np.sum(alist == x) 
        p_avg = L + (E + 1) / 2.0
        rank = (p_avg - 1) / (n - 1)
        return rank * 2 - 1
    
class TorusProduction(object):
    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.date = config['trading_date']
        self.ticker = config['ticker']
        self.contract_main = config['contract_main']
        self.contract_second_main = config['contract_second_main']
        self.parallel_num = config['parallel_num']
        self.model_file_path = config['model_file_path']
        self.model_name_dict = config['model_name_dict']
        self.result_save_path = config['result_save_path']
        self.pre_trade_data_path = config['pre_trade_data_path']
        self.pre_trade_factor_path = config['pre_trade_factor_path']
        self.pre_trade_norm_factor_path = config['pre_trade_norm_factor_path']
        self.model_rank_lenth_dict = config['model_rank_lenth_dict']

        self.data_gentime = config['data_gentime']
        self.prod_data_path = config['prod_data_path']

        self.factor_path = config['factor_path']
        self.factor_freq = config['factor_freq']

        self.pre_trade_model_path = config['pre_trade_model_path']

        self.logger = add_file_logger(f'TorusProduction_{self.ticker}', file_name = os.path.join(config['log_file_path'], f'{self.date}_{self.ticker}.log'))

    def load_data(self):
        self.logger.info('loading data...')
        with open(self.pre_trade_data_path, "r", encoding="utf-8") as f:
            self.his_data = json.load(f)
        for freq in [1,3,5,15]:
            for col in self.his_data[str(freq)].keys():
                self.his_data[str(freq)][col] = np.array(self.his_data[str(freq)][col])
        self.logger.info('data loaded')

    def load_factor(self):
        self.logger.info('loading factor...')
        with open(self.pre_trade_factor_path, "r", encoding="utf-8") as f:
            self.his_factor = json.load(f)
        with open(self.pre_trade_norm_factor_path, "r", encoding="utf-8") as f:
            self.now_norm_factor = json.load(f)
        self.now_raw_factor = {k:np.nan for k in self.now_norm_factor.keys()}
        self.logger.info('factor loaded')

        self.logger.info('start register factor...')
        factor_all = list(self.factor_freq.keys())
        factor_1min_list = []
        factor_3min_list = []
        factor_5min_list = []
        factor_15min_list = []
        for k, v in self.factor_freq.items():
            if 1 in v:
                factor_1min_list.append(k)
            if 3 in v:
                factor_3min_list.append(k)
            if 5 in v:
                factor_5min_list.append(k)
            if 15 in v:
                factor_15min_list.append(k)

        self.factor_freq_dict ={1:factor_1min_list, 3:factor_3min_list, 5:factor_5min_list, 15:factor_15min_list}

        sys.path.insert(4, self.factor_path)
        from commodity_framework import FutureFactor

        for x in factor_all:
            importlib.import_module(x)

        flist = FutureFactor.__subclasses__()
        fac_class_dict = {x.__name__:x for x in flist}

        self.factor_all = {}
        for x in factor_1min_list:
            self.factor_all[f'{x}_{self.ticker}_1M'] = fac_class_dict[x](self.ticker, 1)
        for x in factor_3min_list:
            self.factor_all[f'{x}_{self.ticker}_3M'] = fac_class_dict[x](self.ticker, 3)
        for x in factor_5min_list:
            self.factor_all[f'{x}_{self.ticker}_5M'] = fac_class_dict[x](self.ticker, 5)
        for x in factor_15min_list:
            self.factor_all[f'{x}_{self.ticker}_15M'] = fac_class_dict[x](self.ticker, 15)
        self.factor_all_name_list = list(self.factor_all.keys())

        self.logger.info('factor registered')

    def load_model(self):
        self.logger.info('loading model...')
        self.model_dict = {}
        for k,v in self.model_name_dict.items():
            name_dict = {}
            for name in v:
                self.logger.info(name)
                sub_list = []
                sub_name = 'lgb' if 'lgb' in name else 'mlp'
                sub_path = os.path.join(self.model_file_path, name, sub_name)
                
                for file in os.listdir(sub_path):
                    if file.endswith('onnx'):
                        self.logger.info(file)
                        name_path = os.path.join(sub_path, file)
                        # self.logger.info('load')
                        model_onnx = onnx.load(name_path)
                        # self.logger.info('check')
                        onnx.checker.check_model(model_onnx)
                        # self.logger.info('serialize')
                        model_onnx = model_onnx.SerializeToString()
                        # self.logger.info('create session')
                        ort_sess = ort.InferenceSession(model_onnx)
                        # self.logger.info('done')
                        model_onnx_factors = pd.read_csv(os.path.join(sub_path, file.replace('.onnx', '.csv')),header=None)
                        model_onnx_factors = [x.replace('TICKER', self.ticker) for x in model_onnx_factors[0].tolist()]
                        sub_list.append([copy.copy(ort_sess), model_onnx_factors])
                    else:
                        continue
                name_dict[name] = sub_list
            self.model_dict[k] = name_dict
        self.logger.info('model loaded')

        self.logger.info('loading model raw value...')
        with open(self.pre_trade_model_path, "r", encoding="utf-8") as f:
            self.his_model_raw = json.load(f)
        self.logger.info('model raw value loaded')

    def pre_calculate_for_fac(self, x):
        self.factor_all[x].pre_calculate({col:self.his_data[str(self.factor_all[x].freq)][col] for col in self.factor_all[x].required_columns})
        return self.factor_all[x]

    def pre_calculate_factor(self):
        self.logger.info('pre-calculating factor...')
        rlist = concurrent_apply_func(self.pre_calculate_for_fac, self.factor_all_name_list, self.parallel_num, logger=self.logger)
        self.factor_all = rlist
        self.logger.info('pre-calculated factor')

    def calculate_factor_model(self):
        self.logger.info('calculating factor model...')
        all_raw_factor_dict = {}
        all_norm_factor_dict = {}
        factor_time_dict = {}

        all_raw_model_dict = {}
        all_norm_model_dict = {}
        model_time_dict = {}
        for now_time in self.data_gentime['1']:
            stime = time.time()
            for freq in [1,3,5,15]:
                if now_time in self.data_gentime[str(freq)]:
                    self.logger.info(f'calculating freq {freq} factor model at {now_time}')
                    while True:
                        now_time_freq_path = os.path.join(self.prod_data_path, f'{now_time}_{freq}M.json')
                        if os.path.exists(now_time_freq_path):
                            with open(now_time_freq_path, "r", encoding="utf-8") as f:
                                now_data_freq = json.load(f)
                            for col in self.his_data[str(freq)].keys():
                                self.his_data[str(freq)][col] = np.append(self.his_data[str(freq)][col], now_data_freq[col])
                            md_time = self.his_data[str(1)]['dt'][-1]
                            for fac_name in self.factor_freq_dict[freq]:
                                full_fac_name = f'{fac_name}_{self.ticker}_{freq}M'
                                _data = {col:self.his_data[str(self.factor_all[full_fac_name].freq)][col] for col in self.factor_all[full_fac_name].required_columns}  
                                try:
                                    raw = self.factor_all[full_fac_name].calculate(copy.deepcopy(_data))
                                except Exception as e:
                                    raw = np.nan
                                    self.logger.error(f'{str(md_time)}, {freq}, {full_fac_name}, {str(e)}')
                                self.his_factor[str(freq)][full_fac_name].append(raw)
                                normalize_size = self.factor_all[full_fac_name].normalize_size
                                normalize_type = self.factor_all[full_fac_name].normalize_type
                                if normalize_size > 1:
                                    norm = calc_norm(self.his_factor[str(freq)][full_fac_name], normalize_size, normalize_type)
                                else:
                                    norm = raw
                                self.now_raw_factor[full_fac_name] = raw
                                self.now_norm_factor[full_fac_name] = norm
                            break
                        else:
                            time.sleep(1)
            _md_time = self.his_data[str(1)]['dt'][-1]
            
            self.logger.info(f'calculating factor for {_md_time} done, time cost {time.time() - stime}')
            self.logger.info(f'{_md_time} factor raw values: {str(self.now_raw_factor)}')
            self.logger.info(f'{_md_time} factor norm values: {str(self.now_norm_factor)}')

            all_raw_factor_dict[_md_time] = copy.copy(self.now_raw_factor)
            all_norm_factor_dict[_md_time] = copy.copy(self.now_norm_factor)
            factor_time_dict[_md_time] = time.time() - stime

            self.logger.info(f'start model predict at {now_time}')
            model_raw_dict = {}
            model_norm_dict = {}
            mstime = time.time()
            for freq in [1,5,15]:
                if now_time in self.data_gentime[str(freq)]:
                    for model_name in self.model_dict[str(freq)].keys():
                        self.logger.info(f'start predict {model_name} at {now_time}')
                        mtime = time.time()
                        mp_list = self.model_dict[str(freq)][model_name]
                        y_list = []
                        x_value = np.array([[self.now_norm_factor[x] if not np.isnan(self.now_norm_factor[x]) else 0 for x in mp_list[0][1]]])
                        for mp in mp_list:
                            y_value = mp[0].run(None, {mp[0].get_inputs()[0].name: x_value.astype(np.float32)})
                            if 'lgb' in model_name:
                                y_value = y_value[0][0][0]
                            else:
                                y_value = y_value[0][0]
                            y_list.append(y_value)
                        y_raw = np.nanmean(y_list)
                        self.his_model_raw[model_name].append(y_raw)
                        y_norm = calc_norm(self.his_model_raw[model_name], self.model_rank_lenth_dict[str(freq)], 'ts_rank')
                        model_raw_dict[model_name] = y_raw
                        model_norm_dict[model_name] = y_norm
                        self.logger.info(f'predict {model_name} done, raw : {y_raw}, norm : {y_norm},time cost {time.time() - mtime}')

            self.logger.info(f'calculating model for {_md_time} done, time cost {time.time() - mstime}')
            self.logger.info(f'{_md_time} model raw values: {str(model_raw_dict)}')
            self.logger.info(f'{_md_time} model norm values: {str(model_norm_dict)}')

            all_raw_model_dict[_md_time] = copy.copy(model_raw_dict)
            all_norm_model_dict[_md_time] = copy.copy(model_norm_dict)
            model_time_dict[_md_time] = time.time() - mstime
            self.logger.info(f'finished model predict at {now_time}')
        
        self.logger.info(f'finished all factor and model predict, start save results')
        pd.DataFrame(all_raw_factor_dict).T.to_csv(os.path.join(self.result_save_path, f'{self.date}_{self.ticker}_raw_factor.csv'))
        pd.DataFrame(all_norm_factor_dict).T.to_csv(os.path.join(self.result_save_path, f'{self.date}_{self.ticker}_norm_factor.csv'))
        pd.DataFrame(all_raw_model_dict).T.to_csv(os.path.join(self.result_save_path, f'{self.date}_{self.ticker}_raw_model.csv'))
        pd.DataFrame(all_norm_model_dict).T.to_csv(os.path.join(self.result_save_path, f'{self.date}_{self.ticker}_norm_model.csv'))
        pd.DataFrame(factor_time_dict, index = ['time_cost']).T.to_csv(os.path.join(self.result_save_path, f'{self.date}_{self.ticker}_time_using_factor.csv'))
        pd.DataFrame(model_time_dict, index = ['time_cost']).T.to_csv(os.path.join(self.result_save_path, f'{self.date}_{self.ticker}_time_using_model.csv'))

    def run(self):
        self.logger.info(f'start torus strategy {self.ticker}...')
        self.load_data()
        self.load_factor()
        self.pre_calculate_factor()
        self.load_model()
        self.calculate_factor_model()
        self.logger.info(f'finished torus strategy {self.ticker}...')

if __name__ == '__main__':
    tp = TorusProduction('/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/test_samples/torus/v1.0/para/20250801/AU.SHF.json')
    tp.run()
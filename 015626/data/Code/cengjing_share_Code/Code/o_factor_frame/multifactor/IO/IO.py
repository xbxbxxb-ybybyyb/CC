import pandas as pd
import datetime as dt
import os
from .IO_enums import *
from .naming_config import public_h5root
import concurrent.futures


def str_date_parser(str_name):
    """
    --- DESCRIPTION ---
    Parse 'YYYMMMDD.xxx' styled string / file name to datetime object
    """
    if any([isinstance(str_name, dt.date), isinstance(str_name, dt.datetime), isinstance(str_name, pd.Timestamp)]):
        return pd.Timestamp(str_name)
    if type(str_name) is int:
        str_name = str(str_name)
    if type(str_name) is str:
        if len(str_name) == 8:
            return pd.Timestamp(dt.datetime.strptime(str_name, '%Y%m%d'))
        elif len(str_name) == 14:
            return pd.Timestamp(dt.datetime.strptime(str_name, '%Y%m%d%H%M%S'))
        else:
            raise AssertionError
    else:
        raise AssertionError


def str_time_parser(str_name):
    if isinstance(str_name, pd.Timedelta):
        return str_name
    else:
        assert isinstance(str_name, str), 'input is not string'
    if len(str_name) == 4:
        _h, _m, _s = int(str_name[:2]), int(str_name[2:4]), 0
    elif len(str_name) == 6:
        _h, _m, _s = int(str_name[:2]), int(str_name[2:4]), int(str_name[4:6])
    else:
        raise AssertionError
    return pd.Timedelta(hours=_h, minutes=_m, seconds=_s)


def get_root_keys(h5_store):
    """
    --- DESCRIPTION ---
    Get group keys
    """
    if type(h5_store) is pd.io.pytables.HDFStore:
        return ['/' + item for item in list(h5_store.root._v_groups.keys())]


def csv_dumper(file_list, hdf5, dataset, from_scratch=False, header_exist=True, factor_name='Jone', **kwargs):
    """
    --- DESCRIPTION ---
    Reads in csv files as specified in file_list and tries to concatenate csv contents into one multiIndexed Pandas DataFrame
    Stores the generated DataFrame object in a single dataset of HDF5 database WITHOUT intention to override original dataset data

    --- CAUTION ---
    File names are parsed as 'YYYYMMDD.xxx' string as DataFrame primary index 'dt'
    In case dataset 'dt' index already contains dates specified by csv files, csv_dumper will NOT override dataset old data

    --- PARAMETER ---
    file_list: ['xxx.xx', 'xxx.xx']
    hdf5     : file name of HDF5 database
    dataset  : dataset name to store DataFrame
    """

    ts_meta = dt.datetime.today()

    if '/' not in dataset:
        dataset = '/' + dataset
    if type(file_list) is not list:
        file_list = [file_list]
    file_list.sort()
    if from_scratch:
        if not os.path.exists(os.path.dirname(hdf5)):
            os.makedirs(os.path.dirname(hdf5))
    with pd.HDFStore(hdf5) as h5_store:
        if dataset in get_root_keys(h5_store):
            # dataset is already created
            # retrieve dt list
            if from_scratch:
                dt_lst = pd.to_datetime(h5_store.select_column(dataset, 'dt').dt.date.unique()).tolist()
            else:
                dt_lst = []
            print('%s last tapped date: %s' % (dataset, h5_store.get_storer(dataset).attrs.modification_date.isoformat()))
        else:
            dt_lst = []

        for _file in file_list:
            date_ticker = str_date_parser(os.path.basename(_file).split('.')[0])
            exist_flag = False
            if from_scratch:
                exist_flag = date_ticker in dt_lst
            else:
                exist_flag = date_is_exist(date_ticker, h5_store, dataset)
            if exist_flag:
                print('%s already exists in database, skipping...' % date_ticker.strftime('%Y%m%d'))
                # Neglect intentionally to protect hdf5 old data
                pass
            else:
                dt_lst.append(date_ticker)
                # Prepare multiIndex DataFrame
                if header_exist:
                    pd_file = pd.read_csv(_file)
                    # In case Ticker column is unnamed
                    pd_file.rename(columns={'Unnamed: 0': 'Ticker'}, inplace=True)
                    pd_file.rename(columns={'ticker': 'Ticker'}, inplace=True)
                else:
                    pd_file = pd.read_csv(_file, header=None)
                    pd_file.rename(columns={0: 'Ticker', 1: factor_name}, inplace=True)
                pd_file['dt'] = date_ticker
                pd_file.set_index(['dt', 'Ticker'], append=False, inplace=True)
                # Dump DataFrame
                h5_store.append(dataset, pd_file, data_columns=True, **kwargs)
                h5_store.get_storer(dataset).attrs.modification_date = ts_meta
                print('%s appended to %s' % (date_ticker.strftime('%Y%m%d'), dataset))


def hdf5_replacer(file_list, hdf5, dataset, from_scratch=False):
    """
    --- DESCRIPTION ---
    Reads in csv files as specified in file_list and tries to concatenate csv contents into one multiIndexed Pandas DataFrame
    Stores the generated DataFrame object in a single dataset of HDF5 database WITH intention to replace old data in dataset

    --- CAUTION ---
    File names are parsed as 'YYYYMMDD.xxx' string as DataFrame primary index 'dt'
    If dataset 'dt' index does not contain dates specified by csv files, hdf5_replacer will raise an NameErro Exception

    --- PARAMETER ---
    file_list: ['xxx.xx', 'xxx.xx']
    hdf5     : file name of HDF5 database
    dataset  : dataset name to store DataFrame
    """

    ts_meta = dt.datetime.today()

    if '/' not in dataset:
        dataset = '/' + dataset
    if type(file_list) is not list:
        file_list = [file_list]

    with pd.HDFStore(hdf5) as h5_store:
        if dataset in get_root_keys(h5_store):
            # dataset is already created
            if from_scratch:
                dt_lst = pd.to_datetime(h5_store.select_column(dataset, 'dt').dt.date.unique()).tolist()
            print('%s last tapped date: %s' % (dataset, h5_store.get_storer(dataset).attrs.modification_date.isoformat()))
        else:
            print('%s dataset not created, use csv_dumper to initialise instead' % dataset)
            raise NameError

        for _file in file_list:
            date_ticker = str_date_parser(os.path.basename(_file).split('.')[0])
            if from_scratch:
                exist_flag = date_ticker in dt_lst
            else:
                exist_flag = date_is_exist(date_ticker, h5_store, dataset)
            if not exist_flag:
                print('%s does not exist in database, aborting...' % date_ticker.strftime('%Y%m%d'))
                raise NameError
            else:
                # Prepare multiIndex DataFrame
                pd_file = pd.read_csv(_file)
                # In case Ticker column is unnamed
                pd_file.rename(columns={'Unnamed: 0':'Ticker'}, inplace=True)
                pd_file.rename(columns={'ticker':'Ticker'}, inplace=True)
                pd_file['dt'] = date_ticker
                pd_file.set_index(['dt', 'Ticker'], append=False, inplace=True)
                # Delete old records
                record_num = h5_store.remove(dataset, 'dt=date_ticker')
                print('%d records deleted at %s %s' % (record_num, date_ticker.strftime('%Y%m%d'), dataset))
                # Append new records
                h5_store.append(dataset, pd_file, data_columns=True)
                h5_store.get_storer(dataset).attrs.modification_date = ts_meta
                print('%s appended to %s' % (date_ticker.strftime('%Y%m%d'), dataset))


def pd_hdf5_writer(pd_factor, hdf5, dataset=None, override=None, append=None, from_scratch=True,
                   override_overlap=True, date_column=None, min_itemsize=None):
    """
    --- DESCRIPTION ---
    Dump DataFrame/Series into HDF5 dataset with override and append switch
    By default, override and append switch are both unset (None)

    --- CAUTION ---
    Only ONE tag should be set during one single Func call
    Input DataFrame should be multiIndexed by ['dt', 'Ticker']
    dataset should be explicitly specified or can be inferred by DataFrame name

    --- PARAMETER ---
    override : DataFrame will replace dataset content in hdf5 file
    append   : DataFrame will be appended (possibly override certain data) to dataset in hdf5 file
    otherwise: DataFrame will be stored as new dataset in hdf5 file
    date_column: If not None, use this column as index in append mode to slice or delete records
    """

    ts_meta = dt.datetime.today()

    # DataFrame format verification
    if isinstance(pd_factor.index, pd.MultiIndex):
        assert pd_factor.index.names == ['dt', 'Ticker'], 'Index name error, abort...'
        dt_ref = 'dt'
    else:
        assert pd_factor.index.names == ['dt'], 'Index name error, abort...'
        dt_ref = 'index'
    assert isinstance(pd_factor.index.get_level_values(level='dt'), pd.DatetimeIndex)
    pd_factor = pd_factor.sort_index(level=0)

    if dataset is None:
        # dataset should be able to be inferred by name attribute
        try:
            dataset = pd_factor.name
        except:
            print('dataset cannot be inferred by Dataframe name, aborting...')
            raise AssertionError

    if '/' not in dataset:
        dataset = '/' + dataset

    # Parameter verification
    # Only three modes are valid: override, append, new
    if override is not None and append is not None:
        print('Only one tag of override and append can be specified, aborting...')
        raise SyntaxError
    if override is not None:
        if override is not True:
            print('The override tag should only be True or unset, aborting...')
            raise SyntaxError
    if append is not None:
        if append is not True:
            print('The append tag should only be True or unset, aborting...')
            raise SyntaxError

    with pd.HDFStore(hdf5) as h5_store:
        # Common actions, dt_lst extraction
        if dataset in get_root_keys(h5_store):
            # dataset is already created
            try:
                if from_scratch:
                    dt_lst = pd.to_datetime(h5_store.select_column(dataset, dt_ref).dt.date.unique()).tolist()
                print('%s last tapped date: %s' % (dataset, h5_store.get_storer(dataset).attrs.modification_date.isoformat()))
            except AttributeError:
                print('Last tapped date unknown, data may be corrupted...')
                if append or override:
                    raise AttributeError
                else:
                    dt_lst = []
        else:
            dt_lst = []

        if override:
            if from_scratch:
                exist_flag = len(dt_lst) != 0
            else:
                exist_flag = not is_empty_dataset(h5_store, dataset)
            if not exist_flag:
                # dt_lst is empty
                print('%s does not exit in %s, aborting...' % (dataset, hdf5))
                raise AssertionError
            h5_store.put(dataset, pd_factor, format='table', append=False, data_columns=True, min_itemsize=min_itemsize)
            h5_store.get_storer(dataset).attrs.modification_date = ts_meta
            print('%s is overriden with newly input DataFrame in %s' % (dataset, hdf5))
        elif append:
            # Append Func with data replacement
            if date_column is not None:
                dt_lst_to_process = pd.to_datetime(pd.unique(pd_factor[date_column])).tolist()
            else:
                dt_lst_to_process = pd.to_datetime(pd.unique(pd_factor.index.get_level_values('dt').date)).tolist()
            if len(dt_lst_to_process) == len(pd_factor.index.get_level_values('dt')):
                is_daily_freq = True
            else:
                is_daily_freq = False
            dt_lst_to_process.sort()
            for date_ticker in dt_lst_to_process:
                if from_scratch:
                    exist_flag = date_ticker in dt_lst
                else:
                    exist_flag = date_is_exist(date_ticker, h5_store, dataset, dt_ref=dt_ref)
                if exist_flag and override_overlap:
                    # Delete old records
                    if date_column is None:
                        record_num = h5_store.remove(dataset, '%s>=%s & %s<%s' % (dt_ref, date_ticker.strftime('%Y%m%d'),
                                                                                  dt_ref, (date_ticker + pd.Timedelta('1D')).strftime('%Y%m%d')))
                    else:
                        record_num = h5_store.remove(dataset, '%s=date_ticker' % date_column)
                    print('%d records deleted at %s %s' % (record_num, date_ticker.strftime('%Y%m%d'), dataset))
                if not exist_flag or override_overlap:
                    # Append new records
                    if date_column is not None:
                        sliced_data = pd_factor.loc[pd_factor[date_column]==date_ticker]
                    else:
                        if dt_ref == 'index' and is_daily_freq:
                            sliced_data = pd_factor.loc[date_ticker.strftime('%Y%m%d'):date_ticker.strftime('%Y%m%d')]
                        else:
                            sliced_data = pd_factor.loc[date_ticker.strftime('%Y%m%d')]
                    h5_store.append(dataset, sliced_data, data_columns=True)
                    h5_store.get_storer(dataset).attrs.modification_date = ts_meta
                    print('%s appended to %s' % (date_ticker.strftime('%Y%m%d'), dataset))
        else:
            # new stash
            if from_scratch:
                exist_flag = len(dt_lst) != 0
            else:
                exist_flag = not is_empty_dataset(h5_store, dataset)
            if not exist_flag:
                h5_store.put(dataset, pd_factor, format='table', append=False,
                             data_columns=True, min_itemsize=min_itemsize)
                h5_store.get_storer(dataset).attrs.modification_date = ts_meta
                print('%s is newly created to store input DataFrame in %s' % (dataset, hdf5))
            else:
                print('%s already exits in %s, aborting...' % (dataset, hdf5))
                raise AssertionError


def hdf5_node_remover(hdf5, dataset=None):
    """
    --- DESCRIPTION ---
    Remove dataset from hdf5 database
    --- CAUTION ---
    This Func only makes dataset inaccessible, use h5repack/ptrepack to reclaim disk spaces
    """
    with pd.HDFStore(hdf5) as h5_store:
        h5_store.get_node(dataset)._f_remove(recursive=True)


def read_data(trading_days=None, columns=None, universe=None, mkttype=MktType.CHINA, dtype=DType.STOCK,
              ftype=FType.MD, dfreq=DFreq.DAILY, dsource=DSource.WIND,
              dtable=None, alt=None, h5root=public_h5root, select_str=None, max_workers=1):
    """
    --- DESCRIPTION ---
    Read data from dsource or alt source by specifing trading days, universe, columns, etc...
    --- CAUTION ---
    alt source will override dsource
    dsource could be given as list, which will generate multiIndexed columns in return
    --- PARAMETER ---
    trading_days : [start, end] or date list as in type dt.date
    universe     : stock ticker list or UniType or None for all
    columns      : [open, close, moment] alike
    mkttype      : MktType.CHINA, MktType.HK, ...
    dtype        : DType.STOCK, DType.FUTURES, ...
    ftype        : FType.FDD, FType.MD, ...
    dfreq        : DFreq.TICK, DFreq.MINUTE, ...
    dsource      : DSource.HTSC, DSource.WIND, ...
    dtable       : DTable.con_forecast_stk, ...
    alt          : '/example/test.h5' absolute path to custom HDF5 database
    """
    start_date = None
    end_date = None
    # Parameter verification
    # Date process
    if trading_days is not None:
        if type(trading_days) is not list:
            trading_days = [trading_days]
        try:
            trading_days = [str_date_parser(item) for item in trading_days]
        except:
            print('Illegal input in trading days, aborting...')
            raise TypeError
        if len(trading_days) == 2:
            start_date, end_date = min(trading_days), max(trading_days)
    # NPY_MAXARGS 32 limitation
    NPY_MAXARGS = 30
    if universe is not None:
        if type(universe) is not list:
            universe = [universe]
    if columns is not None:
        if type(columns) is not list:
            columns = [columns]
    # Path assembly
    abs_h5_path = path_assembler(mkttype=mkttype, dtype=dtype, ftype=ftype, dfreq=dfreq,
                                 dsource=dsource, dtable=dtable, alt=alt, h5root=h5root)
    # Data retrieve
    pd_retrieved = pd.DataFrame()
    with pd.HDFStore(abs_h5_path, 'r') as h5_store:
        s_type = None
        # Tags to check after data retrieve
        filter_trading_day = False
        filter_universe = False
        filter_columns = False
        h5_root_keys = get_root_keys(h5_store)
        # Two formats of hdf5 internal structure supported
        if len(h5_root_keys) == 1:
            # Only one dataset inside
            s_type = 1
            s_type_cols = h5_store.get_node(h5_root_keys[0]).table.colnames
        else:
            # Factors/data stores as separate datasets
            s_type = 2
            s_type_cols = [item.replace('/', '') for item in h5_root_keys]
        if 'dt' in  h5_store.get_node(h5_root_keys[0]).table.colnames:
            dt_ref = 'dt'
        else:
            dt_ref = 'index'
        # User request columns verification
        if columns is not None:
            if not all([item in s_type_cols for item in columns]):
                print('Illegal column item(s) found: %s' % ' '.join([item for item in columns if item not in s_type_cols]))
                raise AssertionError
        else:
            # Retrieve all columns available
            if s_type == 2:
                columns = s_type_cols
        # Search string prepare
        # columns/universe/trading_days dimension exceed NPY_MAXARGS limit check in mind
        if trading_days is not None:
            if len(trading_days) >= NPY_MAXARGS:
                start_date, end_date = min(trading_days), max(trading_days)
                filter_trading_day = True
            sc_date = '%s >= %r & %s <= %r' % (dt_ref, start_date, dt_ref, end_date) if start_date is not None else '%s in %r' % (dt_ref, trading_days)
        else:
            sc_date = None
        if universe is not None and len(universe) >= NPY_MAXARGS:
            filter_universe = True
            sc_univ = None
        else:
            sc_univ = 'Ticker in %r' % universe if universe is not None else None
        if columns is not None and s_type == 1 and len(columns) >= NPY_MAXARGS:
            filter_columns = True
            sc_col = None
        else:
            sc_col  = 'columns = %r' % columns if columns is not None else None
        # Real thing
        if s_type == 1:
            if select_str is not None:
                assert isinstance(select_str, str)
            sc_string = ' & '.join([item for item in [sc_date, sc_col, sc_univ, select_str] if item is not None])
            sc_string = None if len(sc_string) == 0 else sc_string
            pd_retrieved = h5_store.select(h5_root_keys[0], where=sc_string)
        elif s_type == 2:
            assert select_str is None
            def little_retriever(abs_h5_path, fct, where_cls):
                with pd.HDFStore(abs_h5_path, 'r') as h5_store:
                    pd_little = h5_store.select(fct, where=where_cls)
                return pd_little
            sc_string = ' & '.join([item for item in [sc_date, sc_univ] if item is not None])
            sc_string = None if len(sc_string) == 0 else sc_string
            # Never concat in iteration
            pd_cat_store = []
            # Multithread for IO intensive tasks
            if max_workers is None:
                max_workers = min(6, len(columns))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_retrieving = {executor.submit(little_retriever, abs_h5_path, fct, sc_string): fct for fct in columns}
                for future in concurrent.futures.as_completed(future_retrieving):
                    fct = future_retrieving[future]
                    try:
                        pd_cat_store.append(future.result())
                    except Exception as exc:
                        print('%s generated an exception during retrieval: %s' % (fct, exc))
            pd_retrieved = pd.concat(pd_cat_store, axis=1)
        # Filter after data retrieval
        idx = pd.IndexSlice
        if filter_trading_day:
            pd_retrieved = pd_retrieved.loc[idx[trading_days, :], :]
        if filter_universe:
            pd_retrieved = pd_retrieved.loc[idx[:, universe], :]
        if filter_columns:
            pd_retrieved = pd_retrieved.loc[:, columns]
    return pd_retrieved.sort_index(level=0)


def path_assembler(mkttype, dtype, ftype, dfreq, dsource, dtable, alt, h5root=public_h5root):
    abs_path_root = os.path.normpath(h5root)
    # Type process
    dsource = dsource.name
    # Path assembly
    if alt is not None:
        abs_h5_path = alt
    else:
        if dtable is not None:
            dtable = dtable.name
            h5_file_name = dtable + '.h5'
            abs_h5_path = os.path.join(*[abs_path_root, 'DATABASE', dsource, dtable, h5_file_name])
        else:
            dfreq = dfreq.name
            ftype = ftype.name
            dtype = dtype.name
            mkttype = mkttype.name
            h5_file_name = '_'.join([ftype, mkttype, dtype, dfreq, dsource]) + '.h5'
            abs_h5_path = os.path.join(*[abs_path_root, ftype, '_'.join([mkttype, dtype]),
                                         dfreq, dsource, h5_file_name])
    return abs_h5_path


def get_available_cols(mkttype=MktType.CHINA, dtype=DType.STOCK, ftype=FType.MD, dfreq=DFreq.DAILY,
                       dsource=DSource.WIND, dtable=None, alt=None, h5root=public_h5root):
    abs_h5_path = path_assembler(mkttype=mkttype, dtype=dtype, ftype=ftype, dfreq=dfreq,
                                 dsource=dsource, dtable=dtable, alt=alt, h5root=h5root)
    with pd.HDFStore(abs_h5_path, 'r') as h5_store:
        h5_root_keys = get_root_keys(h5_store)
        if len(h5_root_keys) == 1:
            # Only one dataset inside
            s_type = 1
            s_type_cols = h5_store.get_node(h5_root_keys[0]).table.colnames
        else:
            # Factors/data stores as separate datasets
            s_type = 2
            s_type_cols = [item.replace('/', '') for item in h5_root_keys]
    return s_type_cols


def hdf5_repairer(h5_input, h5_output=None, filter_lst=None, entry_lst=None, ptrepack_path=None, complevel=9, sortby=None):
    """
    --- DESCRIPTION ---
    Use ptrepack to reclaim space and fix possible errors
    --- CAUTION ---
    Works only with hdf5 file with separate datasets since it use get_available_cols
    Due to Windows limitations, input and output HDF5s should be in the same directory
    """
    is_override = False
    if h5_output is None:
        h5_output = dt.datetime.now().strftime('%Y%m%d_%H%M%S') + '.h5'
        is_override = True

    if os.path.exists(h5_output):
        print('Existing file for HDF5 output, aborting...')
        raise AssertionError

    if h5_input == h5_output:
        print('Input folder should differ from output folder, aborting...')
        raise AssertionError
    try:
        factor_names = get_available_cols(alt=h5_input)
    except:
        if entry_lst is None:
            print('Cannot retrieve HDF5 file information, aborting...')
            raise AssertionError
        else:
            print('Cannot retrieve HDF5 file information, using entry list instead')
            factor_names = entry_lst

    if entry_lst is None:
        factor_todo_lst = factor_names
    else:
        if not isinstance(entry_lst, list):
            entry_lst = [entry_lst]
        assert all([item in factor_names for item in entry_lst])
        factor_todo_lst = entry_lst

    if filter_lst is not None:
        if not isinstance(filter_lst, list):
            filter_lst = [filter_lst]
        factor_todo_lst = [item for item in factor_todo_lst if item not in filter_lst]

    if ptrepack_path is None:
        ptrepack_path = 'ptrepack'

    current_folder = os.getcwd()
    input_basename = os.path.basename(h5_input)
    output_basename = os.path.basename(h5_output)

    if sortby is None:
        command_options = '--chunkshape=auto --propindexes --complevel=%d --complib=blosc' % complevel
    else:
        command_options = '--chunkshape=auto --propindexes --complevel=%d --complib=blosc --sortby=%s' % (complevel, sortby)

    os.chdir(os.path.dirname(h5_input))
    if filter_lst is None and entry_lst is None:
        command = ' '.join([ptrepack_path, command_options, input_basename, output_basename])
        print('Calling %s' % command)
        os.system(command)
    else:
        for factor in factor_todo_lst:
            print('Processing %s' % factor)
            command = ' '.join([ptrepack_path, command_options,
                                input_basename+':/'+factor,
                                output_basename+':/'+factor])
            os.system(command)

    if os.stat(output_basename).st_size / os.stat(input_basename).st_size >= 0.25:
        if is_override:
            os.remove(input_basename)
            os.rename(output_basename, input_basename)
    else:
        print('In/out file sizes mismatch, Repack may be FAILED!')

    os.chdir(current_folder)


def hdf_optimizer(hdf5, repack=True, sortby='dt'):
    with pd.HDFStore(hdf5) as h5_store:
        s_type = None
        # Tags to check after data retrieve
        h5_root_keys = get_root_keys(h5_store)
        # Two formats of hdf5 internal structure supported
        if len(h5_root_keys) == 1:
            # Only one dataset inside
            s_type = 1
        else:
            # Factors/data stores as separate datasets
            s_type = 2
            s_type_cols = [item.replace('/', '') for item in h5_root_keys]
        if s_type == 1:
            h5_store.create_table_index(h5_root_keys[0], optlevel=9, kind='full')
        else:
            for factor in s_type_cols:
                h5_store.create_table_index(factor, optlevel=9, kind='full')
    if repack:
        hdf5_repairer(hdf5, sortby=sortby)


def dipping(depth=10, columns=None, mkttype=MktType.CHINA, dtype=DType.STOCK, ftype=FType.MD, dfreq=DFreq.DAILY,
            dsource=DSource.WIND, dtable=None, alt=None, h5root=public_h5root, max_workers=1):
    """
    --- DESCRIPTION ---
    Behaves like pandas.head/tail, for positive/negtive depth parameter
    """
    # Path assembly
    abs_h5_path = path_assembler(mkttype=mkttype, dtype=dtype, ftype=ftype, dfreq=dfreq,
                                 dsource=dsource, dtable=dtable, alt=alt, h5root=h5root)
    # Data retrieve
    pd_retrieved = pd.DataFrame()
    with pd.HDFStore(abs_h5_path, 'r') as h5_store:
        s_type = None
        # Tags to check after data retrieve
        h5_root_keys = get_root_keys(h5_store)
        # Two formats of hdf5 internal structure supported
        if len(h5_root_keys) == 1:
            # Only one dataset inside
            s_type = 1
            s_type_cols = h5_store.get_node(h5_root_keys[0]).table.colnames
        else:
            # Factors/data stores as separate datasets
            s_type = 2
            s_type_cols = [item.replace('/', '') for item in h5_root_keys]
        # Real thing
        if columns is not None:
            if type(columns) is not list:
                columns = [columns]
            if not all([item in s_type_cols for item in columns]):
                print('Illegal column item(s) found: %s' % ' '.join([item for item in columns if item not in s_type_cols]))
                raise AssertionError
        if s_type == 1:
            nrows = h5_store.get_storer(h5_root_keys[0]).nrows
            _start, _stop = ht_index(depth, nrows)
            pd_retrieved = h5_store.select(h5_root_keys[0], start=_start,stop=_stop)
            pd_retrieved = pd_retrieved[columns] if columns is not None else pd_retrieved
        elif s_type == 2:
            pd_cat_store = []
            def little_retriever(abs_h5_path, fct, depth):
                with pd.HDFStore(abs_h5_path, 'r') as h5_store:
                    nrows = h5_store.get_storer(fct).nrows
                    _start, _stop = ht_index(depth, nrows)
                    pd_little = h5_store.select(fct, start=_start,stop=_stop)
                return pd_little
            if max_workers is None:
                max_workers = min(6, len(s_type_cols))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                if columns is None:
                    future_retrieving = {executor.submit(little_retriever, abs_h5_path, fct, depth): fct for fct in s_type_cols}
                else:
                    future_retrieving = {executor.submit(little_retriever, abs_h5_path, fct, depth): fct for fct in columns}
                for future in concurrent.futures.as_completed(future_retrieving):
                    fct = future_retrieving[future]
                    try:
                        pd_cat_store.append(future.result())
                    except Exception as exc:
                        print('%s generated an exception during retrieval: %s' % (fct, exc))
            pd_retrieved = pd.concat(pd_cat_store, axis=1)
    return pd_retrieved.sort_index(level=0)


def ht_index(depth, nrows):
    if depth > 0:
        return nrows - depth, nrows
    elif depth < 0:
        return 0, abs(depth)
    else:
        return ht_index(10, nrows)


def head_tail(head, tail, *args, **kwargs):
    head_pd = dipping(-head, *args, **kwargs)
    tail_pd = dipping(tail, *args, **kwargs)
    return head_pd.append(tail_pd)


def date_is_exist(date, h5_store, dataset, dt_ref='dt'):
    date = str_date_parser(date)
    sc_date = '%s>=%s & %s<%s' % (dt_ref, date.strftime('%Y%m%d'),
                                  dt_ref, (date+pd.Timedelta('1D')).strftime('%Y%m%d'))
    pd_little = h5_store.select(dataset, where=sc_date)
    if len(pd_little) != 0:
        return True
    else:
        return False

def is_empty_dataset(h5_store, dataset):
    try:
        res = h5_store.select(dataset, start=0, end=1)
    except KeyError:
        return True
    if len(res) == 0:
        return  True
    else:
        return False


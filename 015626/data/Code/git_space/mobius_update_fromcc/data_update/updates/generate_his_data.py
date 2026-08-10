import pandas as pd
import os
import json
import datetime
import re
import csv
import time
import ray
import zipfile
from link import LinkMessage
import settings
from xquant.factordata import FactorData
from xquant.compute.aimr import AIMR

lm = LinkMessage()

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def get_future_date_list(date_str):
    time_array = date_str.split('-')

    begin = datetime.datetime(int(time_array[0]), int(time_array[1]), int(time_array[2]), 9, 30, 0)
    futures_time_list = []
    for i in range(0, 120):
        new_time = begin + datetime.timedelta(minutes=i)
        futures_time_list.append(datetime.datetime.strftime(new_time, "%Y-%m-%d %H:%M:%S"))
    begin = datetime.datetime(int(time_array[0]), int(time_array[1]), int(time_array[2]), 13, 0)
    for i in range(0, 120):
        new_time = begin + datetime.timedelta(minutes=i)
        futures_time_list.append(datetime.datetime.strftime(new_time, "%Y-%m-%d %H:%M:%S"))

    return futures_time_list


def get_stock_date_list(date_str):
    time_array = date_str.split('-')

    begin = datetime.datetime(int(time_array[0]), int(time_array[1]), int(time_array[2]), 9, 30, 0)
    stock_time_list = []
    for i in range(0, 120):
        new_time = begin + datetime.timedelta(minutes=i)
        stock_time_list.append(datetime.datetime.strftime(new_time, "%Y-%m-%d %H:%M:%S"))
    begin = datetime.datetime(int(time_array[0]), int(time_array[1]), int(time_array[2]), 13, 0)
    for i in range(0, 117):
        new_time = begin + datetime.timedelta(minutes=i)
        stock_time_list.append(datetime.datetime.strftime(new_time, "%Y-%m-%d %H:%M:%S"))

    return stock_time_list


def camel(s):
    if "_" in s:
        s = re.sub(r"(\s|_|-)+", " ", s).title().replace(" ", "")
        if "Superorder" in s or "Smallorder" in s or "Bigorder" in s or "Midorder" in s:
            temp_s = s[0].lower() + s[1:]
            return temp_s.replace("order", "Order")
        return s[0].lower() + s[1:]
    else:
        return s[0].lower() + s[1:]


def get_columns_list(df):
    columns_list = ["symbol", "amended", "suspended"]
    for columns in df:
        if "BAS" in str(columns):
            columns = str(columns).replace("BAS", "bas")
        elif "adjfactor" in str(columns):
            columns = str(columns).replace("adjfactor", "adjFactor")
        elif "OBI" in str(columns):
            columns = str(columns).replace("OBI", "obi")
        else:
            columns = camel(str(columns))
        columns_list.append(columns)
    columns_list_res = []
    for i in columns_list:
        if i in ['sellBigOrderCountV2',
                 'sellBigOrderMoneyV2',
                 'sellBigOrderVolumeV2',
                 'sellMidOrderCountV2',
                 'sellMidOrderMoneyV2',
                 'sellMidOrderVolumeV2',
                 'sellSmallOrderCountV2',
                 'sellSmallOrderMoneyV2',
                 'sellSmallOrderVolumeV2',
                 'sellSuperOrderCountV2',
                 'sellSuperOrderMoneyV2',
                 'sellSuperOrderVolumeV2',
                 'sellMidOrderVolumeOthermin',
                 'sellSmallOrderVolumeOthermin',
                 'buyBigOrderCountOthermin',
                 'buyMidOrderMoneyOthermin',
                 'buySmallOrderMoneyOthermin',
                 'buyMidOrderVolumeOthermin',
                 'buySmallOrderVolumeOthermin',
                 'buySmallOrderMoneyThismin'
                 ]:
            i = i.replace("Order", "order")
        elif i in ['sellorderamtTotal','buyorderamtTotal']:
            i = i.replace('orderamt','OrderAmt')
        columns_list_res.append(i)
    return columns_list_res


def get_index_columns_list(df):
    columns_list = ["symbol", "amended"]
    for columns in df:
        if "BAS" in str(columns):
            columns = str(columns).replace("BAS", "bas")
        else:
            columns = camel(str(columns))
        columns_list.append(columns)

    return columns_list


def get_real_input_file(input_file):
    if "CHINA_STOCK905" in input_file:
        input_file = input_file.replace("CHINA_STOCK905", "CHINA_STOCK")
    elif "CHINA_STOCK300" in input_file:
        input_file = input_file.replace("CHINA_STOCK300", "CHINA_STOCK")
    elif "CHINA_STOCK50" in input_file:
        input_file = input_file.replace("CHINA_STOCK50", "CHINA_STOCK")

    return input_file


@ray.remote
def hdf52json_readh5(input_file, date_time):
    symbol, elementType, tt_type = get_sym_ele_type(input_file)
    input_file = get_real_input_file(input_file)

    data = pd.read_hdf(input_file)
    df = data.reset_index()
    date_list = get_future_date_list(date_time)
    json_list = []
    try:
        for i in date_list:
            columns_list = ["symbol", "amended"]
            for columns in df:
                if "BAS" in str(columns):
                    columns = str(columns).replace("BAS", "bas")
                else:
                    columns = camel(str(columns))
                columns_list.append(columns)
            data_dict = dict()
            recv_timestamp = (datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
            data_dict["recvTimestamp"] = '{}.000'.format(recv_timestamp)
            data_dict["timestamp"] = '{}.000'.format(i)
            data_dict["symbol"] = symbol
            data_dict["columns"] = columns_list[0:2] + columns_list[4:]
            data_dict["type"] = tt_type
            data_dict["elementType"] = elementType
            data_dict["elementField"] = "indicatorsList"
            ddf = df[df["dt"] == i]
            details_list = []
            for row in ddf.itertuples():
                detail_list = []
                for i in row:
                    detail_list.append(i)
                detail_list.insert(3, False)
                if symbol == "FS_IF_1MIN" or symbol == "FS_IC_1MIN" or symbol == "FS_IH_1MIN" or symbol == "FS_IM_1MIN" \
                        or symbol == "FS_T_1MIN":
                    detail_list[2] = str(detail_list[2])[:-1]
                details_list.append(detail_list[2:])
            data_dict["details"] = details_list
            json_list.append(data_dict)
    except Exception as e:
        print(e)
    return json_list


def hdf52json(input_file_list, date_time):
    json_dict_list = []
    all_json_list = ray.get([hdf52json_readh5.remote(input_file, date_time) for input_file in input_file_list])
    for json_list in all_json_list:
        json_dict_list += json_list
    return sorted(json_dict_list, key=lambda x: x["timestamp"])

@ray.remote
def gpiaohdf52json_readh5(input_file, date_time):
    date_list = get_stock_date_list(date_time)
    columns = settings.STOCK_FACTOR_COLUMNS if settings.STOCK_FACTOR_COLUMNS else None
    json_dict = dict()
    input_file = get_real_input_file(input_file)
    json_key = input_file.split("/")[-1].split(".")[0]
    stock_name = input_file.split("/")[-1]
    stock_name = stock_name.replace('.h5', '')
    #        print(stock_name)
    h5 = pd.HDFStore(input_file)
    data = h5.select(stock_name, where="dt>='{}'&dt<='{}'".format(date_list[0], date_list[-1]), columns=columns)
    df = data.reset_index()
    h5.close()
    if df.empty:
        return stock_name
    else:
        return df

def gpiaohdf52json(input_file_list, date_time, stock_type):
    date_list = get_stock_date_list(date_time)
    all_json_list = list()
    columns = settings.STOCK_FACTOR_COLUMNS if settings.STOCK_FACTOR_COLUMNS else None
    demo_input_file = input_file_list[0]
    symbol, elementType, tt_type = get_sym_ele_type(demo_input_file, stock_type)
    demo_input_file = get_real_input_file(input_file_list[0])
    tmp_data = pd.read_hdf(demo_input_file, columns=columns)
    tmp_df = tmp_data.reset_index()
    #    print(date_list[0])
    #    print(date_list[-1])
    df_list = ray.get([gpiaohdf52json_readh5.remote(input_file, date_time) for input_file in input_file_list])
    all_stock_df = pd.concat([i for i in df_list if not isinstance(i, str)])
    suspended_stock_list = [i for i in df_list if isinstance(i, str)]
    ori_columns = all_stock_df.columns.to_list()
    all_stock_df["symbol"] = all_stock_df['Ticker']
    all_stock_df['amended'] = False
    all_stock_df["suspended"] = False
    all_stock_df['dt'] = all_stock_df['dt'].astype(str)
    all_stock_df = all_stock_df[["symbol", "amended", "suspended"]+ori_columns]
    if len(suspended_stock_list) > 0:
        print("h5文件中未获取到标的：{}在 {} 的数据, 置为suspended".format(str(suspended_stock_list), date_time))
        # 补充缺失的票的dataframe到总的dataframe中 方便后面一起转换
        # [[key, False, True] + [0 * i for i in range(len(columns_list) - 5)]]
        lack_stock_df = pd.DataFrame([[i] + [False, True] + [j, i] + [0]*(len(ori_columns)-2) for i in suspended_stock_list for j in date_list],
                                     columns=all_stock_df.columns)
        all_stock_df = pd.concat([all_stock_df, lack_stock_df])
    all_stock_df = all_stock_df.sort_values(['dt', 'symbol'])

    columns_list = get_columns_list(tmp_df)
    groupby_time_series = all_stock_df.groupby('dt').apply(lambda x: x[["symbol", "amended", "suspended"]+ori_columns[2:]].values.tolist())
    groupby_time_dict = groupby_time_series.to_dict()

    for date_str, data_details in groupby_time_dict.items():
        data_dict = {}
        recv_timestamp = (
                datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=1)).strftime(
            "%Y-%m-%d %H:%M:%S")
        data_dict["recvTimestamp"] = '{}.000'.format(recv_timestamp)
        data_dict["timestamp"] = '{}.000'.format(date_str)
        data_dict["symbol"] = symbol
        data_dict["columns"] = columns_list[0:3] + columns_list[5:]
        data_dict["type"] = tt_type
        data_dict["elementType"] = elementType
        data_dict["elementField"] = "indicatorsList"
        data_dict['details'] = data_details
        all_json_list.append(data_dict)

    return sorted(all_json_list, key=lambda x: x["timestamp"])


@ray.remote
def indexhdf52json_readh5(input_file, date_time):
    date_list = get_stock_date_list(date_time)
    json_dict = dict()
    input_file = get_real_input_file(input_file)
    json_key = input_file.split("/")[-1].split(".")[0]
    stock_name = input_file.split("/")[-1]
    stock_name = stock_name.replace('.h5', '')
    #        print(stock_name)
    h5 = pd.HDFStore(input_file)
    data = h5.select(stock_name, where="dt>='{}'&dt<='{}'".format(date_list[0], date_list[-1]))
    df = data.reset_index()
    json_dict[json_key] = df
    h5.close()
    return json_dict

def indexhdf52json(input_file_list, date_time):
    date_list = get_stock_date_list(date_time)
    all_json_list = list()

    demo_input_file = input_file_list[0]
    symbol, elementType, tt_type = get_sym_ele_type(demo_input_file)
    demo_input_file = get_real_input_file(input_file_list[0])
    tmp_data = pd.read_hdf(demo_input_file)
    tmp_df = tmp_data.reset_index()
    #    print(date_list[0])
    #    print(date_list[-1])
    json_dict = dict()
    json_dict_list = ray.get([indexhdf52json_readh5.remote(input_file, date_time) for input_file in input_file_list])
    for i in json_dict_list:
        json_dict.update(i)
    columns_list = get_index_columns_list(tmp_df)
    for date_str in date_list:
        data_dict = dict()
        recv_timestamp = (
                datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=1)).strftime(
            "%Y-%m-%d %H:%M:%S")
        data_dict["recvTimestamp"] = '{}.000'.format(recv_timestamp)
        data_dict["timestamp"] = '{}.000'.format(date_str)
        data_dict["symbol"] = symbol
        data_dict["columns"] = columns_list[0:2] + columns_list[4:]
        data_dict["type"] = tt_type
        data_dict["elementType"] = elementType
        data_dict["elementField"] = "indicatorsList"
        all_details_list = []

        for json_data in json_dict.values():
            # input_file = get_real_input_file(input_file)
            # data = pd.read_hdf(input_file)
            # df = data.reset_index()
            ddf = json_data[json_data["dt"] == date_str]
            details_list = []
            for row in ddf.itertuples():
                detail_list = []
                for i in row:
                    detail_list.append(i)
                detail_list.insert(3, False)
                if symbol == "FS_IF_1MIN" or symbol == "FS_IC_1MIN" or symbol == "FS_IH_1MIN" or symbol == "FS_IM_1MIN" \
                        or symbol == "FS_T_1MIN":
                    detail_list[2] = str(detail_list[2])[:-1]
                details_list.append(detail_list[2:])
            all_details_list += details_list
        data_dict["details"] = all_details_list
        all_json_list.append(data_dict)

    return sorted(all_json_list, key=lambda x: x["timestamp"])


def get_H5_data(input_file_list, dst_path, date_time):
    date_list = get_stock_date_list(date_time)

    for input_file in input_file_list:
        input_file = get_real_input_file(input_file)
        data = pd.read_hdf(input_file)
        df = data.reset_index()
        filename = input_file.split("/")[-1].split(".")[0]
        filename = dst_path + '/' + filename + '.csv'
        #        print(filename)
        data1 = df.loc[df["dt"].isin(date_list)]
        data1.to_csv(filename)


def write_json(json_list, output_file):
    with open(output_file, "w", ) as f:
        json.dump(json_list, f, cls=DateEncoder)


#        json.dump(json_list, f, indent=4, cls=DateEncoder)
#        json.dumps(data,f,separators=(',',':'))


def get_sym_ele_type(input_file, stock_type='sz50'):
    if "CHINA_FUTURES" in input_file:
        if 'IM_MINUTE.h5' in input_file:
            symbol = "FS_IM_1MIN"
        if "IF_MINUTE.h5" in input_file:
            symbol = "FS_IF_1MIN"
        elif "IC_MINUTE.h5" in input_file:
            symbol = "FS_IC_1MIN"
        elif "IH_MINUTE.h5" in input_file:
            symbol = "FS_IH_1MIN"
        elif "T_MINUTE.h5" in input_file:
            symbol = "FS_T_1MIN"
        elementType = "ZtFutureSymbolicIndicator"
        tt_type = "ZtFutureAggregatedSymbolicIndicator"
    elif "CHINA_INDEX" in input_file:
        symbol = "FS_INDEX_1MIN"
        elementType = "ZtIndexSymbolicIndicator"
        tt_type = "ZtIndexAggregatedSymbolicIndicator"
    elif "CHINA_STOCK" in input_file:
        if stock_type == 'hs300':
            symbol = "FS_000300CONS_1MIN"
            elementType = "ZtStockSymbolicIndicator"
            tt_type = "ZtStockAggregatedSymbolicIndicator"
        if stock_type == 'zz500':
            symbol = "FS_000905CONS_1MIN"
            elementType = "ZtStockSymbolicIndicator"
            tt_type = "ZtStockAggregatedSymbolicIndicator"
        if stock_type == 'sz50':
            symbol = "FS_000016CONS_1MIN"
            elementType = "ZtStockSymbolicIndicator"
            tt_type = "ZtStockAggregatedSymbolicIndicator"
        if stock_type == 'zz1000':
            symbol = "FS_000852CONS_1MIN"
            elementType = "ZtStockSymbolicIndicator"
            tt_type = "ZtStockAggregatedSymbolicIndicator"
 
    return symbol, elementType, tt_type


def get_available_file_name():
    fifty_path = r"/data/user/010793/FUTUREDATA/UNIVERSE/20201231_SZ50.csv"
    three_hundred_path = r"/data/user/010793/FUTUREDATA/UNIVERSE/20201231_HS300.csv"
    five_hundred_path = r"/data/user/010793/FUTUREDATA/UNIVERSE/20201231_ZZ500.csv"

    with open(fifty_path, 'r') as f:
        reader = csv.reader(f)
        temp_fifty_stock_path = [row[1] for row in reader]
    with open(three_hundred_path, 'r') as f:
        reader = csv.reader(f)
        temp_three_hundred_stock_path = [row[1] for row in reader]
    with open(five_hundred_path, 'r', encoding="UTF-8") as f:
        reader = csv.reader(f)
        temp_five_hundred_stock_path = [row[1] for row in reader]
    fifty_stock_path = temp_fifty_stock_path[1:]
    three_hundred_stock_path = temp_three_hundred_stock_path[1:]
    five_hundred_stock_path = temp_five_hundred_stock_path[1:]

    return fifty_stock_path, three_hundred_stock_path, five_hundred_stock_path


def get_available_file_name_from_xquant(date_str):
    #    获取当前交易日，定时任务设置在只在交易日19：00后运行
    #    date_str = time.strftime('%Y%m%d',time.localtime(time.time()))
    #    date_str = '20191215'
    #    print(date_str)
    #    判断预估明日的成分股是否调整

    try:
        s = FactorData()
        date_list = s.tradingday(date_str, 2)
        SZ50_data = s.hset('INDEX', date_list[1], 'SZ50', 1)
        HS300_data = s.hset('INDEX', date_list[1], 'HS300', 1)
        ZZ500_data = s.hset('INDEX', date_list[1], 'ZZ500', 1)
        ZZ1000_data = s.hset('INDEX', date_list[1], 'ZZ1000', 1)

        fifty_stock_path = SZ50_data['stock'].tolist()
        three_hundred_stock_path = HS300_data['stock'].tolist()
        five_hundred_stock_path = ZZ500_data['stock'].tolist()
        zz1000_stock_path = ZZ1000_data['stock'].tolist()

    except:
        print("权重文件读取异常")
        lm.sendMessage("权重文件读取异常")

    return fifty_stock_path, three_hundred_stock_path, five_hundred_stock_path, zz1000_stock_path


def get_input_file_list_new(public_input_path, stock_input_path, index_input_path, future_input_path, date_time):
    dir_list = os.listdir(public_input_path)
    # input_file_list = []
    for dir_name in dir_list:
        if dir_name == "CHINA_INDUSTRY" or dir_name == "UNIVERSE":
            continue
        elif dir_name == "CHINA_STOCK":
            fifty_stock_path_lists = []
            three_hundred_path_lists = []
            five_hundred_path_lists = []
            zz1000_path_lists = []
            fifty_stock_path_list, three_hundred_stock_path_list, five_hundred_stock_path_list, zz1000_stock_path_list = get_available_file_name_from_xquant(
                date_time)

            fifty_stock_path_list.sort()
            three_hundred_stock_path_list.sort()
            five_hundred_stock_path_list.sort()
            zz1000_stock_path_list.sort()

            for fifty_stock_path in fifty_stock_path_list:
                fifty_path = os.path.join(stock_input_path, "{}.h5".format(fifty_stock_path))
                fifty_stock_path_lists.append(fifty_path)
            for three_hundred_stock_path in three_hundred_stock_path_list:
                three_hundred_path = os.path.join(stock_input_path, "{}.h5".format(three_hundred_stock_path))
                three_hundred_path_lists.append(three_hundred_path)
            for five_hundred_stock_path in five_hundred_stock_path_list:
                five_hundred_path = os.path.join(stock_input_path, "{}.h5".format(five_hundred_stock_path))
                five_hundred_path_lists.append(five_hundred_path)
            for zz1000_stock_path in zz1000_stock_path_list:
                zz1000_path = os.path.join(stock_input_path, "{}.h5".format(zz1000_stock_path))
                zz1000_path_lists.append(zz1000_path)
        elif dir_name == "CHINA_FUTURES":
            china_futures_path_lists = []
            file_list = os.listdir(future_input_path)
            for file_name in file_list:
                if "MINUTE.h5" in file_name:
                    file_path = os.path.join(future_input_path, file_name)
                    china_futures_path_lists.append(file_path)

        elif dir_name == "CHINA_INDEX":
            china_index_path_lists = []
            file_list = os.listdir(index_input_path)
            for file_name in file_list:
                if "SH.h5" in file_name:
                    file_path = os.path.join(index_input_path, file_name)
                    china_index_path_lists.append(file_path)

    return fifty_stock_path_lists, three_hundred_path_lists, five_hundred_path_lists, zz1000_path_lists, china_futures_path_lists, china_index_path_lists


def Bar(arg):
    return arg


def zip_files(files, zip_name):
    zip = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for file in files:
        #        print ('compressing', file)
        zip.write(file)
    zip.close()


#    print ('compressing finished')
def str_convert(s):
    #    s = '20210101'
    s_l = list(s)
    s_l.insert(4, '-')
    s_l.insert(7, '-')
    s_m = ''.join(s_l)
    return s_m


if __name__ == '__main__':
    param = AIMR.getParam()
    #param = "20210922_20210922"
    lm.sendMessage(param)
    print(param)
    public_input_path = settings.PUBLIC_INPUT_PATH
    stock_input_path = settings.STOCK_INPUT_PATH
    index_input_path = settings.INDEX_INPUT_PATH
    future_input_path = settings.FUTURE_INPUT_PATH

    date_list = param.split('_')
    date_time = str_convert(date_list[0])
    print(date_time)
    format_date = date_time.replace('-', '')
    output_file = os.path.join(settings.MINUTEDATA_DIR, "tmp", format_date)
    fifty_stock_path_lists, three_hundred_path_lists, five_hundred_path_lists, zz1000_path_lists, china_futures_path_lists, \
    china_index_path_lists = get_input_file_list_new(public_input_path, stock_input_path, index_input_path, future_input_path, date_list[1])

    # 多进程
    ray.init(num_cpus=18)
    res_list = []
    a = time.time()

    print("begin fifty_stock_list")
    res_fifty = gpiaohdf52json(fifty_stock_path_lists, date_time, 'sz50')
    res_list += res_fifty

    print("begin three_hundred_list")
    res_three_hundred = gpiaohdf52json(three_hundred_path_lists, date_time, 'hs300')
    res_list += res_three_hundred

    print("begin five_hundred_json_list")
    res_five_hundred = gpiaohdf52json(five_hundred_path_lists, date_time, 'zz500')
    res_list += res_five_hundred

    print("begin zz1000_json_list")
    res_zz1000 = gpiaohdf52json(zz1000_path_lists, date_time, 'zz1000')
    res_list += res_zz1000

    print("begin china_index_list")
    res_index = indexhdf52json(china_index_path_lists, date_time)
    res_list += res_index

    print("begin china_futures")
    res_futures = hdf52json(china_futures_path_lists, date_time)
    res_list += res_futures

    all_json_list = res_list

    print("begin write_json")
    write_json(sorted(all_json_list, key=lambda x: x["timestamp"]), output_file)


    b = time.time()
    #    print(b-a)

    lm.sendMessage(date_time + ' data transfer done, delay: ' + str((b - a) / 60) + 'min')

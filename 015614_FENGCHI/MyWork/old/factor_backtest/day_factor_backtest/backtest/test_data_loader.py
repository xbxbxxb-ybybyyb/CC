import os
import pickle
import datetime as dt

depend_data_dict = {}
root_path = "/data/group/800080/factor_test/"
daily_store_path = os.path.join(root_path, "daily")
excess_return_root = os.path.join(root_path, "excess_return")


def get_industry_code_all(start_date, end_date):
    data = depend_data_dict.get("industry_code_all")
    if data is not None:
        return data[start_date:end_date]

    data = pickle.load(open(os.path.join(daily_store_path, 'industry_code_all.pkl'), "rb"))
    data.index = data.index.strftime("%Y%m%d")
    depend_data_dict["industry_code_all"] = data
    return data[start_date:end_date]


def get_mkt_cap_ard(start_date, end_date):
    data = depend_data_dict.get("mkt_cap_ard")
    if data is not None:
        return data[start_date:end_date]

    data = pickle.load(open(os.path.join(daily_store_path, 'mkt_cap_ard.pkl'), "rb"))
    data.index = data.index.strftime("%Y%m%d")
    depend_data_dict["mkt_cap_ard"] = data
    return data[start_date:end_date]


def get_price_data(price_type):
    data = depend_data_dict.get(price_type)
    if data is not None:
        return data

    data = pickle.load(open(os.path.join(daily_store_path, price_type + "_adj.pkl"), "rb"))
    data.index = data.index.strftime("%Y%m%d")
    depend_data_dict[price_type] = data
    return data


def get_is_valid_raw():
    data = depend_data_dict.get("is_valid_raw")
    if data is not None:
        return data
    data = pickle.load(open("/data/user/666889/Apollo/AlphaDataBase/is_valid_raw.pkl", "rb"))
    depend_data_dict["is_valid_raw"] = data
    return data


def get_is_universe():
    data = depend_data_dict.get("is_universe")
    if data is not None:
        return data
    data = pickle.load(open("/data/user/666889/Apollo/AlphaDataBase/is_universe.pkl", "rb"))
    data = data.astype(float)
    depend_data_dict["is_universe"] = data
    return data

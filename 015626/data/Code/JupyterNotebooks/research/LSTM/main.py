# -*- coding: utf-8 -*-

import pickle
import pandas as pd
from bilstm.regressor import BiLSTMRegressor


def train():
    minute = 5

    # set model
    model = BiLSTMRegressor()

    # load data
    dataset_file = "./data/dataset_all_202007_202012.pkl"

    print("loading data from {}".format(dataset_file))
    dataset = load_pickle(dataset_file)

    x_train = dataset["x_train_norm"]
    y_train = dataset["y_train_norm"][minute]
    x_valid = dataset["x_valid_norm"]
    y_valid = dataset["y_valid_norm"][minute]

    print("x_train: {:<15} from {:<20} to {:<20}".format(str(x_train.shape), str(x_train.index[0]), str(x_train.index[-1])))
    print("y_train: {:<15} from {:<20} to {:<20}".format(str(y_train.shape), str(y_train.index[0]), str(y_train.index[-1])))
    print("x_valid: {:<15} from {:<20} to {:<20}".format(str(x_valid.shape), str(x_valid.index[0]), str(x_valid.index[-1])))
    print("y_valid: {:<15} from {:<20} to {:<20}".format(str(y_valid.shape), str(y_valid.index[0]), str(y_valid.index[-1])))

    x_train_np = x_train.to_numpy()
    y_train_np = y_train.to_numpy()
    x_valid_np = x_valid.to_numpy()
    y_valid_np = y_valid.to_numpy()

    # train
    model.fit(x_train_np, y_train_np, x_valid_np, y_valid_np)

    # save model
    model_file = "./model/model.bilstm.{:02d}min.bin".format(minute)
    print("saving model to {}".format(model_file))
    model.save(model_file)

    # validate
    y_pred_np = model.predict(x_valid_np)
    y_pred_df = pd.DataFrame(data=y_pred_np, index=x_valid.index)

    # save results
    result_file = "./output/valid.bilstm.{:02d}min.pkl".format(minute)
    print("saving validation results to {}".format(result_file))
    save_pickle(y_pred_df, result_file)


def test():
    minute = 5

    # set model
    model = BiLSTMRegressor()

    # load model
    model_file = "./model/model.bilstm.{:02d}min.bin".format(minute)
    print("loading model from {}".format(model_file))
    model.load(model_file)

    # load data
    dataset_file = "./data/dataset_all_202007_202012.pkl"
    print("loading data from {}".format(dataset_file))
    dataset = load_pickle(dataset_file)

    x_test = dataset["x_test_norm"]

    print("x_test: {:<15} from {:<20} to {:<20}".format(str(x_test.shape), str(x_test.index[0]), str(x_test.index[-1])))

    x_test_np = x_test.to_numpy()

    # predict
    y_pred_np = model.predict(x_test_np)
    y_pred_df = pd.DataFrame(data=y_pred_np, index=x_test.index)

    # save results
    result_file = "./output/test.bilstm.{:02d}min.pkl".format(minute)
    print("saving testing results to {}".format(result_file))
    save_pickle(y_pred_df, result_file)


def load_pickle(data_file):
    with open(data_file, mode="rb") as file:
        data = pickle.load(file)
    return data


def save_pickle(data, data_file):
    with open(data_file, mode="wb") as file:
         pickle.dump(data, file)


if __name__ == "__main__":
    train()
    test()

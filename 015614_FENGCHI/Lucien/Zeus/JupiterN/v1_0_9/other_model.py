import sys
sys.path.append('../')
import os
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.utils.data as Data
from LucienUtil import IO
from datetime import datetime
from sklearn.metrics import auc
from sklearn.metrics import roc_curve
from sklearn.externals import joblib
from torch.autograd import Variable
import json
# import onnx
# from onnx_tf.backend import prepare


def func_model_eval_forward_pass(model, data_X_tf, data_Y_tf, shuffle_tag, batch_size):
    torch_dataset_eval = Data.TensorDataset(data_X_tf, data_Y_tf)
    loader_eval = Data.DataLoader(dataset=torch_dataset_eval, batch_size=batch_size, shuffle=shuffle_tag)
    eval_preds = np.array([0])
    eval_labels = np.array([0])
    eval_loss = []
    for step, (batch_x, batch_y) in enumerate(loader_eval):
        batch_x_cuda = batch_x.cuda()
        batch_y_cuda = batch_y.cuda()
        with torch.no_grad():
            prediction = model(batch_x_cuda)
            loss = criterion(prediction, batch_y_cuda)
        eval_loss.append(loss.item())
        prediction_array = prediction.cpu().data.numpy()
        labels_array = batch_y.data.numpy().reshape(-1, 1)
        if step == 0:
            eval_preds = prediction_array
            eval_labels = labels_array
        else:
            eval_preds = np.vstack([eval_preds, prediction_array])
            eval_labels = np.vstack([eval_labels, labels_array])
        del prediction
        del batch_x_cuda
        del batch_y_cuda
    eval_labels = np.squeeze(eval_labels)
    return eval_preds, eval_labels, np.mean(eval_loss)
def func_model_performance(eval_preds, eval_labels, positive_threshold):
    eval_positive_prob = eval_preds[:, -1]
    eval_positive_prob_transform = eval_positive_prob.copy()
    eval_positive_prob_transform = eval_positive_prob_transform - np.min(eval_positive_prob_transform)
    eval_positive_prob_transform = eval_positive_prob_transform / np.max(eval_positive_prob_transform)
    fpr, tpr, th = roc_curve(eval_labels, eval_positive_prob_transform, pos_label=1)
    eval_auc = auc(fpr, tpr)
    eval_prediction_label = np.array([0.0] * len(eval_positive_prob))
    eval_prediction_label[eval_positive_prob >= positive_threshold] = 1
    eval_precision = np.mean(eval_labels[eval_prediction_label == 1])
    eval_recall = np.mean(eval_prediction_label[eval_labels == 1])
    return eval_auc, eval_precision, eval_recall, eval_prediction_label

from dataApi.tradeDate import get_date_range
date_index =get_date_range(20160101, 20201231)
date_index = list(map(str, date_index))
#super params
train_window = 700
valid_window = 70
test_window = 7000
test_date_start = '20191008'
data_version = 'All_20160104_20200630'
model_version = '1'
model_save_version = '1'
test_date_start_before_end = '20190102'
test_date_start_before = '20190930'
test_date_back_watch = 0
test_back_watch_thres_tune_tag = False
save_java_model_tag = False
positive_threshold_test = 0.0100

# data_saveDir = '/data/user/015613/project_panStrong/data'
# model_saveDir = "/data/user/015613/project_panStrong/highwaynet/model/" + model_save_version
# result_saveDir = "/data/user/015613/project_panStrong/highwaynet/result"
# output_factor_saveDir = "/data/user/015613/project_panStrong/highwaynet"
# output_factor_name_test_label = 'jupiter_total_reg_test_v'+ model_version +'_test_label' ############
# output_factor_name_test_prob = 'jupiter_total_reg_test_v'+ model_version +'_test_prob' ############
# output_factor_name_valid_label = 'jupiter_total_reg_test_v'+ model_version +'_valid_label' ############
# output_factor_name_valid_prob = 'jupiter_total_reg_test_v'+ model_version +'_valid_prob' ############

#read data
# with open(data_saveDir + '/' + 'panStrong_manual_data_v' + data_version + '.pkl', 'rb') as f:
#     factor_data = joblib.load(f)
# factor_list_result_df = pd.read_excel('/data/user/015613/project_panStrong/data_select_result_hand_in/xgb_importance_20190102_allreg4.xlsx')
# factor_list_selected = list(factor_list_result_df[factor_list_result_df['corr_selected'] == 1]['factor_name'].values)
# factor_data = factor_data[factor_list_selected]
# print(factor_data.shape)
# date_index = np.array(list(np.unique(factor_data.index.get_level_values(level=0))))
# with open(data_saveDir + '/' + 'panStrong_manual_continuous_label_v' + data_version + '.pkl', 'rb') as f:
#     label_data = joblib.load(f)
# with open(data_saveDir + '/' + 'panStrong_manual_continuous_label_pct_v' + data_version + '.pkl', 'rb') as f:
#     label_data_pct = joblib.load(f)
# with open(data_saveDir + '/' + 'panStrong_manual_weighted_label_v' + data_version + '.pkl', 'rb') as f:
#     weighted_label_data = joblib.load(f)
# with open(data_saveDir + '/' + 'panStrong_manual_weighted_label_pct_v' + data_version + '.pkl', 'rb') as f:
#     weighted_label_pct_data = joblib.load(f)

# print('Before delete nans: ' + str(factor_data.shape[0]))
# factor_data = factor_data.dropna(axis=0)
# print('After delete nans: ' + str(factor_data.shape[0]))
# label_data = label_data.reindex(index=factor_data.index)
# label_data_pct = label_data_pct.reindex(index=factor_data.index)
# weighted_label_data = weighted_label_data.reindex(index=factor_data.index)
# weighted_label_pct_data = weighted_label_pct_data.reindex(index=factor_data.index)

#extra data
# rawData_dir = '/data/user/013600/factor_manager_v2/all_factor_bank/raw/all_factor_20150101_20211231.pkl'
# raw_data = pd.read_pickle(rawData_dir)
# raw_data = raw_data[['T_o2pre']].copy() #改成自己的分场景字段
#
# factor_num = len(factor_data.columns)

#model params
epoch_num = 500
early_stop_num = 30
valid_batch_size = 1000
dropout = 0.4
# input_size = factor_num
# hidden_1_size = int(input_size/2) #
hidden_2_size = 10 #
class_num = 1
#pytorch settings
# torch.set_default_tensor_type(torch.FloatTensor)
# print(model_saveDir)
#model
class HighwayNet(nn.Module):
    def __init__(self, in_dim, hidden_1_size, hidden_2_size, out_dim):
        super(HighwayNet, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(in_dim, hidden_1_size), nn.BatchNorm1d(hidden_1_size), nn.SELU(True), nn.Dropout(dropout))
        self.layer2 = nn.Sequential(nn.Linear(hidden_1_size, hidden_2_size), nn.BatchNorm1d(hidden_2_size), nn.SELU(True), nn.Dropout(dropout))
        self.layer3 = nn.Sequential(nn.Linear(hidden_2_size, hidden_2_size), nn.BatchNorm1d(hidden_2_size), nn.SELU(True), nn.Dropout(dropout))
        self.layer4 = nn.Sequential(nn.Linear(hidden_2_size, out_dim), nn.Tanh())
    def forward(self, input_data):
        out = self.layer1(input_data)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        return out

#generate back_test_list
tag_start = 0
for index, date in enumerate(date_index):
    date_ts = pd.to_datetime(date)
    date_str = datetime.strftime(date_ts, '%Y%m%d')
    if date_str >= test_date_start:
        tag_start = index
        break
back_test_date_list = date_index[tag_start:]
test_date_list = []
temp_date_list = []
for date in back_test_date_list:
    temp_date_list.append(date)
    if len(temp_date_list) == test_window:
        test_date_list.append(temp_date_list)
        temp_date_list = []
        test_window = 1000
    elif date == back_test_date_list[-1]:
        test_date_list.append(temp_date_list)
        temp_date_list = []
    elif datetime.strftime(pd.to_datetime(date), '%Y%m%d') == '20201231':
        test_date_list.append(temp_date_list)
        temp_date_list = []
        test_window = 1000
    else:
        pass
#start backtest
output_factor_test_label = pd.DataFrame()
output_factor_test_prob = pd.DataFrame()
output_factor_valid_label = pd.DataFrame()
output_factor_valid_prob = pd.DataFrame()
count = 1
count_for_test_date_list = len(test_date_list)
for temp_i, date_list in enumerate(test_date_list):
    #generate data
    tag_index = list(date_index).index(date_list[0])
    if tag_index - train_window - valid_window < 0:
        train_date_list = date_index[0:tag_index-valid_window]
    else:
        train_date_list = date_index[tag_index-train_window-valid_window:tag_index-valid_window]

    valid_date_list = date_index[tag_index-valid_window:tag_index]

    if temp_i == count_for_test_date_list - 1:
        temp_temp_result = 0
        for temp_temp_count, temp_temp in enumerate(list(date_index)):
            temp_temp_str = datetime.strftime(pd.to_datetime(date_index[temp_temp_count]), '%Y%m%d')
            if temp_temp_str == test_date_start_before_end:
                temp_temp_result = temp_temp_count
                break
        test_date_list = np.array(list(date_index[temp_temp_result:tag_index]) + list(date_list)) #######################
    else:
        test_date_list = date_list

    temp_train_start_date_str = datetime.strftime(pd.to_datetime(train_date_list[0]), '%Y%m%d')
    temp_valid_start_date_str = datetime.strftime(pd.to_datetime(valid_date_list[0]), '%Y%m%d')
    temp_test_start_date_str = datetime.strftime(pd.to_datetime(test_date_list[0]), '%Y%m%d')
    temp_train_end_date_str = datetime.strftime(pd.to_datetime(train_date_list[-1]), '%Y%m%d')
    temp_valid_end_date_str = datetime.strftime(pd.to_datetime(valid_date_list[-1]), '%Y%m%d')
    temp_test_end_date_str = datetime.strftime(pd.to_datetime(test_date_list[-1]), '%Y%m%d')
    test_date_back_watch = temp_test_start_date_str
    print('train start:' + temp_train_start_date_str + ', valid start:' + temp_valid_start_date_str + ', test start:' + temp_test_start_date_str + '.')
    print('train end:' + temp_train_end_date_str + ', valid end:' + temp_valid_end_date_str + ', test end:' + temp_test_end_date_str + '.')

    train_X = factor_data.loc[train_date_list,:].copy()
    before_train_nums = len(train_X)
    #################
    #结合raw_data改成分场景数据
    #################
    after_train_nums = len(train_X)
    print('train ratio: ' + str(after_train_nums / before_train_nums))

    valid_X = factor_data.loc[valid_date_list,:].copy()
    before_valid_nums = len(valid_X)
    #################
    # 结合raw_data改成分场景数据
    #################
    after_valid_nums = len(valid_X)
    print('valid ratio: ' + str(after_valid_nums / before_valid_nums))

    test_X = factor_data.loc[test_date_list,:].copy()
    #################
    # 结合raw_data改成分场景数据
    #################

    print(str(train_X.shape[0])+' train, '+str(valid_X.shape[0])+' valid, '+str(test_X.shape[0])+' test.')
    train_Y_for_balance = np.squeeze(label_data.reindex(index=train_X.index).values)
    train_X_for_balance = train_X.values.copy()

    train_Y_label_for_balance = train_Y_for_balance.copy()
    train_Y_label_for_balance[train_Y_label_for_balance >= 0.0] = 1.0
    train_Y_label_for_balance[train_Y_label_for_balance < 0.0] = 0.0

    train_X_for_balance_positive = train_X_for_balance[train_Y_label_for_balance == 1]
    train_X_for_balance_negative = train_X_for_balance[train_Y_label_for_balance == 0]
    train_Y_for_balance_positive = train_Y_for_balance[train_Y_label_for_balance == 1]
    train_Y_for_balance_negative = train_Y_for_balance[train_Y_label_for_balance == 0]

    train_X_balanced = train_X_for_balance
    train_Y_balanced = train_Y_for_balance
    data_num_total = len(train_X_for_balance)
    class_weight = [len(train_X_for_balance_positive) / data_num_total, len(train_X_for_balance_negative) / data_num_total]  # reverse

    #data scaler
    data_scaler_dict = {}
    train_X_array = []
    valid_X_array = []
    test_X_array = []
    for i in range(factor_num):
        temp_factor_name = list(train_X.columns)[i]
        temp_train_X = train_X_balanced[:, i].copy()
        temp_valid_X = valid_X.iloc[:, i].values.copy()
        temp_test_X = test_X.iloc[:, i].values.copy()

        n, median, MAD, train_min, train_max = my_scaler_fit_minmax_MAD(temp_train_X, 5)
        data_scaler_dict[temp_factor_name] = [train_min, train_max, median - n * MAD, median + n * MAD]
        train_data_scalered = my_scaler_transform_minmax_MAD(temp_train_X, n, median, MAD, train_min, train_max, -1, 1)
        valid_data_scalered = my_scaler_transform_minmax_MAD(temp_valid_X, n, median, MAD, train_min, train_max, -1, 1)
        test_data_scalered = my_scaler_transform_minmax_MAD(temp_test_X, n, median, MAD, train_min, train_max, -1, 1)

        train_data_scalered_reshape = train_data_scalered.reshape(-1, 1)
        valid_data_scalered_reshape = valid_data_scalered.reshape(-1, 1)
        test_data_scalered_reshape = test_data_scalered.reshape(-1, 1)
        train_X_array.append(train_data_scalered_reshape)
        valid_X_array.append(valid_data_scalered_reshape)
        test_X_array.append(test_data_scalered_reshape)
    train_X_array = np.hstack(train_X_array)
    valid_X_array = np.hstack(valid_X_array)
    test_X_array = np.hstack(test_X_array)

    #save firm offer data
    FilePath = result_saveDir + '/' + temp_test_end_date_str + '_jupiterN_test' +'/'
    if save_java_model_tag:
        if not os.path.exists(FilePath):
            os.makedirs(FilePath)
            print("creat folder " + FilePath)
        with open(FilePath + 'test_date_range' + '.pkl', 'wb') as f:
            joblib.dump([temp_test_start_date_str, temp_test_end_date_str], f)
        with open(FilePath + 'factor_scaler_dict' + '.pkl', 'wb') as f:
            joblib.dump(data_scaler_dict, f)
        jsontext = []
        for factor in list(train_X.columns):
            # print(factor)
            temp_json_data = {'factorName': factor}
            temp_min_max = data_scaler_dict[factor]
            temp_json_data['min'] = temp_min_max[0]
            temp_json_data['max'] = temp_min_max[1]
            temp_json_data['min_mad'] = temp_min_max[2]
            temp_json_data['max_mad'] = temp_min_max[3]
            jsontext.append(temp_json_data)
        jsondata = json.dumps(jsontext, indent=2, separators=(',', ': '))
        f = open(FilePath + 'factor_scaler_dict.json', 'w')
        f.write(jsondata)
        f.close()
        with open(FilePath + 'factor_name' + '.pkl', 'wb') as f:
            joblib.dump(list(train_X.columns), f)
        jsontext = []
        for factor in list(train_X.columns):
            jsontext.append(factor)
        jsondata = json.dumps(jsontext, indent=2, separators=(',', ': '))
        f = open(FilePath + 'factor_name.json', 'w')
        f.write(jsondata)
        f.close()

    train_Y_array = train_Y_balanced
    train_Y_array_weight_for_loss = np.ones([len(train_Y_array), 1])
    train_Y_array = train_Y_array.reshape(-1, 1)

    valid_Y_array = np.squeeze(label_data.reindex(index=valid_X.index).values)
    valid_Y_array_weight_for_loss = np.ones([len(valid_Y_array), 1])
    valid_Y_array = valid_Y_array.reshape(-1, 1)

    test_Y_array = np.squeeze(label_data.reindex(index=test_X.index).values)
    test_Y_array_weight_for_loss = np.ones([len(test_Y_array), 1])
    test_Y_array = test_Y_array.reshape(-1, 1)

    # generate model
    model = HighwayNet(input_size, hidden_1_size, hidden_2_size, class_num).cuda()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-6)

    #start training
    print('start training')
    starttime = time.time()
    train_X_tf = torch.from_numpy(train_X_array).float()
    train_Y_tf = torch.from_numpy(train_Y_array).float()
    valid_X_tf = torch.from_numpy(valid_X_array).float()
    valid_Y_tf = torch.from_numpy(valid_Y_array).float()
    test_X_tf = torch.from_numpy(test_X_array).float()
    test_Y_tf = torch.from_numpy(test_Y_array).float()
    train_Y_array_weight_for_loss_tf = torch.from_numpy(train_Y_array_weight_for_loss).float()
    valid_Y_array_weight_for_loss_tf = torch.from_numpy(valid_Y_array_weight_for_loss).float()
    test_Y_array_weight_for_loss_tf = torch.from_numpy(test_Y_array_weight_for_loss).float()

    torch_dataset = Data.TensorDataset(train_X_tf, train_Y_tf)
    loader = Data.DataLoader(dataset=torch_dataset, batch_size=128, shuffle=True)
    best_evaluation = 0.0
    best_state = []
    not_boost_count = 0
    model_save_dir = model_saveDir + '/' + 'model_' + temp_test_end_date_str + '.pth'
    start_tag = 0
    for epoch in range(epoch_num):
        model.train()
        for step, (batch_x, batch_y) in enumerate(loader):
            batch_x_cuda = batch_x.cuda()
            batch_y_cuda = batch_y.cuda()
            prediction = model(batch_x_cuda)
            loss = criterion(prediction, batch_y_cuda)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        model.eval()
        # cal train evaluation
        if epoch % 1 == 0:
            train_preds, train_labels, train_loss = func_model_eval_forward_pass(model, train_X_tf, train_Y_tf, False, valid_batch_size)
        else:
            train_loss = np.nan
        # cal valid evaluation
        valid_preds, valid_labels, valid_loss = func_model_eval_forward_pass(model, valid_X_tf, valid_Y_tf, False, valid_batch_size)
        valid_weighted_label = weighted_label_data.reindex(index=valid_X.index)
        valid_weighted_label = np.argmax(valid_weighted_label.values, axis=1)
        best_valid_prob = positive_threshold_test#tranformed_threshold
        valid_auc, valid_precision, valid_recall, valid_prediction_label = func_model_performance(valid_preds, valid_weighted_label, best_valid_prob)

        print('epoch:'+str(epoch)+', '+'valid:' + str(round(valid_loss, 4)) + ',' + str(round(valid_auc, 4)) + ',' + str(round(valid_precision, 4)) + ',' + str(round(valid_recall, 4)) + '.')

        if valid_auc >= best_evaluation and epoch > 5:
            start_tag = 1
            torch.save(model.state_dict(), model_save_dir)
            not_boost_count = 0
            best_evaluation = valid_auc
            best_state = [valid_loss, valid_auc, valid_precision, valid_recall]
        else:
            if start_tag:
                not_boost_count = not_boost_count + 1
            if not_boost_count >= early_stop_num:
                print('The evaluation has not been improved in finite epoch')
                break
    print('valid:' + str(round(best_state[0], 4)) + ', ' + str(round(best_state[1], 4)) + ', ' + str(round(best_state[2], 4)) + ', ' + str(round(best_state[3], 4)))
    model.load_state_dict(torch.load(model_save_dir))
    model.eval()

    if save_java_model_tag:
        torch.save(model.state_dict(), FilePath + 'model_' + temp_test_end_date_str + '.pth')
        # arrange model
        model.cpu()
        # convert pytorch to onnx
        dummy_input = Variable(torch.randn(1, input_size))
        torch.onnx.export(model, dummy_input, FilePath + 'model_' + temp_test_end_date_str + '.onnx')
        model.cuda()
        # convert onnx to tf
        model_onnx = onnx.load(FilePath + 'model_' + temp_test_end_date_str + '.onnx')
        model_tf = prepare(model_onnx)
        model_tf.export_graph(FilePath + 'model_' + temp_test_end_date_str + '.pb')

    valid_preds, valid_labels, valid_loss = func_model_eval_forward_pass(model, valid_X_tf, valid_Y_tf, False, valid_batch_size)
    valid_weighted_label = weighted_label_pct_data.reindex(index=valid_X.index)
    valid_weighted_label = np.argmax(valid_weighted_label.values, axis=1)
    best_valid_prob = positive_threshold_test#tranformed_threshold_for_test
    valid_auc, valid_precision, valid_recall, valid_prediction_label = func_model_performance(valid_preds, valid_weighted_label, best_valid_prob)
    print('valid:' + str(round(best_valid_prob, 4)) + ',' + str(round(valid_auc, 4)) + ',' + str(round(valid_precision, 4)) + ',' + str(round(valid_recall, 4)) + '.')

    test_preds, test_labels, test_loss = func_model_eval_forward_pass(model, test_X_tf, test_Y_tf, False, valid_batch_size)


    test_weighted_label = weighted_label_pct_data.reindex(index=test_X.index)
    test_weighted_label = np.argmax(test_weighted_label.values, axis=1)
    test_auc, test_precision, test_recall, test_prediction_label = func_model_performance(test_preds, test_weighted_label,  best_valid_prob)
    print('test:' + str(round(best_valid_prob, 4)) + ',' + str(round(test_auc, 4)) + ',' + str(round(test_precision, 4)) + ',' + str(round(test_recall, 4)) + '.')

    output_array_valid = valid_preds.copy()
    output_array_valid[output_array_valid >= best_valid_prob] = 1
    output_array_valid[output_array_valid < best_valid_prob] = 0
    output_array = test_preds.copy()
    output_array[output_array >= best_valid_prob] = 1
    output_array[output_array < best_valid_prob] = 0
    print(np.sum(output_array))

    # save result
    valid_Y = label_data.reindex(index=valid_X.index)
    tmp_output_factor_valid_label = pd.DataFrame(output_array_valid, index=valid_Y.index, columns=[output_factor_name_valid_label])
    tmp_output_factor_valid_prob = pd.DataFrame(valid_preds, index=valid_Y.index, columns=[output_factor_name_valid_prob])
    if count == 1:
        output_factor_valid_label = tmp_output_factor_valid_label
        output_factor_valid_prob = tmp_output_factor_valid_prob
    else:
        original_index_set = set(output_factor_valid_label.index)
        add_index_set = set(tmp_output_factor_valid_label.index)
        diff_set = add_index_set - original_index_set
        diff_index_list = list(diff_set)
        add_index_list = []
        for temp_add_index in list(tmp_output_factor_valid_label.index):
            if temp_add_index in diff_index_list:
                add_index_list.append(temp_add_index)
        tmp_output_factor_valid_label = tmp_output_factor_valid_label.reindex(index=add_index_list)
        output_factor_valid_label = pd.concat([output_factor_valid_label, tmp_output_factor_valid_label], axis=0)
        tmp_output_factor_valid_prob = tmp_output_factor_valid_prob.reindex(index=add_index_list)
        output_factor_valid_prob = pd.concat([output_factor_valid_prob, tmp_output_factor_valid_prob], axis=0)
    output_abs_dir = output_factor_saveDir + '/' + output_factor_name_valid_label + '.h5'
    if not os.path.exists(output_abs_dir):
        IO.pd_hdf5_writer(output_factor_valid_label, output_abs_dir, dataset=output_factor_name_valid_label)
    else:
        IO.pd_hdf5_writer(output_factor_valid_label, output_abs_dir, dataset=output_factor_name_valid_label, override=True)
    output_abs_dir = output_factor_saveDir + '/' + output_factor_name_valid_prob + '.h5'
    if not os.path.exists(output_abs_dir):
        IO.pd_hdf5_writer(output_factor_valid_prob, output_abs_dir, dataset=output_factor_name_valid_prob)
    else:
        IO.pd_hdf5_writer(output_factor_valid_prob, output_abs_dir, dataset=output_factor_name_valid_prob, override=True)

    test_Y = label_data.reindex(index=test_X.index)
    tmp_output_factor_test_label = pd.DataFrame(output_array, index=test_Y.index, columns=[output_factor_name_test_label])
    tmp_output_factor_test_prob = pd.DataFrame(test_preds, index=test_Y.index, columns=[output_factor_name_test_prob])
    if count == 1:
        output_factor_test_label = tmp_output_factor_test_label
        output_factor_test_prob = tmp_output_factor_test_prob
    else:
        original_index_set = set(output_factor_test_label.index)
        add_index_set = set(tmp_output_factor_test_label.index)
        diff_set = add_index_set - original_index_set
        diff_index_list = list(diff_set)
        add_index_list = []
        for temp_add_index in list(tmp_output_factor_test_label.index):
            if temp_add_index in diff_index_list:
                add_index_list.append(temp_add_index)
        tmp_output_factor_test_label = tmp_output_factor_test_label.reindex(index=add_index_list)
        output_factor_test_label = pd.concat([output_factor_test_label, tmp_output_factor_test_label], axis=0)
        tmp_output_factor_test_prob = tmp_output_factor_test_prob.reindex(index=add_index_list)
        output_factor_test_prob = pd.concat([output_factor_test_prob, tmp_output_factor_test_prob], axis=0)
        output_factor_test_label = output_factor_test_label.sort_index()
        output_factor_test_prob = output_factor_test_prob.sort_index()

    output_abs_dir = output_factor_saveDir + '/' + output_factor_name_test_label + '.h5'
    if not os.path.exists(output_abs_dir):
        IO.pd_hdf5_writer(output_factor_test_label, output_abs_dir, dataset=output_factor_name_test_label)
    else:
        IO.pd_hdf5_writer(output_factor_test_label, output_abs_dir, dataset=output_factor_name_test_label, override=True)
    output_abs_dir = output_factor_saveDir + '/' + output_factor_name_test_prob + '.h5'
    if not os.path.exists(output_abs_dir):
        IO.pd_hdf5_writer(output_factor_test_prob, output_abs_dir, dataset=output_factor_name_test_prob)
    else:
        IO.pd_hdf5_writer(output_factor_test_prob, output_abs_dir, dataset=output_factor_name_test_prob, override=True)
    count = count + 1
    endtime = time.time()
    print("This itr running time: " + str(int(endtime - starttime)))

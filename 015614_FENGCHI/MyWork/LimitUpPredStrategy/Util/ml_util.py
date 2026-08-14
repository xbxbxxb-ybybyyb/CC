# coding: utf-8
# Author：fengchi863
# Date ：2021/3/26 11:28

from sklearn import metrics

def calc_metrics(y_test, y_pred):
    accuracy = metrics.accuracy_score(y_test, y_pred)
    precision = metrics.precision_score(y_test, y_pred)
    recall = metrics.recall_score(y_test, y_pred)
    f1_score = metrics.f1_score(y_test, y_pred)
    print('准确率：%.4f，精准率：%.4f，召回率：%.4f， F1分数：%.4f' %
          (accuracy, precision, recall, f1_score))
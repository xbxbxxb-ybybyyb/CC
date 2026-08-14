import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import xgboost as xgb
from collections import defaultdict
from copy import deepcopy
import random

# 生成一个虚构的分类数据集示例（你可以替换为真实数据）
X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=0, random_state=42)
X = pd.DataFrame(X)
y = pd.Series(y)

# 划分训练集和测试集（这里测试集主要是为了遵循常规流程，在这个示例里重点在训练集特征选择上）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Boruta算法类
class BorutaXGB:
    def __init__(self, estimator=xgb.XGBClassifier(random_state=42), n_estimators=100, max_iter=100):
        """
        初始化BorutaXGB对象
        参数:
        estimator: 使用的基础估计器，默认为XGBClassifier，可替换为其他XGB模型或合适的模型
        n_estimators: 基础估计器中树的数量，默认为100
        max_iter: 最大迭代次数，默认为100
        """
        self.estimator = estimator
        self.estimator.set_params(n_estimators=n_estimators)
        self.max_iter = max_iter
        self.selected_features = []
        self.rejected_features = []
        self.importance_history = defaultdict(list)

    def _create_shadow_features(self, X):
        """
        为原始特征创建影子特征
        参数:
        X: 特征矩阵
        返回:
        包含原始特征和影子特征的新特征矩阵
        """
        num_features = X.shape[1]
        shadow_X = deepcopy(X)
        for col in X.columns:
            # 打乱特征值来创建影子特征
            shadow_X[col + '_shadow'] = random.sample(list(X[col]), len(X[col]))
        return shadow_X

    def _fit_estimator(self, X, y):
        """
        使用给定数据拟合估计器并返回特征重要性

        参数:
        X: 特征矩阵
        y: 目标变量

        返回:
        特征重要性字典，键为特征名，值为重要性得分
        """
        self.estimator.fit(X, y)
        feature_importance = self.estimator.feature_importances_
        feature_importance_dict = dict(zip(X.columns, feature_importance))
        return feature_importance_dict

    def _compare_importance(self, feature_importance, shadow_importance):
        """
        比较原始特征和影子特征的重要性，确定重要特征、暂定特征和拒绝特征

        参数:
        feature_importance: 原始特征重要性字典
        shadow_importance: 影子特征重要性字典

        返回:
        三个列表，分别为重要特征、暂定特征、拒绝特征的名称列表
        """
        important_features = []
        tentative_features = []
        rejected_features = []

        max_shadow_importance = max(shadow_importance.values())
        for feature, importance in feature_importance.items():
            if feature.endswith('_shadow'):
                continue
            if importance > max_shadow_importance:
                important_features.append(feature)
            elif importance == max_shadow_importance:
                tentative_features.append(feature)
            else:
                rejected_features.append(feature)

        return important_features, tentative_features, rejected_features

    def fit(self, X, y):
        """
        运行Boruta算法进行特征选择

        参数:
        X: 训练集特征矩阵
        y: 训练集目标变量
        """
        X_with_shadow = self._create_shadow_features(X)
        iteration = 0
        while iteration < self.max_iter:
            feature_importance = self._fit_estimator(X_with_shadow, y)
            # 分离原始特征和影子特征的重要性字典
            original_feature_importance = {k: v for k, v in feature_importance.items() if not k.endswith('_shadow')}
            shadow_feature_importance = {k: v for k, v in feature_importance.items() if k.endswith('_shadow')}
            important, tentative, rejected = self._compare_importance(original_feature_importance,
                                                                      shadow_feature_importance)
            self.selected_features.extend(important)
            self.rejected_features.extend(rejected)
            for feature in tentative:
                self.importance_history[feature].append(original_feature_importance[feature])
            if len(tentative) == 0:
                break
            # 去除已确定为不重要和已选择的特征，重新构建特征矩阵进行下一轮迭代
            remaining_features = [col for col in X.columns if col not in self.rejected_features + self.selected_features]
            X = X[remaining_features]
            X_with_shadow = self._create_shadow_features(X)
            iteration += 1

        return self.selected_features
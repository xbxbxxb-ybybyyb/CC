import numpy as np
from xgboost import XGBClassifier

X_train = np.random.randn(10,8)
y_train = np.concatenate([np.ones(5),np.zeros(5)],0)
X_test = np.random.randn(6,8)
y_test = np.concatenate([np.ones(3),np.zeros(3)],0)

clf = XGBClassifier(objective='binary:logistic', colsample_bytree=0.8, learning_rate=0.2, max_depth=4, subsample=0.9, n_estimators=300, use_label_encoder=False)
clf.fit(X_train, y_train, early_stopping_rounds=50, eval_metric="auc", eval_set=[(X_test, y_test)], verbose=True)
train_predict = clf.predict(X_train)
yp = clf.predict_proba(X_test)  # [6,2] 第一列是预测为第一类的概率，第二列是预测为第二类的概率

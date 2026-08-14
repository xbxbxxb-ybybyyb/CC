import pandas as pd
import time
import os

def prepare_model_fold(model_name, model_root):

    sub_folds = ['conf', 'train', 'test', 'pred', 'analyse']
    for f in sub_folds:
        path = f'{model_root}/{model_name}/{f}/'
        if not os.path.exists(path):
            os.makedirs(path)

def set_model():

    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    return model

def train_model(X_train, y_train, d_train, c_train, ry_train, model, model_name, model_root, model_idx):

    model.fit(X_train, y_train)
    from sklearn.externals import joblib
    joblib.dump(model, f'{model_root}/{model_name}/conf/{model_idx}.pkl')
    yh_train = model.predict(X_train)
    df_train = pd.DataFrame({'date': d_train, 'code': c_train, 'ry': ry_train, 'y': y_train, 'yh': yh_train})
    df_train.to_pickle(f'{model_root}/{model_name}/train/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model

def pred_model(X, y, d, c, ry, model, model_name, model_root, model_idx, pred_type='pred'):

    yh = model.predict(X)
    df_pred = pd.DataFrame({'date': d, 'code': c, 'ry': ry, 'y': y, 'yh': yh})
    df_pred.to_pickle(f'{model_root}/{model_name}/{pred_type}/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish {pred_type} model {model_idx}')

def load_model(model_name, model_root, model_idx):

    from sklearn.externals import joblib
    model = joblib.load(f'{model_root}/{model_name}/conf/{model_idx}.pkl')
    return model

if __name__ == '__main__':

    model_root = '/arch1/user/015836/HFmodel/MorningModel/LR/OLS/'
    model_name = '20210402TSF400T488P10'
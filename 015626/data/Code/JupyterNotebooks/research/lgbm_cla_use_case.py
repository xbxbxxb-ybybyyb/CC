import gc,json,sys,os,random
import dill as pickle
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier,CatBoostRegressor
import lightgbm as lgb
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor,ExtraTreesClassifier,ExtraTreesRegressor
from sklearn.model_selection import KFold,StratifiedKFold,TimeSeriesSplit
from sklearn.linear_model import LinearRegression,ElasticNetCV,ElasticNet,Lasso,RandomizedLasso,LassoLarsIC,HuberRegressor,LassoCV,LogisticRegressionCV,LogisticRegression


from functools import partial
import matplotlib.pyplot as plt
plt.style.use('ggplot')



seed = 2018
np.random.seed(seed)
random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)

def set_seed(seed=2018):
	os.environ['PYTHONHASHSEED'] = str(seed)	
	random.seed(seed)
	np.random.seed(seed)
	try:
		tf.set_random_seed(seed)
		os.environ['TF_DETERMINISTIC_OPS'] = '1' 
		os.environ['TF_CUDNN_DETERMINISTIC'] = '1'
		os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
	except:
		1==1
	return

set_seed()


def get_sample_weight_helper(y_train_k,weight_type='abs_ret',filter_cut=2,trunc_pct=None):
	y_train_label_k = y_train_k.copy()
	y_train_label_k[y_train_k>0] = 1
	y_train_label_k[y_train_k<=0] = 0
	y_train_weight_k = get_sample_weight(y_train_k,weight_type,filter_cut,trunc_pct)
	return y_train_weight_k,y_train_label_k

def get_sample_weight(y_train,weight_type='abs_ret',filter_cut=2,trunc_pct=None):
    if weight_type not in ['abs_ret','sharpe','ret_square']:
        print('weight_type error')
        raise Exception
    if isinstance(y_train,pd.DataFrame):
        y_use = y_train.iloc[:,0]
    else:
        y_use = y_train
    if trunc_pct is not None:
        y_use = get_data_trunc(y_use,cut_limit=trunc_pct)
    if weight_type=='abs_ret':
        y_train_abs = np.abs(y_use)
        y_train_weight = y_train_abs/np.sum(y_train_abs) * len(y_train_abs)
    elif weight_type == 'sharpe':
        ret = y_use
        ret_abs = np.abs(ret)
        ret_vol = ret.rolling(120,1).std()
        ret_sharpe_abs = ret_abs/ret_vol
        ret_sharpe_abs = ret_sharpe_abs.fillna(0)
        y_train_weight = ret_sharpe_abs/np.sum(ret_sharpe_abs) * len(ret_sharpe_abs)
    elif weight_type == 'ret_square':
        ret_sqr = y_use**2
        y_train_weight = ret_sqr/np.sum(ret_sqr) * len(ret_sqr)    
    if filter_cut is not None:
        y_train_weight[y_train_weight>filter_cut] = filter_cut
    return y_train_weight


def fold_split_helper(x_train,y_train,fold_num,shuffle=False,tsp=False,random_state=2018):
	os.environ['PYTHONHASHSEED'] = str(random_state)	
	random.seed(random_state)
	np.random.seed(random_state)		
	if shuffle:
		folds = KFold(n_splits=fold_num,shuffle=shuffle,random_state=random_state)
		splits = folds.split(x_train, y_train)
	else:
		if tsp:
			folds = TimeSeriesSplit(n_splits=fold_num)
			splits = folds.split(x_train, y_train)
		else:
			folds = KFold(n_splits=fold_num,random_state=random_state)
			if isinstance(x_train.index,pd.MultiIndex):
				date_info = x_train.index.get_level_values(0).date
			else:
				date_info = x_train.index.date
			splits = folds.split(x_train, y_train, date_info)
	return splits
	

def learning_rate_decay_power(current_iter,base_learning_rate=0.001,lr_decay=0.999,min_ratio=0.5):
	lr = base_learning_rate  * np.power(lr_decay, current_iter)
	min_lr = base_learning_rate*min_ratio
	return lr if lr >min_lr  else min_lr


def pred_template(x,model,pred='regression',best_iteration=False):
	if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
		x_type = 'pd'
		x_np = x.values
	else:
		x_type = 'np'
		x_np = x
	if pred=='regression':
		y_mat = model.predict(x_np)
	else:
		if len(x_np.shape)>2:
			y_mat = model.predict_proba(x_np).flatten()
		else:
			if best_iteration:
				y_mat = model.predict_proba(x_np,ntree_limit=model.best_iteration)[:, 1]
			else:
				y_mat_temp = model.predict_proba(x_np)
				if np.shape(y_mat_temp)[1] > 2:
					y_mat = y_mat_temp[:, -1] - y_mat_temp[:, 0]
				else:
					y_mat = y_mat_temp[:, 1]
	
	if x_type == 'pd':
		y = pd.Series(y_mat.flatten(),index=x.index)
	else:
		y = y_mat
	return y    


def collect_feature_importance_helper(model=None,x_train=None):
	""" if model is None, return dummy list to track factor used """
	if isinstance(x_train.index,pd.MultiIndex):
		col = x_train.index[-1][0]
	else:
		col = x_train.index[-1]
	if model is None:
		fi_raw = np.zeros(len(x_train.columns))
	else:
		if type(model) in [xgb.XGBClassifier,xgb.XGBRegressor,RandomForestClassifier,lgb.LGBMRegressor,lgb.LGBMClassifier,
						   ExtraTreesClassifier,ExtraTreesRegressor]:
			fi_raw = model.feature_importances_
		elif type(model) in [Lasso,ElasticNet,LassoCV,LinearRegression,LassoLarsIC,HuberRegressor]:
			fi_raw = model.coef_
		elif type(model) in [LogisticRegression]:
			fi_raw = model.coef_[0]
		elif type(model) in [RandomizedLasso]:
			fi_raw = model.scores_
		else:
			print ('feature importance model not covered: %s'%(model))
			raise Exception
	feature_importance = pd.DataFrame(fi_raw,index=x_train.columns,columns=[col])
	return feature_importance


def collect_model_score_helper(model,x_train,y_train,validation_pct=None):
	if isinstance(x_train.index,pd.MultiIndex):
		col = x_train.index[-1][0]
	else:
		col = x_train.index[-1]
	if type(model) in [xgb.XGBClassifier,xgb.XGBRegressor]:
		#if validation_pct is not None:
		if isinstance(y_train,pd.DataFrame):
			model_score = pd.DataFrame([model.best_score],index=y_train.columns,columns=[col])
		else:
			model_score = pd.Series(model.best_score,index=[col])
		#else:
		#    model_score = np.nan
	elif type(model) in [lgb.LGBMRegressor,lgb.LGBMClassifier]:
		if isinstance(y_train,pd.DataFrame):
			model_score = pd.DataFrame(list(model.best_score_['valid'].values()),index=y_train.columns,columns=[col])
		else:
			model_score = pd.Series(list(model.best_score_['valid'].values()),index=[col])
	elif type(model) in [Lasso,ElasticNet,LassoCV,LinearRegression,LassoLarsIC,HuberRegressor,
						 ExtraTreesClassifier,ExtraTreesRegressor]:
		if isinstance(y_train,pd.DataFrame):
			model_score = pd.DataFrame([model.score(x_train,y_train)],index=y_train.columns,columns=[col])
		else:
			 model_score = pd.Series([model.score(x_train,y_train)],index=[col])
	else:
		print ('model not covered: %s'%(type(model)))
		raise Exception
	return model_score


def pred_fit_lgbm_cla_kf(y_train,x_train,x_test,param=None,fold_num=2,
						 verbose=True,track_feature_importance=False,return_misc=False,
						 return_score=False,plot_model=False,weight_type='abs_ret',
						 stratified=True,return_model=False,std_norm=False,shuffle=False,tsp=False,
						 filter_cut=None,trunc_pct=None):
	res_ctn = {}
	score_list = []
	model_list,fi_dict = {},{}
	misc_dict = {}
	if param is None:
		param = {'alpha': 0.1,
				 'booster': 'gbtree',
				 'colsample_bytree': 0.8,
				 'max_depth': 10,
				 'num_leaves': 200, 
				 'subsample': 0.4,
				 'learning_rate':0.0001,
				 'lr_decay':0.999,
				 'min_ratio':0.5,
				 'metric': 'auc',
				 'n_estimators':1000,
				 'n_jobs':-1,
				 'tree_method':'gpu_hist',
				 'gpu_id':0}
	if 'learning_rate' in param:
		lr_decay = 0.999 if 'lr_decay' not in param else param['lr_decay']
		min_ratio = 0.5 if 'min_ratio' not in param else param['min_ratio']
		lrdp = partial(learning_rate_decay_power,base_learning_rate=param['learning_rate'],lr_decay=lr_decay,min_ratio=min_ratio)
		#lrdp = partial(learning_rate_decay_power,base_learning_rate=param['learning_rate'],lr_decay=0.999,min_ratio=0.5)
		param = {i:param[i] for i in param if i not in ['lr_decay','min_ratio']}
	# k fold prediction
	set_seed()
	splits = fold_split_helper(x_train,y_train,fold_num,shuffle=shuffle,tsp=tsp)
	y_preds_k = np.zeros(x_test.shape[0])
	pred_res_list = []
	for fold_n, (train_index, valid_index) in enumerate(splits):
		print('Fold:',fold_n+1)
		x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
		y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
		model = lgb.LGBMClassifier(**param)
		if std_norm:
			y_train_k_std = y_train_k.std()
			if not isinstance(y_train_k_std,np.float):
				y_train_k_std = y_train_k_std.values
			y_train_k = y_train_k/y_train_k_std
			y_valid_k = y_valid_k/y_train_k_std
		if 'eval_metric' in param:
			eval_metric = param['eval_metric']
		elif 'metric' in param:
			eval_metric = param['metric']
		else:
			eval_metric = 'auc'          
		fit_params={"early_stopping_rounds":20, 
					"eval_metric" : eval_metric, 
					"eval_set" : [(x_valid_k,y_valid_k)],
					'eval_names': ['valid'],
					'callbacks': [lgb.reset_parameter(learning_rate=lrdp)],
					'verbose': 500,
					'categorical_feature': 'auto'}
		y_train_label_k = y_train_k.copy()
		y_train_label_k[y_train_k.iloc[:,0]>0] = 1
		y_train_label_k[y_train_k.iloc[:,0]<=0] = 0
		y_valid_label_k = y_valid_k.copy()
		y_valid_label_k[y_valid_k.iloc[:,0]>0] = 1
		y_valid_label_k[y_valid_k.iloc[:,0]<=0] = 0		
		fit_params['eval_set'] = [(x_valid_k,y_valid_label_k)]			
		if weight_type is None:
			model.fit(x_train_k, y_train_label_k,**fit_params)
		else:
			y_train_weight_k = get_sample_weight(y_train_k,weight_type)
			y_train_weight_k[y_train_weight_k>2] = 2
			if trunc_pct is not None:
				y_train_weight_k = get_sample_weight(y_train_k,weight_type,filter_cut,trunc_pct)
			fit_params['sample_weight'] = y_train_weight_k
			if isinstance(y_train_label_k,pd.Series):
				model.fit(x_train_k,y_train_label_k,**fit_params)
			else:
				model.fit(x_train_k,y_train_label_k.iloc[:,0],**fit_params)
		pred_res_itr = pred_template(x_test,model,pred='classification')
		y_preds_k += pred_res_itr / fold_num
		pred_res_list.append(pred_res_itr)
		if plot_model:
			lgb.plot_metric(model)
			plt.show()
		if track_feature_importance:
			fi_dict[fold_n] = collect_feature_importance_helper(model,x_train_k)
			#fi_dict[fold_n] = collect_feature_importance_helper(model,x_train)			
		if return_score:
			if weight_type is None:
				score_list.append(collect_model_score_helper(model,x_train_k,y_train_k))
			else: 
				score_list.append(collect_model_score_helper(model,x_train_k,y_train_label_k))
		"""        
		if return_misc:
			misc_dict[fold_n] = pd.DataFrame([model.evals_result_['validation_0'][eval_metric],
											  model.evals_result_['validation_1'][eval_metric]],index=['train','validaiton']).T
		"""
		if return_model:
			model_list[fold_n] = model
		del x_train_k, x_valid_k, y_train_k, y_valid_k
		gc.collect()
	res_ctn['prediction'] = y_preds_k
	pred_res_df = pd.concat(pred_res_list,axis=1)
	if track_feature_importance:
		res_ctn['feature_importance'] = fi_dict
	if return_misc:
		res_ctn['misc'] = pred_res_df#misc_dict
	if return_score:
		res_ctn['score'] = pd.DataFrame(pd.concat(score_list,axis=1).fillna(0).mean(axis=1) ,columns = [y_preds_k.index[0]])
	if return_model:
		res_ctn['model'] = model_list
	return res_ctn





"""
###############################
#### use case ###

###############################
### read data
fac_path_itr = '/data/user/020529/share/data/commodity/Fac_AL.h5'
ret_path_itr = '/data/user/020529/share/data/commodity/Ret_AL.h5'

fac = pd.read_hdf(fac_path_itr)
ret = pd.read_hdf(ret_path_itr)
print(fac.shape,ret.shape)
sdate_train = '20190101'
edate_train = '20221231'
sdate_test = '20230101'

x = fac.copy()
y = ret[[20]].copy()
x_train = x.loc[sdate_train:edate_train]
x_test = x.loc[sdate_test:]

y_train = y.loc[sdate_train:edate_train]
y_test = y.loc[sdate_test:]
print('prep fitting data')

###############################
### train model
track_feature_importance = True
return_score = True
verbose = True
fold_num = 5
return_model = True
return_misc = False
plot_model = True

param = {'reg_alpha': 0.01,
         'reg_lambda':0.0001,
         'colsample_bytree':0.2,
         'subsample': 0.4,
         'max_depth':8,
         'num_leaves': 256,#200, 
         'learning_rate':0.01,#0.1,#0.001,
         'lr_decay':0.9995,#0.999
         'min_ratio':0.001,
         'metric': 'auc',
         'n_estimators':1000,# for test purpose#2000*4,#2000*2,#2000*5,
         'n_jobs':24,
         'random_state':2018}

fit_pred_func = partial(pred_fit_lgbm_cla_kf,param=param,fold_num=fold_num,
                        weight_type='abs_ret',
                        stratified=True,
                        verbose=verbose,track_feature_importance=track_feature_importance,
                        return_score=return_score,return_model=return_model,
                        return_misc=return_misc,
                        plot_model=plot_model,
                        shuffle=True,filter_cut=None,trunc_pct=None)    

########################################################################

x = fac.copy()
y = ret.copy()

res_dict_model = fit_pred_func(y_train,x_train,x_test)




"""
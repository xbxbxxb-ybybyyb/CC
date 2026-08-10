# lgbm_reg
def pred_fit_lgbm_reg_kf(y_train,x_train,x_test,param=None,fold_num=2,
						 verbose=True,track_feature_importance=False,return_misc=False,
						 return_score=False,plot_model=False,return_model=False,
						 std_norm=False,std_add_back=False,early_stopping_rounds=20,
						 shuffle=False,tsp=False):
	set_seed()
	res_ctn = {}
	score_list = []
	model_list,fi_dict = {},{}
	misc_dict = {}
	if param is None:
		param = {"eval_metric" : 'rmse', 
				'n_jobs':-1,
				'num_iterations':2000,
				'random_state':2018,
				'max_depth':-1,
				'silent':False,
				'metric':None,
				'colsample_bytree': 0.6,
				'min_child_samples': 200,
				'min_child_weight': 0.01, 
				'num_leaves': 30, 
				'reg_alpha': 5,
				'reg_lambda': 0, 
				'subsample': 0.5}
	if 'learning_rate' in param:
		lr_decay = 0.999 if 'lr_decay' not in param else param['lr_decay']
		min_ratio = 0.5 if 'min_ratio' not in param else param['min_ratio']
		lrdp = partial(learning_rate_decay_power,base_learning_rate=param['learning_rate'],lr_decay=lr_decay,min_ratio=min_ratio)
		#lrdp = partial(learning_rate_decay_power,base_learning_rate=param['learning_rate'],lr_decay=0.999,min_ratio=0.5)
		param = {i:param[i] for i in param if i not in ['lr_decay','min_ratio']}
	# k fold prediction
	"""
	if shuffle:
		folds = KFold(n_splits=fold_num,shuffle=shuffle,random_state=2018)
		splits = folds.split(x_train, y_train)
	else:
		if tsp:
			folds = TimeSeriesSplit(n_splits=fold_num)
			splits = folds.split(x_train, y_train)
		else:
			folds = KFold(n_splits=fold_num)
			splits = folds.split(x_train, y_train,x_train.index.date)
	"""
	splits = fold_split_helper(x_train,y_train,fold_num,shuffle=shuffle,tsp=tsp)    
	y_preds_k = np.zeros(x_test.shape[0])
	pred_res_list = []
	for fold_n, (train_index, valid_index) in enumerate(splits):
		print('Fold:',fold_n+1)
		x_train_k, x_valid_k = x_train.iloc[train_index], x_train.iloc[valid_index]
		y_train_k, y_valid_k = y_train.iloc[train_index], y_train.iloc[valid_index]
		if std_norm:
			y_train_k_std = y_train_k.std()
			if not isinstance(y_train_k_std,np.float):
				y_train_k_std = y_train_k_std.values
			y_train_k = y_train_k/y_train_k_std
			y_valid_k = y_valid_k/y_train_k_std

		model = lgb.LGBMRegressor(**param)
		if 'eval_metric' in param:
			eval_metric = param['eval_metric']
		elif 'metric' in param:
			eval_metric = param['metric']
		else:
			eval_metric = 'rmse'                  
		fit_params={"early_stopping_rounds":early_stopping_rounds, 
					"eval_metric" : eval_metric, 
					"eval_set" : [(x_valid_k,y_valid_k)],
					'eval_names': ['valid'],
					'callbacks': [lgb.reset_parameter(learning_rate=lrdp)],
					'verbose': 500,
					'categorical_feature': 'auto'}
		model.fit(x_train_k.values,y_train_k.values,**fit_params)
		pred_res_itr = pred_template(x_test,model,pred='regression')
		std_add_back = std_norm
		if std_add_back:
			pred_res_itr = pred_res_itr * y_train_k_std
		y_preds_k += pred_res_itr / fold_num
		pred_res_list.append(pred_res_itr)        
		if plot_model:
			lgb.plot_metric(model)
			plt.show()
		if track_feature_importance:
			fi_dict[fold_n] = collect_feature_importance_helper(model,x_train_k)
		if return_score:
			score_list.append(collect_model_score_helper(model,x_train_k,y_train_k))
		if return_misc:
			pred_res_list.append(pred_res_itr)        
		if return_model:
			model_list[fold_n] = model          
		del x_train_k, x_valid_k, y_train_k, y_valid_k
		gc.collect()
	res_ctn['prediction'] = y_preds_k
	if track_feature_importance:
		res_ctn['feature_importance'] = fi_dict
	if return_misc:
		res_ctn['misc'] = pd.DataFrame(pd.concat(pred_res_list,axis=1))
	if return_score:
		res_ctn['score'] = pd.DataFrame(pd.concat(score_list,axis=1).fillna(0).mean(axis=1) ,columns = [y_preds_k.index[0]])
	if return_model:
		res_ctn['model'] = model_list
	return res_ctn
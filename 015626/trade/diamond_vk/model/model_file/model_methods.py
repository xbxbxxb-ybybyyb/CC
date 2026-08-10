# lgbm rank
predict_score = lgbm.predict(nonlinear_fcts, raw_score=True)
predict_score = pd.Series(predict_score, index=nonlinear_fcts.index)

# lgbm bin
predict_score = lgbm.predict_proba(nonlinear_fcts, raw_score=False)
predict_score = pd.Series(predict_score[:, 1], index=nonlinear_fcts.index)

# et bin
predict_score = clf.predict_proba(nonlinear_fcts.fillna(0))
predict_score = pd.Series(predict_score[:, 1], index=nonlinear_fcts.index)

# lr bin
lr_score = lr_model.predict_proba(x2.fillna(0))
lr_score = pd.Series(lr_score[:, 1], index=x2.index)

# lasso 
def sklearn_predictor(x, res):
    assert np.all([isinstance(item, pd.DataFrame) for item in [x]])
    assert len(res['valid_cols']) != 0
    x_ = fill_infinite(x[res['valid_cols']]).values
    return pd.Series(res['model'].predict(x_).ravel(), index=x.index)
lasso_score = sklearn_predictor(x2, lasso_model)
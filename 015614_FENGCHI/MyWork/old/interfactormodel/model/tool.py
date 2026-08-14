from sklearn.linear_model import Ridge
import numpy as np
import bottleneck


def get_metric(score, model_days, code_num, pool, ret):

    fit = np.full(model_days * code_num, np.nan)
    fit[pool.flatten()] = score
    fit = fit.reshape(model_days, code_num)
    fit = (bottleneck.nanrankdata(fit, axis=1).T / pool.sum(axis=1)).T
    ret_top = ret.copy()
    ret_top[fit <= 0.9] = np.nan
    weight = np.logspace(model_days, 0, model_days, base=0.99)
    weight /= weight.sum()
    metric = (np.nanmean(ret_top, axis=1) - np.nanmean(ret, axis=1)).dot(weight)
    return - metric

def get_score(alpha, feature, label):

    reg = Ridge(alpha=alpha).fit(feature, label)
    score = reg.predict(feature)
    return score

def bisection_search(feature, label, model_days, code_num, pool, ret, start=100., lr=100, tol=1e-10, max_iter=100):

    x0 = start
    score = get_score(x0, feature, label)
    metric = get_metric(score, model_days, code_num, pool, ret)
    print(x0, metric)
    y0 = metric

    x1 = start + lr
    score = get_score(x1, feature, label)
    metric = get_metric(score, model_days, code_num, pool, ret)
    print(x1, metric)
    y1 = metric

    while y1 <= y0:

        lr *= 2
        x2 = start + lr
        score = get_score(x2, feature, label)
        metric = get_metric(score, model_days, code_num, pool, ret)
        print(x2, metric)
        y2 = metric
        if y2 > y1:
            x1 = x2
            break
        x0 = x1
        x1 = x2
        y0 = y1
        y1 = y2

    i = 0
    while i < max_iter:

        i += 1
        x2 = (x0 + x1) / 2
        score = get_score(x2, feature, label)
        metric = get_metric(score, model_days, code_num, pool, ret)
        print(i, x2, metric)
        y2 = metric
        if abs(y2 / y0 - 1) < tol:
            return x0
        elif y2 > y0:
            x1 = x2
        else:
            x3 = x2 + (x1 - x2) / 100
            score = get_score(x3, feature, label)
            metric = get_metric(score, model_days, code_num, pool, ret)
            y3 = metric
            if y3 <= y2:
                x0 = x3
                y0 = y3
            else:
                x1 = x2








def model_predict():



    def gradient_descent(Xa, Xb, lam, error=1e-10, max_iter=100):

        m = Xa.shape[0]
        n = Xb.shape[0]
        alpha = np.ones(m) / m
        beta = np.ones(n) / n
        _loss = dual_loss_func(Xa, Xb, alpha, beta, lam, m)
        lr = 1.
        iter_num = 0
        while True:
            loss_ = _loss
            _lr = 0.

            ga, gb = partial_dual_loss_func(Xa, Xb, alpha, beta, lam, m)
            while True:
                _alpha = alpha - ga * lr
                _beta = beta - gb * lr
                _alpha, _beta = linear_projection(_alpha, _beta)
                loss = dual_loss_func(Xa, Xb, _alpha, _beta, lam, m)
                if loss < _loss:
                    _loss = loss
                    _lr = lr
                    lr *= 2
                    # print('lr=', lr)
                else:
                    break
            while True:
                if lr - _lr < error:
                    break
                lr_ = (_lr + lr) / 2.
                _alpha = alpha - ga * lr_
                _beta = beta - gb * lr_
                _alpha, _beta = linear_projection(_alpha, _beta)
                loss = dual_loss_func(Xa, Xb, _alpha, _beta, lam, m)
                if loss < _loss:
                    if _loss - loss < error * 1000:
                        _loss = loss
                        break
                    _loss = loss
                    _lr = lr_
                else:
                    lr = lr_
                # print('lr_=', lr_)
            iter_num += 1
            print(loss_ - _loss)
            if (loss_ - _loss < error) | (iter_num > max_iter):
                return _alpha, _beta

            alpha = _alpha
            beta = _beta
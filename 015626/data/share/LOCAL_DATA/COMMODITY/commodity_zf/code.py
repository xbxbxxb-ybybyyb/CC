## backtest:
retlist = []
poslist = []

for ticker in tickerlist:
    if ticker in blacklist:
        continue
    prod_data = data.xs(ticker,level=1)
    ## 1. parameters
    lw = 32
    sw = 10
    atrdays = 14
    atr_in_thd = 0.01
    atr_out_thd = 0.03
    # evthd = 0.024
    # xvthd = 0.023
    dailyretthd = 0.03
    
    ## 2. variable prepare
    clsorg = prod_data['close']
    ecls = prod_data['close']-prod_data['gap']
    highprice = prod_data['high']
    lowprice = prod_data['low']
    preclose = prod_data['pre_close']
    rt = prod_data['close']/prod_data['pre_close']-1
    
    atr = pd.concat([abs(highprice - lowprice),abs(highprice-preclose),abs(lowprice-preclose)],axis=1).max(axis=1)
    atr_ratio = atr.rolling(atrdays,min_periods = 5).mean()/clsorg
    #atr_ratio = atr / clos
    atr_ratio_rk = ts_rank(atr_ratio,120)
    curvol = rt.rolling(atrdays,min_periods = 5).std()
    
    mashort = ecls.rolling(5).mean()
    mamidshort = ecls.rolling(10).mean()
    mamid = ecls.rolling(20).mean()
    mamidlong = ecls.rolling(30).mean()
    malong = ecls.rolling(60).mean()
    
    ## 3. signal construct
    # 1. turtle signal
    eH = ecls.rolling(lw,min_periods = int(lw/2)).max().shift(1)
    eL = ecls.rolling(lw, min_periods = int(lw/2)).min().shift(1)
    xH = ecls.rolling(sw,min_periods = int(sw/2)).max().shift(1)
    xL = ecls.rolling(sw,min_periods = int(sw/2)).min().shift(1)
    emid = (eH+eL)/2
    
    elong1 = (ecls > eH).astype(int)
    elong2 = (ecls > emid).astype(int)
    #turtlelongin = signal_trans(elong1,elong2)
    turtlelongin = elong1
    
    eshort1 = (ecls < eL).astype(int)
    eshort2 = (ecls < emid).astype(int)
    #turtleshortin = signal_trans(eshort1,eshort2)
    turtleshortin = eshort1
    
    turtlelongout = (ecls < xL).astype(int)
    turtleshortout = (ecls > xH).astype(int)
    # 2. masignal
    malongin = ((ecls > mashort)&(mashort > mamidshort)&(mamidshort > mamid) &(mamid > mamidlong)&(mamidlong > malong)).astype(int)
    mashortin = ((ecls < mashort)&(mashort < mamidshort)&(mamidshort < mamid) &(mamid < mamidlong)&(mamidlong < malong)).astype(int)
    
    maratio = (ecls - malong) / clsorg
    # 3. atrsignal
    #atrin = ((atr_ratio > atr_in_thd)&(atr_ratio < atr_out_thd)).astype(int)
    atrin = ((atr_ratio_rk < 0.3)&(atr_ratio_rk >-0.8)).astype(int)
    atrout = (atr_ratio_rk > 0.8).astype(int)
    
    #atrout = (atr_ratio > atr_out_thd).astype(int)
    # 4. dailyret
    dailyretlongout = (rt < -0.03)
    dailyretshortout = (rt > 0.03)
    
    longin =  malongin & atrin
    shortin =  mashortin & atrin
    longout = turtlelongout | dailyretlongout | atrout
    shortout = turtleshortout | dailyretshortout | atrout
   
    # longin = turtlelongin & atrin
    # shortin = turtleshortin & atrin
    # longout = turtlelongout | dailyretlongout
    # shortout = turtleshortout | dailyretshortout
    
    # signal to position
    pos = pd.Series([0]*len(longin),index = longin.index)
    trade = pd.Series([0]*len(longin),index = longin.index)
    tradetime = 0
    for i in range(1,len(prod_data)):
        if pos.iloc[i-1] == 0:
            if longin.iloc[i]:
                pos.iloc[i] = 1
                tradetime = tradetime + 1
                trade.iloc[i] = tradetime
            elif shortin.iloc[i]:
                pos.iloc[i] = -1
                tradetime = tradetime + 1
                trade.iloc[i] = tradetime
            else:
                pos.iloc[i] = 0
        elif pos.iloc[i-1] == 1:
            if longout.iloc[i]:
                pos.iloc[i] = 0
            else:
                pos.iloc[i] = 1
                trade.iloc[i] = tradetime
        elif pos.iloc[i-1] == -1:
            if shortout.iloc[i]:
                pos.iloc[i] = 0
            else:
                pos.iloc[i] = -1
                trade.iloc[i] = tradetime
        else:
            raise ValueError("something wrong with position!")
        pos.name = ticker
    #dailyret = ((ecls.shift(-1)-ecls)*pos)/clsorg
    dailyret = ((ecls - ecls.shift(1))*pos.shift(1))/clsorg
    dailyret.name = ticker
    retlist.append(dailyret)
    poslist.append(pos)
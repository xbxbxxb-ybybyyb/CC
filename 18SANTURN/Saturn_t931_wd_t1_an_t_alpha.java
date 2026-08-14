/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Comparator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_an_t_alpha
extends BaseFactor {
    public Saturn_t931_wd_t1_an_t_alpha(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_an_t_alpha"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List marketOrderList = this.marketDataManager.getLxjjTradeSellMap().values().stream().sorted(Comparator.comparing(MarketOrder::getPrice).thenComparing(MarketOrder::getNo)).limit(100L).collect(Collectors.toList());
        LinkedList<Double> x = new LinkedList<Double>();
        LinkedList<Double> y = new LinkedList<Double>();
        for (MarketOrder marketOrder : marketOrderList) {
            x.add(Double.valueOf(marketOrder.getFillList().size()));
            y.add(Double.valueOf(TimeUtil.calTimeDelta(93000000L, (long)marketOrder.getFirstFillMdTime())));
        }
        double factorValue = MathUtil.calculateStd(x) == 0.0 || MathUtil.calculateStd(y) == 0.0 || x.size() < 3 ? Double.NaN : MathUtil.regressionRes(y, x)[0][0];
        this.updateValue(0, Double.isNaN(factorValue /= 10000.0) ? 2.0 : factorValue);
    }
}


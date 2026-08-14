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
import java.util.ArrayList;
import java.util.Map;

public class Saturn_t931_wd_t1_rise_money_med
extends BaseFactor {
    public Saturn_t931_wd_t1_rise_money_med(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_rise_money_med"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Double> lst = new ArrayList<Double>();
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (marketOrder.getMaxPrice() == marketOrder.getMinPrice()) continue;
            lst.add(marketOrder.getAmt());
        }
        double factorValue = Math.log(MathUtil.calcMedian(lst.stream().mapToDouble(e -> e).toArray()));
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 10.8 : factorValue);
    }
}


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.Ordering
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.Ordering;
import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Comparator;
import java.util.Map;

public class Saturn_t931_wd_t1_high_max_money
extends BaseFactor {
    public Saturn_t931_wd_t1_high_max_money(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_high_max_money"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Ordering orderOrdering = Ordering.from(Comparator.comparing(MarketOrder::getVwap).thenComparing(MarketOrder::getNo));
        double a = orderOrdering.leastOf(this.marketDataManager.getLxjjTradeBuyMap().values(), Math.min(100, this.marketDataManager.getLxjjTradeBuyMap().size())).stream().mapToDouble(MarketOrder::getAmt).max().orElse(Double.NaN);
        double value = Math.log(a);
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 13.0 : value);
    }
}


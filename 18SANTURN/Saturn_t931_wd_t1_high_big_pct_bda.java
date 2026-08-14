/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.Ordering
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.Ordering;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Comparator;
import java.util.Map;

public class Saturn_t931_wd_t1_high_big_pct_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_high_big_pct_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_high_big_pct_bda"};
    }

    @Override
    public void update(Fill fill) {
    }

    @Override
    public void calculate() {
        Ordering orderOrdering = Ordering.from(Comparator.comparing(MarketOrder::getVwap).thenComparing(MarketOrder::getNo));
        double a = orderOrdering.leastOf(this.marketDataManager.getLxjjTradeBuyMap().values(), Math.min(100, this.marketDataManager.getLxjjTradeBuyMap().size())).stream().filter(e -> e.getAmt() > 50000.0).mapToDouble(MarketOrder::getAmt).sum();
        double b = orderOrdering.leastOf(this.marketDataManager.getLxjjTradeSellMap().values(), Math.min(100, this.marketDataManager.getLxjjTradeSellMap().size())).stream().filter(e -> e.getAmt() > 50000.0).mapToDouble(MarketOrder::getAmt).sum();
        double value = 0.35;
        if (a + b != 0.0) {
            value = a / (a + b);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.35 : value);
    }
}


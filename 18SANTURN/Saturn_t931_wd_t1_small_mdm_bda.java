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
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_t1_small_mdm_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_small_mdm_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_small_mdm_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Ordering orderOrdering = Ordering.from(Comparator.comparing(MarketOrder::getQty));
        List s1 = orderOrdering.leastOf(this.marketDataManager.getLxjjTradeBuyMap().values(), Math.min(200, this.marketDataManager.getLxjjTradeBuyMap().size()));
        List s2 = orderOrdering.leastOf(this.marketDataManager.getLxjjTradeSellMap().values(), Math.min(200, this.marketDataManager.getLxjjTradeSellMap().size()));
        double a = s1.stream().mapToDouble(MarketOrder::getQty).max().orElse(Double.NaN) / s1.stream().mapToDouble(MarketOrder::getQty).average().orElse(Double.NaN);
        double b = s2.stream().mapToDouble(MarketOrder::getQty).max().orElse(Double.NaN) / s2.stream().mapToDouble(MarketOrder::getQty).average().orElse(Double.NaN);
        double value = 0.4;
        if (a + b != 0.0) {
            value = a / (a + b);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.4 : value);
    }
}


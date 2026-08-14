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
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_min100v_weight_t
extends BaseFactor {
    public Saturn_t931_wd_t1_min100v_weight_t(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_min100v_weight_t"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List marketOrderList = this.marketDataManager.getLxjjTradeBuyMap().values().stream().sorted(Comparator.comparing(MarketOrder::getPrice).thenComparing(MarketOrder::getNo)).limit(100L).collect(Collectors.toList());
        double value1 = 0.0;
        double value2 = 0.0;
        for (MarketOrder marketOrder : marketOrderList) {
            value1 += marketOrder.getFirstFillMdTime() * marketOrder.getQty();
            value2 += marketOrder.getQty().doubleValue();
        }
        double factorValue = value1 / value2;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 9.3015E7 : factorValue);
    }
}


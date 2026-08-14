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
import java.util.Map;

public class Saturn_t931_wd_t1_big_bid_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_big_bid_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_big_bid_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.9;
        Double median = MathUtil.calculateSortedMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getQty).sorted().toArray());
        double qty = this.marketDataManager.getLxjjTradeBuyMap().values().stream().filter(order -> order.getQty() > median).mapToDouble(MarketOrder::getQty).sum();
        if (qty > 0.0) {
            value = qty / this.marketDataManager.getLxjjTotalQty();
        }
        this.updateValue(0, value);
    }
}


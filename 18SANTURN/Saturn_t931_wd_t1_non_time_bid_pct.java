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
import java.util.Map;

public class Saturn_t931_wd_t1_non_time_bid_pct
extends BaseFactor {
    public Saturn_t931_wd_t1_non_time_bid_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_non_time_bid_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sum1 = this.marketDataManager.getLxjjTradeBuyMap().values().stream().filter(order -> order.getFillTimeDelta() == 0.0).mapToDouble(MarketOrder::getQty).sum();
        double value = this.marketDataManager.getLxjjTotalQty() == 0.0 ? 0.8 : sum1 / this.marketDataManager.getLxjjTotalQty();
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.8 : value);
    }
}


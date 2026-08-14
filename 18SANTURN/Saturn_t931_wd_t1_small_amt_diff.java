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

public class Saturn_t931_wd_t1_small_amt_diff
extends BaseFactor {
    public Saturn_t931_wd_t1_small_amt_diff(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_small_amt_diff"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.5;
        if (this.marketDataManager.getFillList().size() > 0) {
            double buyQty = this.marketDataManager.getLxjjTradeBuyMap().values().stream().filter(order -> order.getAmt() < 40000.0).mapToDouble(MarketOrder::getQty).sum();
            double sellQty = this.marketDataManager.getLxjjTradeSellMap().values().stream().filter(order -> order.getAmt() < 40000.0).mapToDouble(MarketOrder::getQty).sum();
            value = (buyQty - sellQty) / this.marketDataManager.getFreeFloatCapital();
        }
        this.updateValue(0, value);
    }
}


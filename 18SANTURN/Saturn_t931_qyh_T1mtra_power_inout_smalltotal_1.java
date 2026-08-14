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

public class Saturn_t931_qyh_T1mtra_power_inout_smalltotal_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_power_inout_smalltotal_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_power_inout_smalltotal_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double buySum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (!(marketOrder.getAmt() < 50000.0)) continue;
            buySum += marketOrder.getAmt().doubleValue();
        }
        double sellSum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeSellMap().values()) {
            if (!(marketOrder.getAmt() < 50000.0)) continue;
            sellSum += marketOrder.getAmt().doubleValue();
        }
        double factor = 1.0;
        if (sellSum > 0.001) {
            factor = buySum / sellSum;
        }
        this.updateValue(0, Double.isNaN(factor) ? 1.0 : factor);
    }
}


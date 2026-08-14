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

public class Saturn_t931_qyh_T1mtra_ratio_in_big_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_ratio_in_big_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_ratio_in_big_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double buySum = 0.0;
        double buyFilterSum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (marketOrder.getAmt() >= 200000.0) {
                buyFilterSum += marketOrder.getAmt().doubleValue();
            }
            buySum += marketOrder.getAmt().doubleValue();
        }
        double factor = 0.4;
        if (buySum > 0.001) {
            factor = buyFilterSum / buySum;
        }
        this.updateValue(0, Double.isNaN(factor) ? 0.4 : factor);
    }
}


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashSet;
import java.util.Map;

public class Saturn_t931_qyh_T1mtra_ratio_in_small_out_big_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_ratio_in_small_out_big_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_ratio_in_small_out_big_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        HashSet<Long> noSet = new HashSet<Long>();
        double buySum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            buySum += marketOrder.getAmt().doubleValue();
            if (!(marketOrder.getAmt() < 50000.0)) continue;
            for (Fill fill : marketOrder.getFillList()) {
                noSet.add(fill.getTradeIndex());
            }
        }
        double totalSum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeSellMap().values()) {
            if (!(marketOrder.getAmt() >= 200000.0)) continue;
            for (Fill fill : marketOrder.getFillList()) {
                if (!noSet.contains(fill.getTradeIndex())) continue;
                totalSum += fill.getAmt().doubleValue();
            }
        }
        double factor = 0.3;
        if (buySum > 0.001) {
            factor = totalSum / buySum;
        }
        this.updateValue(0, Double.isNaN(factor) ? 0.3 : factor);
    }
}


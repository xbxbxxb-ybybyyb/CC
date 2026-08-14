/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_wd_jtcs_small_bid_amt_d_sum
extends BaseFactor {
    public Saturn_t930_wd_jtcs_small_bid_amt_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_small_bid_amt_d_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<String, Map<Long, Double>> buySum = this.marketDataManager.getBuyOrderJhjjAmtSum();
        double currSum = 0.0;
        double totalSum = 0.0;
        for (Map.Entry<String, Map<Long, Double>> entry : buySum.entrySet()) {
            double totalAmt = 0.0;
            for (Double val : entry.getValue().values()) {
                if (!(val <= 100000.0)) continue;
                totalAmt += val.doubleValue();
            }
            totalSum += totalAmt;
            if (!entry.getKey().equals(this.marketDataManager.getSymbol())) continue;
            currSum = totalAmt;
        }
        this.updateValue(0, totalSum != 0.0 ? currSum / totalSum : 0.02);
    }
}


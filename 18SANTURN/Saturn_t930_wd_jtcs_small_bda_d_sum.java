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
import java.util.HashMap;
import java.util.Map;

public class Saturn_t930_wd_jtcs_small_bda_d_sum
extends BaseFactor {
    public Saturn_t930_wd_jtcs_small_bda_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_small_bda_d_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<String, Map<Long, Double>> sellSum = this.marketDataManager.getSellOrderJhjjAmtSum();
        Map<String, Map<Long, Double>> buySum = this.marketDataManager.getBuyOrderJhjjAmtSum();
        double bdsSum = 0.0;
        double currBds = 0.0;
        HashMap<String, Double> buyAmtSmallMap = new HashMap<String, Double>(sellSum.size());
        for (Map.Entry<String, Map<Long, Double>> entry : buySum.entrySet()) {
            double totalBuyAmt = 0.0;
            for (Double val : entry.getValue().values()) {
                if (!(val <= 100000.0)) continue;
                totalBuyAmt += val.doubleValue();
            }
            buyAmtSmallMap.put(entry.getKey(), totalBuyAmt);
        }
        for (Map.Entry<String, Map<Long, Double>> entry : sellSum.entrySet()) {
            double totalSellAmt = 0.0;
            for (Double val : entry.getValue().values()) {
                if (!(val <= 100000.0)) continue;
                totalSellAmt += val.doubleValue();
            }
            double bds = totalSellAmt != 0.0 ? (Double)buyAmtSmallMap.get(entry.getKey()) / totalSellAmt : 0.0;
            bdsSum += bds;
            if (!entry.getKey().equals(this.marketDataManager.getSymbol())) continue;
            currBds = bds;
        }
        this.updateValue(0, bdsSum != 0.0 ? currBds / bdsSum : 0.01);
    }
}


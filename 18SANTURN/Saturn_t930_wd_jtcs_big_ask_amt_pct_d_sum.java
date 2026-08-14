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

public class Saturn_t930_wd_jtcs_big_ask_amt_pct_d_sum
extends BaseFactor {
    public Saturn_t930_wd_jtcs_big_ask_amt_pct_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jtcs_big_ask_amt_pct_d_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<String, Double> amtSum = this.marketDataManager.getTotalJhjjAmtSum();
        Map<String, Map<Long, Double>> sellSum = this.marketDataManager.getSellOrderJhjjAmtSum();
        double pct = 0.0;
        double pctSum = 0.0;
        for (Map.Entry<String, Double> entry : amtSum.entrySet()) {
            double totalAmt = 0.0;
            for (Double val : sellSum.get(entry.getKey()).values()) {
                if (!(val > 200000.0)) continue;
                totalAmt += val.doubleValue();
            }
            pctSum += totalAmt / entry.getValue();
            if (!entry.getKey().equals(this.marketDataManager.getSymbol())) continue;
            pct = totalAmt / entry.getValue();
        }
        this.updateValue(0, pctSum != 0.0 ? pct / pctSum : 0.03);
    }
}


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_t1_rise_pct_compare
extends BaseFactor {
    public Saturn_t931_wd_t1_rise_pct_compare(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_rise_pct_compare"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        double value = 0.25;
        if (fillList.size() > 1) {
            Double preTran1 = null;
            Double preTran2 = fillList.get(0).getPrice();
            double sum1 = 0.0;
            double sum2 = 0.0;
            for (int i = 1; i < fillList.size(); ++i) {
                Double price = fillList.get(i).getPrice();
                if (price > fillList.get(i - 1).getPrice()) {
                    sum1 += preTran1 == null ? 0.0 : Math.abs(price - preTran1);
                    preTran1 = price;
                    continue;
                }
                sum2 += Math.abs(price - preTran2);
                preTran2 = price;
            }
            if (sum1 + sum2 != 0.0) {
                value = sum1 / (sum1 + sum2);
            }
        }
        this.updateValue(0, value);
    }
}


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

public class Saturn_t931_wd_t1_low_price_vol_rate
extends BaseFactor {
    public Saturn_t931_wd_t1_low_price_vol_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_low_price_vol_rate"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double tradeQtySum = this.marketDataManager.getLxjjTotalQty();
        if (tradeQtySum == 0.0) {
            this.updateValue(0, 0.0);
        } else {
            List<Fill> fillList = this.marketDataManager.getLxjjFillList();
            double minFillPrice = 1.01 * fillList.stream().mapToDouble(Fill::getPrice).min().orElse(0.0);
            double qtySum = fillList.stream().filter(fill -> fill.getPrice() >= minFillPrice).mapToDouble(Fill::getQty).sum();
            this.updateValue(0, qtySum / tradeQtySum);
        }
    }
}


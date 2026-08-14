/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t940_wd_t10_max_min_pct
extends BaseFactor {
    private Double maxTradePrice = null;
    private Double minTradePrice = null;

    public Saturn_t940_wd_t10_max_min_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_max_min_pct"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        double price = fill.getPrice();
        long time = fill.getMdTime();
        if (time < 94000000L) {
            if (this.maxTradePrice == null) {
                this.maxTradePrice = price;
            } else if (price > this.maxTradePrice) {
                this.maxTradePrice = price;
            }
            if (this.minTradePrice == null) {
                this.minTradePrice = price;
            } else if (price < this.minTradePrice) {
                this.minTradePrice = price;
            }
        }
    }

    @Override
    public void calculate() {
        double value = 1.05;
        if (this.maxTradePrice != null && this.minTradePrice != null) {
            value = this.maxTradePrice / this.minTradePrice;
        }
        this.updateValue(0, value);
    }
}


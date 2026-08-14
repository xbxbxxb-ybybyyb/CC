/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t931_wd_t1_max_min_pct
extends BaseFactor {
    private Double maxTradePrice = null;
    private Double minTradePrice = null;

    public Saturn_t931_wd_t1_max_min_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_min_pct"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        this.maxTradePrice = null == this.maxTradePrice ? fill.getPrice() : Double.max(this.maxTradePrice, fill.getPrice());
        this.minTradePrice = null == this.minTradePrice ? fill.getPrice() : Double.min(this.minTradePrice, fill.getPrice());
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


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t931_wd_t1_max_s_qty_rate
extends BaseFactor {
    private final Map<Long, Double> timeToQty = new HashMap<Long, Double>();

    public Saturn_t931_wd_t1_max_s_qty_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_s_qty_rate"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        if (fill.getSide() == Trade.Side.Offer) {
            this.timeToQty.merge(fill.getMdTime() / 1000L, fill.getQty(), Double::sum);
        }
    }

    @Override
    public void calculate() {
        if (this.marketDataManager.getLxjjTotalQty() == 0.0) {
            this.updateValue(0, 0.1);
        } else {
            double maxQty = this.timeToQty.values().stream().mapToDouble(Double::doubleValue).max().orElse(Double.NaN);
            double factorValue = maxQty / this.marketDataManager.getLxjjTotalQty();
            this.updateValue(0, Double.isNaN(factorValue) ? 0.1 : factorValue);
        }
    }
}


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

public class Saturn_t931_wd_t1_qty_ms_density
extends BaseFactor {
    private final HashMap<Integer, Double> secondQtyMap;
    private double totalQty = 0.0;

    public Saturn_t931_wd_t1_qty_ms_density(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_qty_ms_density"};
        this.updateMode = 1;
        this.secondQtyMap = new HashMap();
    }

    @Override
    public void update(Fill fill) {
        if (fill.getSide() == Trade.Side.Bid) {
            this.secondQtyMap.merge((int)(fill.getMdTime() % 1000L / 100L), fill.getQty(), Double::sum);
            this.totalQty += fill.getQty().doubleValue();
        }
    }

    @Override
    public void calculate() {
        double value = this.secondQtyMap.isEmpty() ? 0.2 : this.secondQtyMap.values().stream().mapToDouble(qty -> qty / this.totalQty).max().orElse(0.2);
        this.updateValue(0, value);
    }
}


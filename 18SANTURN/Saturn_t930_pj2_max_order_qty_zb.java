/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.QtyPrice
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.QtyPrice;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_pj2_max_order_qty_zb
extends BaseFactor {
    public Saturn_t930_pj2_max_order_qty_zb(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_max_order_qty_zb"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double maxBuyQty = this.marketDataManager.getQuoteList().stream().mapToDouble(e -> ((QtyPrice)e.getBids().get(0)).getQuantity() + ((QtyPrice)e.getBids().get(1)).getQuantity()).max().orElse(0.0);
        double value = maxBuyQty / this.marketDataManager.getFreeFloatCapital();
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.0 : value);
    }
}


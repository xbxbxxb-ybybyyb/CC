/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Quote
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.QtyPrice
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Quote;
import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.QtyPrice;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_pj2_jhjj_volume_zb
extends BaseFactor {
    public Saturn_t930_pj2_jhjj_volume_zb(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_jhjj_volume_zb"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double totalVol;
        Quote lastQuote = this.marketDataManager.getLastQuote();
        if (null == lastQuote) {
            totalVol = 0.0;
        } else {
            totalVol = lastQuote.getTotalVolume();
            if (totalVol == 0.0) {
                totalVol = ((QtyPrice)lastQuote.getBids().get(0)).getQuantity();
            }
        }
        double value = totalVol / this.marketDataManager.getFreeFloatCapital();
        this.updateValue(0, Double.isInfinite(value) || Double.isNaN(value) ? 0.0 : value);
    }
}


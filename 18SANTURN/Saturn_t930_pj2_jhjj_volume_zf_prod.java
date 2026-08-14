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

public class Saturn_t930_pj2_jhjj_volume_zf_prod
extends BaseFactor {
    public Saturn_t930_pj2_jhjj_volume_zf_prod(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_jhjj_volume_zf_prod"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        Quote quote = this.marketDataManager.getLastQuote();
        if (quote != null) {
            double price;
            double callAuctionVolume = quote.getTotalVolume();
            if (callAuctionVolume == 0.0) {
                callAuctionVolume = 1.0;
            }
            if ((price = quote.getLastPx().doubleValue()) == 0.0) {
                price = ((QtyPrice)quote.getBids().get(0)).getPrice();
            }
            value = (price / this.marketDataManager.getPreClose() - 1.0) * (callAuctionVolume / this.marketDataManager.getFreeFloatCapital());
        }
        if (this.marketDataManager.getSymbol().startsWith("3")) {
            value /= 2.0;
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.0 : value);
    }
}


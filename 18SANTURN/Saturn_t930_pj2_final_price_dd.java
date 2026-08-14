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
import java.util.List;
import java.util.Map;

public class Saturn_t930_pj2_final_price_dd
extends BaseFactor {
    public Saturn_t930_pj2_final_price_dd(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_final_price_dd"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        List<Quote> quoteList = this.marketDataManager.getQuoteList();
        if (quoteList.size() > 0) {
            double maxPrice = quoteList.stream().mapToDouble(e -> ((QtyPrice)e.getBids().get(0)).getPrice()).max().orElse(0.0);
            double lastBid0 = ((QtyPrice)this.marketDataManager.getLastQuote().getBids().get(0)).getPrice();
            value = (maxPrice - lastBid0) / this.marketDataManager.getPreClose();
        }
        value = this.marketDataManager.isStartsWith3() ? value / 2.0 : value;
        this.updateValue(0, value);
    }
}


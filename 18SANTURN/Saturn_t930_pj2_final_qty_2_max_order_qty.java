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

public class Saturn_t930_pj2_final_qty_2_max_order_qty
extends BaseFactor {
    public Saturn_t930_pj2_final_qty_2_max_order_qty(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_final_qty_2_max_order_qty"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 1.0;
        Quote lastQuote = this.marketDataManager.getLastQuote();
        double totalVolume = null == lastQuote ? 0.0 : lastQuote.getTotalVolume();
        List<Quote> quoteList = this.marketDataManager.getQuoteList();
        if (totalVolume != 0.0 && !quoteList.isEmpty()) {
            double maxBuyQty = quoteList.stream().mapToDouble(e -> ((QtyPrice)e.getBids().get(0)).getQuantity() + ((QtyPrice)e.getBids().get(1)).getQuantity()).max().orElse(0.0);
            value = maxBuyQty / totalVolume;
        }
        this.updateValue(0, value);
    }
}


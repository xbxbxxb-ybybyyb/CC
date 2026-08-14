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
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.Date;
import java.util.List;
import java.util.Map;

public class Saturn_t930_pj2_jhjj_volume_ratio_925_920
extends BaseFactor {
    private final Date date920;

    public Saturn_t930_pj2_jhjj_volume_ratio_925_920(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_jhjj_volume_ratio_925_920"};
        this.date920 = TimeUtil.getDateTime(marketDataManager.getParams().getTradeDate(), LocalTime.of(9, 20));
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value;
        Quote lastQuote = this.marketDataManager.getLastQuote();
        List<Quote> quoteList = this.marketDataManager.getQuoteList();
        if (lastQuote == null || quoteList.isEmpty()) {
            value = 0.0;
        } else {
            double totalVol = lastQuote.getTotalVolume();
            if (totalVol == 0.0) {
                totalVol = 1.0;
            }
            double bidQty = 0.0;
            for (Quote quote : quoteList) {
                if (quote.getTimestamp().compareTo(this.date920) < 0) continue;
                bidQty = ((QtyPrice)quote.getBids().get(0)).getQuantity() + ((QtyPrice)quote.getBids().get(1)).getQuantity();
                break;
            }
            value = totalVol + bidQty == 0.0 ? 0.0 : totalVol / (totalVol + bidQty);
        }
        this.updateValue(0, value);
    }
}


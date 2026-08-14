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

public class Saturn_t930_pj2_last_cancel_chance_price
extends BaseFactor {
    private final Date date920;

    public Saturn_t930_pj2_last_cancel_chance_price(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_last_cancel_chance_price"};
        this.date920 = TimeUtil.getDateTime(marketDataManager.getParams().getTradeDate(), LocalTime.of(9, 20));
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        Quote lastQuote = this.marketDataManager.getLastQuote();
        List<Quote> quoteList = this.marketDataManager.getQuoteList();
        if (lastQuote != null && !quoteList.isEmpty()) {
            double preClose = this.marketDataManager.getPreClose();
            double lastPrice = lastQuote.getLastPx() == 0.0 ? ((QtyPrice)lastQuote.getBids().get(0)).getPrice() : lastQuote.getLastPx();
            for (Quote quote : quoteList) {
                if (quote.getTimestamp().compareTo(this.date920) < 0) continue;
                value = (((QtyPrice)quote.getBids().get(0)).getPrice() - lastPrice) / preClose;
                break;
            }
        }
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.0;
        }
        if (this.marketDataManager.isStartsWith3()) {
            value /= 2.0;
        }
        this.updateValue(0, value);
    }
}


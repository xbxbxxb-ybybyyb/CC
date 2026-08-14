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

public class Saturn_t930_wd_jhk_915_925_pct
extends BaseFactor {
    private final Date date915;
    private final Date date916;

    public Saturn_t930_wd_jhk_915_925_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jhk_915_925_pct"};
        this.date915 = TimeUtil.getDateTime(marketDataManager.getParams().getTradeDate(), LocalTime.of(9, 15));
        this.date916 = TimeUtil.getDateTime(marketDataManager.getParams().getTradeDate(), LocalTime.of(9, 16));
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        List<Quote> quoteList = this.marketDataManager.getQuoteList();
        if (quoteList.size() > 0) {
            Double price915_916 = quoteList.stream().filter(e -> e.getTimestamp().compareTo(this.date916) <= 0 && e.getTimestamp().compareTo(this.date915) >= 0).mapToDouble(e -> ((QtyPrice)e.getBids().get(0)).getPrice()).filter(p -> p > 0.0).average().orElse(Double.NaN);
            Double preClosePx = this.marketDataManager.getPreClose();
            Quote lastQuote = this.marketDataManager.getLastQuote();
            if (lastQuote != null && preClosePx != null && preClosePx > 0.0) {
                value = (lastQuote.getLastPx() - price915_916) / preClosePx;
            }
        }
        if (this.marketDataManager.getSymbol().startsWith("3")) {
            value /= 2.0;
        }
        this.updateValue(0, Double.isInfinite(value) || Double.isNaN(value) ? 0.0 : value);
    }
}


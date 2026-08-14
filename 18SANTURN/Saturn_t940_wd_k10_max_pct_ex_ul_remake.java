/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_k10_max_pct_ex_ul_remake
extends BaseFactor {
    public Saturn_t940_wd_k10_max_pct_ex_ul_remake(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_k10_max_pct_ex_ul_remake"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.01;
        List<Tick> tickList = this.marketDataManager.getCurrentTickList();
        if (tickList != null) {
            long d = TimeUtil.TimestampToLongDate(tickList.get(0).getTimestamp());
            double maxPct = 0.1;
            if (this.marketDataManager.getSymbol().startsWith("3")) {
                maxPct = 0.2;
            }
            double preClose = this.marketDataManager.getLastQuote().getPreviousClosingPx();
            double ulPx = Math.floor(preClose * 100.0 * (1.0 + maxPct) + 0.5) / 100.0;
            double preLastPx = 0.0;
            value = Double.MIN_VALUE;
            for (Tick t : this.marketDataManager.getCurrentLxjjTickList()) {
                if (preLastPx != 0.0 && t.getLastPx() / preLastPx - 1.0 > value && t.getLastPx() != ulPx) {
                    value = t.getLastPx() / preLastPx - 1.0;
                }
                preLastPx = t.getLastPx();
            }
            if (value == Double.MIN_VALUE) {
                value = 0.01;
            }
        }
        this.updateValue(0, value);
    }
}


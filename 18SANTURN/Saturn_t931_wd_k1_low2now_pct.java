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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_k1_low2now_pct
extends BaseFactor {
    public Saturn_t931_wd_k1_low2now_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_low2now_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.995;
        List<Tick> tickList = this.marketDataManager.getCurrentTickList();
        if (tickList != null) {
            ArrayList<Double> lastPriceList = new ArrayList<Double>();
            double lastPrice = 0.0;
            for (Tick t : tickList) {
                if (!(t.getLastPx() > 0.0)) continue;
                lastPriceList.add(t.getLastPx());
                lastPrice = t.getLastPx();
            }
            if (!lastPriceList.isEmpty()) {
                if (this.marketDataManager.isStartsWith3()) {
                    double prePx = this.marketDataManager.getPreClose();
                    factorValue = ((MathUtil.calculateMin(lastPriceList) / prePx - 1.0) / 2.0 + 1.0) / ((lastPrice / prePx - 1.0) / 2.0 + 1.0);
                } else {
                    factorValue = MathUtil.calculateMin(lastPriceList) / lastPrice;
                }
            } else {
                factorValue = Double.NaN;
            }
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.995 : factorValue);
    }
}


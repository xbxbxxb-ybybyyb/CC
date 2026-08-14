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
import java.util.HashSet;
import java.util.List;
import java.util.Map;

public class Saturn_t940_wd_cs10_excess_pct_chg
extends BaseFactor {
    public Saturn_t940_wd_cs10_excess_pct_chg(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_cs10_excess_pct_chg"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.02;
        if (this.marketDataManager.getSaturnAfterNotUlLenMap().get(this.marketDataManager.getSymbol()) != null && this.marketDataManager.getSaturnAfterNotUlLenMap().get(this.marketDataManager.getSymbol()) > 10) {
            HashSet<String> stockSet = new HashSet<String>();
            for (String symbol : this.marketDataManager.getSaturnStockSet()) {
                if (this.marketDataManager.getSaturnAfterNotUlLenMap().get(symbol) <= 10) continue;
                stockSet.add(symbol);
            }
            double currentPctChg = 0.0;
            ArrayList<Double> pctChgList = new ArrayList<Double>();
            for (String symbol : stockSet) {
                List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
                if (null == tickList || tickList.isEmpty()) continue;
                double t925LastPx = 0.0;
                for (Tick t : tickList) {
                    if (!(t.getTotalValueTrade() > 0.0)) continue;
                    t925LastPx = t.getLastPx();
                    break;
                }
                double pctChg = ((Tick)tickList.get(tickList.size() - 1)).getLastPx() / t925LastPx;
                pctChgList.add(pctChg);
                if (!symbol.equals(this.marketDataManager.getSymbol())) continue;
                currentPctChg = pctChg;
            }
            value = currentPctChg - MathUtil.calculateMean(pctChgList);
        }
        this.updateValue(0, value);
    }
}


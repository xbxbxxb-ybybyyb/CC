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
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Saturn_t931_wd_cs1_half_amt_pct_d_mean
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_wd_cs1_half_amt_pct_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cs1_half_amt_pct_d_mean"};
        String currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.025;
        Double currentHalfAmtPct = null;
        double halfAmtPctSum = 0.0;
        String currentSymbol = this.marketDataManager.getSymbol();
        int cnt = 0;
        for (String symbol : this.stocksFiltered) {
            List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
            if (null == tickList || tickList.isEmpty()) continue;
            ++cnt;
            double halfAmtPct = this.halfAmtPct(tickList);
            halfAmtPctSum += halfAmtPct;
            if (!symbol.equals(currentSymbol)) continue;
            currentHalfAmtPct = halfAmtPct;
        }
        if (currentHalfAmtPct != null && halfAmtPctSum != 0.0) {
            factorValue = currentHalfAmtPct / halfAmtPctSum * (double)cnt;
        }
        this.updateValue(0, factorValue);
    }

    private double halfAmtPct(List<Tick> tickList) {
        if (null == tickList || tickList.isEmpty()) {
            return 0.0;
        }
        Tick lastTick = tickList.get(tickList.size() - 1);
        if (lastTick.getLastPx() <= 0.0) {
            return 0.0;
        }
        double lastAmt = lastTick.getTotalValueTrade();
        Double firstAmt = null;
        int index = -1;
        for (Tick tick : tickList) {
            if (tick.getLastPx() > 0.0) {
                if (null == firstAmt) {
                    firstAmt = tick.getTotalValueTrade();
                }
                if (tick.getMdTime() > 93030000L) break;
            }
            ++index;
        }
        if (null == firstAmt) {
            return 0.0;
        }
        return index >= 0 && index < tickList.size() ? (tickList.get(index).getTotalValueTrade() - firstAmt) / lastAmt : 0.0;
    }
}


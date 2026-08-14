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

public class Saturn_t931_wd_cs1_rise_px_mean_d_sum
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_wd_cs1_rise_px_mean_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cs1_rise_px_mean_d_sum"};
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
        Double currentF3 = null;
        double f3Sum = 0.0;
        String currentSymbol = this.marketDataManager.getSymbol();
        for (String symbol : this.stocksFiltered) {
            List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
            double f3 = this.calcF3(tickList);
            f3Sum += f3;
            if (!symbol.equals(currentSymbol)) continue;
            currentF3 = f3;
        }
        if (currentF3 != null && f3Sum != 0.0) {
            factorValue = currentF3 / f3Sum;
        }
        this.updateValue(0, factorValue);
    }

    private double calcF3(List<Tick> tickList) {
        if (null == tickList || tickList.size() <= 1) {
            return 0.0;
        }
        double validCount = 0.0;
        double totalTickCount = 0.0;
        Double preLastPx = null;
        for (Tick tick : tickList) {
            if (!(tick.getLastPx() > 0.0)) continue;
            if (null != preLastPx && tick.getLastPx() > preLastPx) {
                validCount += 1.0;
            }
            preLastPx = tick.getLastPx();
            totalTickCount += 1.0;
        }
        return validCount / totalTickCount;
    }
}


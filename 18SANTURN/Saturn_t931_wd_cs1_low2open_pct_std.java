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
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Saturn_t931_wd_cs1_low2open_pct_std
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_wd_cs1_low2open_pct_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cs1_low2open_pct_std"};
        String currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.01;
        if (this.stocksFiltered.size() > 0) {
            ArrayList<Double> low2OpenPctList = new ArrayList<Double>(this.stocksFiltered.size());
            for (String stock : this.stocksFiltered) {
                List tickList = this.marketDataManager.getTickListMap().get((Object)stock);
                double low2OpenPct = this.calcLow2OpenPct(tickList);
                if (Double.isNaN(low2OpenPct)) continue;
                low2OpenPctList.add(low2OpenPct);
            }
            factorValue = MathUtil.calculateStd(low2OpenPctList);
        }
        this.updateValue(0, factorValue);
    }

    private double calcLow2OpenPct(List<Tick> tickList) {
        if (null == tickList || tickList.isEmpty()) {
            return Double.NaN;
        }
        Double openPx = null;
        Double lowPx = null;
        for (Tick tick : tickList) {
            if (!(tick.getLastPx() > 0.0)) continue;
            if (null == openPx) {
                openPx = tick.getLastPx();
            }
            lowPx = null == lowPx ? tick.getLastPx() : Double.min(lowPx, tick.getLastPx());
        }
        return null == openPx ? Double.NaN : lowPx / openPx - 1.0;
    }
}


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
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Saturn_t931_sss_tk1mcs_amtbuy_chg_rank
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_sss_tk1mcs_amtbuy_chg_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1mcs_amtbuy_chg_rank"};
        String currentSymbol = this.marketDataManager.getSymbol();
        Map<String, Integer> map = this.marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        String currentSymbol = this.marketDataManager.getSymbol();
        ArrayList<Double> factorList = new ArrayList<Double>();
        for (String symbol : this.stocksFiltered) {
            List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
            double v = this.getValue(tickList);
            if (symbol.equals(currentSymbol)) {
                value = v;
            }
            factorList.add(v);
        }
        int count1 = 0;
        int count2 = 0;
        for (Double d : factorList) {
            if (d < value) {
                ++count1;
            }
            if (!(d <= value)) continue;
            ++count2;
        }
        double factorValue = 1.0 * (double)(count1 + count2 + 1) / 2.0 / (double)factorList.stream().filter(e -> !Double.isNaN(e)).count() - 0.5;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }

    private double getValue(List<Tick> tickList) {
        Tick t;
        int i;
        int firstValidIndex = -1;
        double value1 = 0.0;
        double value2 = 0.0;
        for (i = 0; i < tickList.size(); ++i) {
            t = tickList.get(i);
            if (t.getTotalBidQty() == 0.0 || t.getWeightedAvgBidPx() == 0.0 || Double.isNaN(t.getLastPx()) || t.getLastPx() == 0.0) continue;
            firstValidIndex = i;
            value1 = t.getTotalBidQty() * t.getWeightedAvgBidPx();
            break;
        }
        if (firstValidIndex != -1) {
            for (i = tickList.size() - 1; i >= 0; --i) {
                t = tickList.get(i);
                if (t.getTotalBidQty() == 0.0 || t.getWeightedAvgBidPx() == 0.0 || Double.isNaN(t.getLastPx()) || t.getLastPx() == 0.0) continue;
                value2 = t.getTotalBidQty() * t.getWeightedAvgBidPx();
                break;
            }
            return value2 - value1;
        }
        return Double.NaN;
    }
}


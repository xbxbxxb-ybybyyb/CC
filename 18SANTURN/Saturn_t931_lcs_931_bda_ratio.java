/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.ArrayListMultimap
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.ArrayListMultimap;
import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Saturn_t931_lcs_931_bda_ratio
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_lcs_931_bda_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_lcs_931_bda_ratio"};
        String currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.stocksFiltered.size() > 0) {
            double mba = 0.0;
            String currentSymbol = this.marketDataManager.getSymbol();
            ArrayList<Double> mbaMeanList = new ArrayList<Double>(this.stocksFiltered.size());
            ArrayListMultimap<String, Tick> tickListMap = this.marketDataManager.getTickListMap();
            for (String symbol : this.stocksFiltered) {
                double mean;
                if (!tickListMap.containsKey((Object)symbol)) continue;
                if (symbol.equals(currentSymbol)) {
                    mba = mean = tickListMap.get((Object)symbol).stream().filter(tick -> tick.getMdTime() >= 92500000L && tick.getLastPx() != 0.0).mapToDouble(tick -> tick.getTotalBidQty() / (tick.getTotalOfferQty() + tick.getTotalBidQty())).average().orElse(0.0);
                } else {
                    mean = tickListMap.get((Object)symbol).stream().mapToDouble(tick -> tick.getTotalBidQty() / (tick.getTotalOfferQty() + tick.getTotalBidQty())).average().orElse(0.0);
                }
                mbaMeanList.add(mean);
            }
            double bdaAvg = MathUtil.calculateMean(mbaMeanList);
            if (bdaAvg != 0.0) {
                value = mba / bdaAvg;
            }
        }
        this.updateValue(0, value);
    }
}


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
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class Saturn_t931_wd_cs1_bid_d_sum
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_wd_cs1_bid_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cs1_bid_d_sum"};
        String currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double bidAmtSum;
        double value = 0.007;
        Map<String, Tick> lastTickMap = this.marketDataManager.getLastTickMap();
        Tick currentLastTick = this.marketDataManager.getCurrentLastTick();
        if (null != currentLastTick && (bidAmtSum = this.stocksFiltered.stream().mapToDouble(stock -> {
            Tick lastTick = (Tick)lastTickMap.get(stock);
            if (null == lastTick) {
                return 0.0;
            }
            return lastTick.getWeightedAvgBidPx() * lastTick.getTotalBidQty();
        }).sum()) != 0.0) {
            value = currentLastTick.getWeightedAvgBidPx() * currentLastTick.getTotalBidQty() / bidAmtSum;
        }
        this.updateValue(0, value);
    }
}


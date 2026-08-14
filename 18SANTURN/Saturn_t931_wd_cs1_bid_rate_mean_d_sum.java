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

public class Saturn_t931_wd_cs1_bid_rate_mean_d_sum
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_wd_cs1_bid_rate_mean_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cs1_bid_rate_mean_d_sum"};
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
        Double currentBidQtyRateMean = null;
        double bidQtyRateMeanSum = 0.0;
        String currentSymbol = this.marketDataManager.getSymbol();
        for (String symbol : this.stocksFiltered) {
            List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
            double bidQtyRateMean = this.calcBidQtyRateMean(tickList);
            bidQtyRateMeanSum += bidQtyRateMean;
            if (!symbol.equals(currentSymbol)) continue;
            currentBidQtyRateMean = bidQtyRateMean;
        }
        if (currentBidQtyRateMean != null && bidQtyRateMeanSum != 0.0) {
            factorValue = currentBidQtyRateMean / bidQtyRateMeanSum;
        }
        this.updateValue(0, factorValue);
    }

    private double calcBidQtyRateMean(List<Tick> tickList) {
        if (null == tickList || tickList.isEmpty()) {
            return 0.0;
        }
        return tickList.stream().filter(tick -> tick.getLastPx() > 0.0).mapToDouble(tick -> tick.getTotalBidQty() / (tick.getTotalBidQty() + tick.getTotalOfferQty())).average().orElse(0.0);
    }
}


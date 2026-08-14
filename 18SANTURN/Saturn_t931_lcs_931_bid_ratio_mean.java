/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  org.apache.commons.lang3.tuple.Pair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.Pair;

public class Saturn_t931_lcs_931_bid_ratio_mean
extends BaseFactor {
    private final String currentSymbol;
    private final Set<String> stocksFiltered;

    public Saturn_t931_lcs_931_bid_ratio_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_lcs_931_bid_ratio_mean"};
        this.currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(this.currentSymbol) && map.get(this.currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.0;
        if (this.stocksFiltered.size() > 0) {
            HashMap allBidAmtMap = new HashMap(128);
            HashMap<Long, Pair> currentBidAmtInfo = new HashMap<Long, Pair>(64);
            for (String symbol : this.stocksFiltered) {
                boolean isCurrentSymbol = symbol.equals(this.currentSymbol);
                List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
                if (null == tickList || tickList.size() <= 0) continue;
                TreeMap<Long, Double> bidAmtMap = new TreeMap<Long, Double>();
                for (Tick tick : tickList) {
                    long mdTime = tick.getMdTime();
                    if (mdTime < 93000000L || tick.getLastPx() == 0.0) continue;
                    Long newTime = mdTime / 100000L * 100L + mdTime % 100000L / 3000L * 3L;
                    double bidAmt = tick.getTotalBidQty() * tick.getWeightedAvgBidPx();
                    bidAmtMap.put(newTime, bidAmt);
                    if (!isCurrentSymbol) continue;
                    currentBidAmtInfo.put(mdTime, Pair.of((Object)newTime, (Object)bidAmt));
                }
                allBidAmtMap.put(symbol, bidAmtMap);
            }
            if (currentBidAmtInfo.size() > 0) {
                factorValue = currentBidAmtInfo.values().stream().mapToDouble(pair -> (Double)pair.getValue() / this.calcUlTotBidByTime(allBidAmtMap, (Long)pair.getKey())).average().orElse(0.0);
            }
        }
        factorValue = Double.isNaN(factorValue) ? 0.0 : factorValue;
        this.updateValue(0, factorValue);
    }

    private double calcUlTotBidByTime(Map<String, TreeMap<Long, Double>> allBidAmtMap, Long time) {
        double bidAmtSum = allBidAmtMap.values().stream().mapToDouble(timeToBidAmt -> this.calcBidAmtByTime((TreeMap<Long, Double>)timeToBidAmt, time)).sum();
        return bidAmtSum == 0.0 ? Double.NaN : bidAmtSum;
    }

    private double calcBidAmtByTime(TreeMap<Long, Double> timeToBidAmt, Long time) {
        if (null == timeToBidAmt || timeToBidAmt.isEmpty()) {
            return 0.0;
        }
        Map.Entry<Long, Double> entry = timeToBidAmt.floorEntry(time);
        return null == entry ? 0.0 : entry.getValue();
    }
}


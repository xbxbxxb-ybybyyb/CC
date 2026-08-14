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

public class Saturn_t931_wd_cs1_amt_d_mean
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_wd_cs1_amt_d_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cs1_amt_d_mean"};
        String currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.017;
        Map<String, Tick> lastTickMap = this.marketDataManager.getLastTickMap();
        Tick currentLastTick = this.marketDataManager.getCurrentLastTick();
        if (null != currentLastTick) {
            double totalValueTradeSum = 0.0;
            int cnt = 0;
            for (String stock : this.stocksFiltered) {
                Tick lastTick = lastTickMap.get(stock);
                if (null == lastTick || lastTick.getLastPx() <= 0.0) continue;
                ++cnt;
                totalValueTradeSum += lastTick.getTotalValueTrade().doubleValue();
            }
            if (totalValueTradeSum != 0.0) {
                factorValue = currentLastTick.getTotalValueTrade() / totalValueTradeSum * (double)cnt;
            }
        }
        this.updateValue(0, factorValue);
    }
}


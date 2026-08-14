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

public class Saturn_t931_sss_tk1mcs_amtdiffp_mean
extends BaseFactor {
    private final Set<String> stocksFiltered;

    public Saturn_t931_sss_tk1mcs_amtdiffp_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1mcs_amtdiffp_mean"};
        String currentSymbol = this.marketDataManager.getSymbol();
        Map<String, Integer> map = this.marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(currentSymbol) && map.get(currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Double> factorList = new ArrayList<Double>();
        for (String symbol : this.stocksFiltered) {
            List tickList = this.marketDataManager.getTickListMap().get((Object)symbol);
            factorList.add(this.getValue(tickList) / this.marketDataManager.getPreFFSMap().get(symbol));
        }
        double factorValue = factorList.stream().filter(x -> !Double.isNaN(x)).mapToDouble(e -> e).average().orElse(0.0);
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.0 : factorValue);
    }

    private double getValue(List<Tick> tickList) {
        double value = Double.NaN;
        for (int i = tickList.size() - 1; i >= 0; --i) {
            Tick t = tickList.get(i);
            if (t.getWeightedAvgOfferPx() == 0.0 || t.getWeightedAvgBidPx() == 0.0 || t.getTotalOfferQty() == 0.0 || t.getTotalBidQty() == 0.0 || Double.isNaN(t.getLastPx())) continue;
            value = (t.getTotalBidQty() * t.getWeightedAvgBidPx() - t.getTotalOfferQty() * t.getWeightedAvgOfferPx()) / t.getPreviousClosingPx();
            break;
        }
        return value;
    }
}


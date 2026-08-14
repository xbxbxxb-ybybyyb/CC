/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.google.common.collect.ArrayListMultimap
 */
package com.huatai.strategy.strong.factor2;

import com.google.common.collect.ArrayListMultimap;
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

public class Saturn_t931_wd_k1_amt_d_b_m_rank
extends BaseFactor {
    private final Set<String> stocksFiltered;
    private final String currentSymbol;

    public Saturn_t931_wd_k1_amt_d_b_m_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_amt_d_b_m_rank"};
        this.currentSymbol = marketDataManager.getSymbol();
        Map<String, Integer> map = marketDataManager.getSaturnAfterNotUlLenMap();
        this.stocksFiltered = map != null && map.containsKey(this.currentSymbol) && map.get(this.currentSymbol) > 10 ? map.entrySet().stream().filter(e -> (Integer)e.getValue() > 10).map(Map.Entry::getKey).collect(Collectors.toSet()) : Collections.emptySet();
    }

    @Override
    public void calculate() {
        ArrayList<Double> pctList = new ArrayList<Double>();
        ArrayListMultimap<String, Tick> tickListMap = this.marketDataManager.getTickListMap();
        int i = 0;
        int index = 0;
        for (String symbol : this.stocksFiltered) {
            pctList.add(this.pct(tickListMap.get((Object)symbol)));
            if (this.currentSymbol.equals(symbol)) {
                index = i;
            }
            ++i;
        }
        List<Double> rankList = MathUtil.calcRankData(pctList, true);
        this.updateValue(0, rankList.isEmpty() || Double.isNaN(rankList.get(index)) ? 0.5 : rankList.get(index));
    }

    private double pct(List<Tick> tickList) {
        ArrayList<Double> res = new ArrayList<Double>();
        if (tickList != null) {
            for (int i = 0; i < tickList.size(); ++i) {
                double bidAmt;
                Tick t = tickList.get(i);
                if (t.getMdTime() < 93000000L) continue;
                double amt = i == 0 ? t.getTotalValueTrade() - this.marketDataManager.getJhjjTotalAmt() : t.getTotalValueTrade() - tickList.get(i - 1).getTotalValueTrade();
                if (!(t.getLastPx() > 0.0) || (bidAmt = t.getTotalBidQty() * t.getWeightedAvgBidPx()) == 0.0) continue;
                res.add(amt / bidAmt);
            }
        }
        return res.isEmpty() ? Double.NaN : MathUtil.calculateSortedMedian(res.stream().sorted().collect(Collectors.toList()));
    }
}


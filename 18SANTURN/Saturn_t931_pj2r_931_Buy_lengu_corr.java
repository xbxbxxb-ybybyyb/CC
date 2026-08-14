/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  org.apache.commons.lang3.tuple.Pair
 *  org.apache.commons.math3.stat.correlation.PearsonsCorrelation
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.commons.math3.stat.correlation.PearsonsCorrelation;

public class Saturn_t931_pj2r_931_Buy_lengu_corr
extends BaseFactor {
    public Saturn_t931_pj2r_931_Buy_lengu_corr(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Buy_lengu_corr"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, MarketOrder> lxjjBuyOrders = this.marketDataManager.getLxjjTradeBuyMap();
        ArrayList<Pair<Double, Integer>> qtyList = new ArrayList<Pair<Double, Integer>>(lxjjBuyOrders.size());
        ArrayList<Pair<Double, Integer>> fillCountList = new ArrayList<Pair<Double, Integer>>(lxjjBuyOrders.size());
        int index = 0;
        for (MarketOrder order : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            qtyList.add((Pair<Double, Integer>)Pair.of((Object)order.getQty(), (Object)index));
            fillCountList.add((Pair<Double, Integer>)Pair.of((Object)order.getFillList().size(), (Object)index));
            ++index;
        }
        double value = this.spearmanCorrelation(fillCountList, qtyList);
        this.updateValue(0, Double.isNaN(value) ? 0.0 : value);
    }

    public double spearmanCorrelation(List<Pair<Double, Integer>> base, List<Pair<Double, Integer>> other) {
        if (base.size() != other.size() || base.size() <= 1) {
            return 0.0;
        }
        double[] baseIndexList = this.getSortedIndexList(base);
        double[] otherIndexList = this.getSortedIndexList(other);
        return new PearsonsCorrelation().correlation(baseIndexList, otherIndexList);
    }

    private double[] getSortedIndexList(List<Pair<Double, Integer>> dataList) {
        int n;
        double[] result = new double[dataList.size()];
        dataList.sort(Map.Entry.comparingByKey());
        double rank = 1.0;
        for (int i = 0; i < dataList.size(); i += n) {
            int j;
            for (j = i; j < dataList.size() - 1 && ((Double)dataList.get(j).getKey()).equals(dataList.get(j + 1).getKey()); ++j) {
            }
            n = j - i + 1;
            for (j = 0; j < n; ++j) {
                int idx = (Integer)dataList.get(i + j).getValue();
                result[idx] = rank + (double)(n - 1) * 0.5;
            }
            rank += (double)n;
        }
        return result;
    }
}


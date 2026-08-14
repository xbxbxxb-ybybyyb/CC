/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  org.apache.commons.lang3.tuple.Pair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import org.apache.commons.lang3.tuple.Pair;

public class Saturn_t931_wd_t1_max_down_rate
extends BaseFactor {
    private final Map<Long, Double> tradeMoneyMap;
    private final Map<Long, Double> tradeQtyMap;

    public Saturn_t931_wd_t1_max_down_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_down_rate"};
        this.updateMode = 1;
        this.tradeMoneyMap = new TreeMap<Long, Double>();
        this.tradeQtyMap = new TreeMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        this.tradeMoneyMap.merge(fill.getMdTime() / 10000L, fill.getAmt(), Double::sum);
        this.tradeQtyMap.merge(fill.getMdTime() / 10000L, fill.getQty(), Double::sum);
    }

    @Override
    public void calculate() {
        ArrayList<Double> pct = new ArrayList<Double>();
        ArrayList<Double> down = new ArrayList<Double>();
        double lastVwap = Double.NaN;
        for (Long t : this.tradeMoneyMap.keySet()) {
            double vwap = this.tradeMoneyMap.get(t) / this.tradeQtyMap.get(t);
            down.add(vwap <= lastVwap ? 1.0 : 0.0);
            pct.add(vwap / lastVwap - 1.0);
            lastVwap = vwap;
        }
        Pair<Integer, Integer> pair = this.getMaxLenArr(down);
        double factorValue = pct.subList((Integer)pair.getLeft(), (Integer)pair.getRight()).stream().filter(x -> !Double.isNaN(x)).mapToDouble(e -> e).sum();
        if (this.marketDataManager.isStartsWith3()) {
            factorValue /= 2.0;
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? -0.0025 : factorValue);
    }

    private Pair<Integer, Integer> getMaxLenArr(List<Double> ser) {
        int startIndex = 0;
        int endIndex = 1;
        int maxLen = 0;
        for (int i = 0; i < ser.size() - 1; ++i) {
            for (int j = i + 1; j < ser.size(); ++j) {
                if (j - i <= maxLen || MathUtil.calculateMean(ser.subList(i, j)) != 1.0) continue;
                maxLen = j - i;
                startIndex = i;
                endIndex = j;
            }
        }
        return Pair.of((Object)startIndex, (Object)endIndex);
    }
}


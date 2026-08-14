/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_m10_trade_num_compare
extends BaseFactor {
    private final Map<Long, Double> numMap;

    public Saturn_t940_wd_m10_trade_num_compare(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_trade_num_compare"};
        this.updateMode = 1;
        this.numMap = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            this.numMap.merge(mdTime / 100000L, 1.0, Double::sum);
        }
    }

    @Override
    public void calculate() {
        double value = 3.25;
        if (this.numMap.size() != 0) {
            double[] countList = this.numMap.values().stream().sorted().mapToDouble(e -> e).toArray();
            double medianCount = MathUtil.calculateSortedMedian(countList);
            ArrayList<Double> m1 = new ArrayList<Double>();
            ArrayList<Double> m2 = new ArrayList<Double>();
            for (Long mdTime : this.numMap.keySet()) {
                if (this.numMap.get(mdTime) > medianCount) {
                    m1.add(this.numMap.get(mdTime));
                    continue;
                }
                m2.add(this.numMap.get(mdTime));
            }
            if (MathUtil.calculateMean(m1) != 0.0) {
                value = MathUtil.calculateMean(m2) / MathUtil.calculateMean(m1);
            }
        }
        this.updateValue(0, value);
    }
}


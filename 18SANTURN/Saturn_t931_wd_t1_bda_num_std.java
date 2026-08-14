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
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_t1_bda_num_std
extends BaseFactor {
    private final Map<Long, Set<Long>> fillBuyNoMap;
    private final Map<Long, Set<Long>> fillSellNoMap;

    public Saturn_t931_wd_t1_bda_num_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_bda_num_std"};
        this.updateMode = 1;
        this.fillBuyNoMap = new HashMap<Long, Set<Long>>();
        this.fillSellNoMap = new HashMap<Long, Set<Long>>();
    }

    @Override
    public void update(Fill fill) {
        this.fillBuyNoMap.computeIfAbsent(fill.getMdTime() / 1000L, k -> new HashSet());
        this.fillBuyNoMap.get(fill.getMdTime() / 1000L).add(fill.getBuyNo());
        this.fillSellNoMap.computeIfAbsent(fill.getMdTime() / 1000L, k -> new HashSet());
        this.fillSellNoMap.get(fill.getMdTime() / 1000L).add(fill.getSellNo());
    }

    @Override
    public void calculate() {
        ArrayList<Double> bda = new ArrayList<Double>();
        for (long t = 93000L; t < 93060L; ++t) {
            if (this.fillBuyNoMap.get(t) == null) continue;
            bda.add(1.0 * (double)this.fillBuyNoMap.get(t).size() / (double)this.fillSellNoMap.get(t).size());
        }
        double factorValue = MathUtil.calculateStd(bda);
        this.updateValue(0, Double.isNaN(factorValue) ? 1.4 : factorValue);
    }
}


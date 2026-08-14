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

public class Saturn_t940_wd_m10_bid_ask_rate_max
extends BaseFactor {
    private final Map<Long, Set<Long>> minuteSellNoMap;
    private final Map<Long, Set<Long>> minuteBuyNoMap;

    public Saturn_t940_wd_m10_bid_ask_rate_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_bid_ask_rate_max"};
        this.updateMode = 1;
        this.minuteSellNoMap = new HashMap<Long, Set<Long>>();
        this.minuteBuyNoMap = new HashMap<Long, Set<Long>>();
    }

    @Override
    public void update(Fill fill) {
        long time = fill.getMdTime();
        if (time < 94000000L) {
            long minute = time / 100000L;
            if (this.minuteBuyNoMap.get(minute) == null) {
                HashSet<Long> buySet = new HashSet<Long>();
                buySet.add(fill.getBuyNo());
                this.minuteBuyNoMap.put(minute, buySet);
            } else {
                this.minuteBuyNoMap.get(minute).add(fill.getBuyNo());
            }
            if (this.minuteSellNoMap.get(minute) == null) {
                HashSet<Long> sellSet = new HashSet<Long>();
                sellSet.add(fill.getSellNo());
                this.minuteSellNoMap.put(minute, sellSet);
            } else {
                this.minuteSellNoMap.get(minute).add(fill.getSellNo());
            }
        }
    }

    @Override
    public void calculate() {
        double value = 1.0;
        if (this.minuteBuyNoMap.size() != 0) {
            ArrayList<Double> askDBidList = new ArrayList<Double>();
            for (long minuteTime : this.minuteBuyNoMap.keySet()) {
                double ratio = 1.0 * (double)this.minuteSellNoMap.get(minuteTime).size() / (double)this.minuteBuyNoMap.get(minuteTime).size();
                if (!(ratio < 50.0)) continue;
                askDBidList.add(ratio);
            }
            if (askDBidList.size() > 0) {
                value = MathUtil.calculateMax(askDBidList);
            }
        }
        this.updateValue(0, value);
    }
}


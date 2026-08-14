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

public class Saturn_t931_wd_t1_ave_bid_amt_std_delta
extends BaseFactor {
    private final Map<Long, Double> totalAmount;
    private final Map<Long, Set<Long>> bidBuyNoMap;

    public Saturn_t931_wd_t1_ave_bid_amt_std_delta(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_ave_bid_amt_std_delta"};
        this.updateMode = 1;
        this.totalAmount = new HashMap<Long, Double>();
        this.bidBuyNoMap = new HashMap<Long, Set<Long>>();
    }

    @Override
    public void update(Fill fill) {
        this.totalAmount.merge(fill.getMdTime() / 1000L, fill.getAmt(), Double::sum);
        this.bidBuyNoMap.computeIfAbsent(fill.getMdTime() / 1000L, k -> new HashSet());
        this.bidBuyNoMap.get(fill.getMdTime() / 1000L).add(fill.getBuyNo());
    }

    @Override
    public void calculate() {
        ArrayList<Double> res = new ArrayList<Double>();
        for (long t = 93000L; t < 93060L; ++t) {
            if (this.bidBuyNoMap.get(t) != null) {
                res.add(this.totalAmount.get(t) / (double)this.bidBuyNoMap.get(t).size());
                continue;
            }
            res.add(Double.NaN);
        }
        ArrayList<Double> diff = new ArrayList<Double>();
        for (int i = 1; i < res.size(); ++i) {
            diff.add((Double)res.get(i) - (Double)res.get(i - 1));
        }
        double factorValue = MathUtil.calculateStd(diff);
        this.updateValue(0, Double.isNaN(factorValue) ? 4000.0 : factorValue);
    }
}


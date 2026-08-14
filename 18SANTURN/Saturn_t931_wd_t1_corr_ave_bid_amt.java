/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.Correlation;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_corr_ave_bid_amt
extends BaseFactor {
    TreeMap<Long, Set<Long>> tradeBuyNoMap = new TreeMap();
    TreeMap<Long, Double> tradeMoneyMap = new TreeMap();

    public Saturn_t931_wd_t1_corr_ave_bid_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_corr_ave_bid_amt"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        this.tradeBuyNoMap.computeIfAbsent(fill.getMdTime() / 1000L, k -> new HashSet());
        this.tradeBuyNoMap.get(fill.getMdTime() / 1000L).add(fill.getBuyNo());
        this.tradeMoneyMap.merge(fill.getMdTime() / 1000L, fill.getAmt(), Double::sum);
    }

    @Override
    public void calculate() {
        ArrayList<Double> amtList = new ArrayList<Double>();
        ArrayList<Double> aveBidAmtList = new ArrayList<Double>();
        for (Long t : this.tradeBuyNoMap.keySet()) {
            Double amt = this.tradeMoneyMap.get(t);
            Set<Long> buyNoSet = this.tradeBuyNoMap.get(t);
            aveBidAmtList.add(MathUtil.roundDecimal(amt / (double)buyNoSet.size(), 10));
            double roundAmt = MathUtil.roundDecimal(amt, 0);
            amtList.add(roundAmt);
        }
        double factorValue = Correlation.spearmanCorrelation(amtList, aveBidAmtList);
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.8 : factorValue);
    }
}


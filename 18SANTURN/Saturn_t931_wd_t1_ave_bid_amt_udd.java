/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_ave_bid_amt_udd
extends BaseFactor {
    TreeMap<Long, Set<Long>> tradeBuyNoMap = new TreeMap();
    TreeMap<Long, Double> tradeMoneyMap = new TreeMap();

    public Saturn_t931_wd_t1_ave_bid_amt_udd(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_ave_bid_amt_udd"};
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
            amtList.add(amt);
            aveBidAmtList.add(amt / (double)buyNoSet.size());
        }
        double median = MathUtil.calculateSortedMedian(aveBidAmtList.stream().sorted().collect(Collectors.toList()));
        double highPart = 0.0;
        int highCnt = 0;
        double lowPart = 0.0;
        for (Double d : aveBidAmtList) {
            if (d >= median) {
                highPart += d.doubleValue();
                ++highCnt;
                continue;
            }
            lowPart += d.doubleValue();
        }
        highPart = highCnt == 0 ? Double.NaN : highPart / (double)highCnt;
        lowPart = highCnt == aveBidAmtList.size() ? 0.0 : lowPart / (double)(aveBidAmtList.size() - highCnt);
        double factorValue = lowPart / highPart;
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 0.2 : factorValue);
    }
}


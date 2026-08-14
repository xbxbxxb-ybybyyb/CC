/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t940_pj2r_940_Convexity
extends BaseFactor {
    private final Map<Long, Double> transaction;
    private long end_Time;

    public Saturn_t940_pj2r_940_Convexity(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Convexity"};
        this.updateMode = 1;
        this.transaction = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L) {
            this.transaction.put(mdTime, fill.getPrice());
            if (mdTime > this.end_Time) {
                this.end_Time = mdTime;
            }
        }
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getLxjjFillList().size() > 1) {
            double jhjjPx = this.marketDataManager.getJhjjPrice();
            if (this.marketDataManager.getFillList().size() == this.marketDataManager.getLxjjFillList().size()) {
                jhjjPx = this.marketDataManager.getLastQuote().getPreviousClosingPx();
            }
            double end_price = this.marketDataManager.getLastFill().getPrice();
            List time_stamp = this.transaction.keySet().stream().sorted().collect(Collectors.toList());
            List price = this.transaction.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(Map.Entry::getValue).collect(Collectors.toList());
            double tot_slope = (end_price - jhjjPx) / (double)TimeUtil.calTimeDelta(93000000L, this.end_Time);
            ArrayList<Double> convexityList = new ArrayList<Double>();
            for (int i = 0; i < time_stamp.size(); ++i) {
                long timeCum = TimeUtil.calTimeDelta(93000000L, (Long)time_stamp.get(i));
                convexityList.add((((double)timeCum * tot_slope + jhjjPx) / (Double)price.get(i) - 1.0) * 100.0);
            }
            value = MathUtil.calculateMax(convexityList);
        }
        this.updateValue(0, value);
    }
}


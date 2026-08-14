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

public class Saturn_t940_wd_m10_ldc_935
extends BaseFactor {
    private final Map<Long, Double> lowMap;
    private final Map<Long, Double> closeMap;

    public Saturn_t940_wd_m10_ldc_935(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_ldc_935"};
        this.updateMode = 1;
        this.closeMap = new HashMap<Long, Double>();
        this.lowMap = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            long minute = mdTime / 100000L;
            this.closeMap.put(minute, fill.getPrice());
            this.lowMap.merge(minute, fill.getPrice(), Double::min);
        }
    }

    @Override
    public void calculate() {
        double value = 0.994;
        if (this.lowMap.size() != 0) {
            long[] minuteList = this.lowMap.keySet().stream().sorted().mapToLong(e -> e).toArray();
            ArrayList<Double> res = new ArrayList<Double>();
            for (int i = 0; i < minuteList.length / 2; ++i) {
                res.add(this.lowMap.get(minuteList[i]) / this.closeMap.get(minuteList[i]));
            }
            value = MathUtil.calculateMean(res);
        }
        this.updateValue(0, value);
    }
}


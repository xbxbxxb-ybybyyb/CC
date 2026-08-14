/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_m10_hdl_max_trade_num
extends BaseFactor {
    private final Map<Long, Double> hiMap;
    private final Map<Long, Double> lowMap;
    private final Map<Long, Integer> countMap;

    public Saturn_t940_wd_m10_hdl_max_trade_num(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_hdl_max_trade_num"};
        this.updateMode = 1;
        this.hiMap = new HashMap<Long, Double>();
        this.lowMap = new HashMap<Long, Double>();
        this.countMap = new HashMap<Long, Integer>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            long minute = mdTime / 100000L;
            this.hiMap.merge(minute, fill.getPrice(), Double::max);
            this.lowMap.merge(minute, fill.getPrice(), Double::min);
            this.countMap.merge(minute, 1, Integer::sum);
        }
    }

    @Override
    public void calculate() {
        double value = 1.005;
        if (this.hiMap.size() != 0) {
            double maxRatio1 = 0.0;
            double maxRatio2 = 0.0;
            double[] countList = this.countMap.values().stream().sorted().mapToDouble(e -> e.intValue()).toArray();
            double medianCount = MathUtil.calculateSortedMedian(countList);
            for (Long mdTime : this.hiMap.keySet()) {
                if ((double)this.countMap.get(mdTime).intValue() > medianCount) {
                    if (!(this.hiMap.get(mdTime) / this.lowMap.get(mdTime) > maxRatio1)) continue;
                    maxRatio1 = this.hiMap.get(mdTime) / this.lowMap.get(mdTime);
                    continue;
                }
                if (!(this.hiMap.get(mdTime) / this.lowMap.get(mdTime) > maxRatio2)) continue;
                maxRatio2 = this.hiMap.get(mdTime) / this.lowMap.get(mdTime);
            }
            if (maxRatio2 != 0.0) {
                value = maxRatio1 / maxRatio2;
            }
        }
        this.updateValue(0, value);
    }
}


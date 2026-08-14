/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_t10_trade3_ms_density
extends BaseFactor {
    private final Map<Integer, Integer> secondsCountMap;

    public Saturn_t940_wd_t10_trade3_ms_density(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_trade3_ms_density"};
        this.updateMode = 1;
        this.secondsCountMap = new HashMap<Integer, Integer>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L && fill.getSide() == Trade.Side.Bid) {
            int second = (int)(mdTime % 1000L / 100L);
            this.secondsCountMap.merge(second, 1, Integer::sum);
        }
    }

    @Override
    public void calculate() {
        double value = 0.25;
        int countSum = this.secondsCountMap.values().stream().mapToInt(e -> e).sum();
        if (countSum != 0) {
            value = 1.0 * (double)this.secondsCountMap.values().stream().sorted().limit(3L).mapToInt(e -> e).sum() / (double)countSum;
        }
        this.updateValue(0, value);
    }
}


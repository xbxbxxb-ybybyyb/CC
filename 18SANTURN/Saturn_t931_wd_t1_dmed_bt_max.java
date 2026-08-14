/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Map;

public class Saturn_t931_wd_t1_dmed_bt_max
extends BaseFactor {
    public Saturn_t931_wd_t1_dmed_bt_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_dmed_bt_max"};
    }

    @Override
    public void update(Fill fill) {
    }

    @Override
    public void calculate() {
        double median = MathUtil.calcMedian(this.marketDataManager.getLxjjFillList().stream().mapToDouble(Fill::getPrice).toArray());
        double maxTime = this.marketDataManager.getLxjjFillList().stream().filter(x -> x.getPrice() < median).mapToDouble(Fill::getMdTime).max().orElse(9.3055E7);
        this.updateValue(0, Double.isNaN(maxTime) || Double.isInfinite(maxTime) ? 9.3055E7 : maxTime);
    }
}


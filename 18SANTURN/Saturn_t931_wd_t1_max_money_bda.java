/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t931_wd_t1_max_money_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_max_money_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_max_money_bda"};
    }

    @Override
    public void update(Fill fill) {
    }

    @Override
    public void calculate() {
        double a = Math.log(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(e -> e.getAmt()).max().orElse(Double.NaN));
        double b = Math.log(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(e -> e.getAmt()).max().orElse(Double.NaN));
        double value = 0.49;
        if (a + b != 0.0) {
            value = a / (a + b);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.49 : value);
    }
}


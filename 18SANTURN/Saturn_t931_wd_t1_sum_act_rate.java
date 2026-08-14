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

public class Saturn_t931_wd_t1_sum_act_rate
extends BaseFactor {
    private final Map<Long, Double> totalAmount;
    private final Map<Long, Double> actAmount;

    public Saturn_t931_wd_t1_sum_act_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_sum_act_rate"};
        this.updateMode = 1;
        this.totalAmount = new HashMap<Long, Double>();
        this.actAmount = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        this.totalAmount.merge(fill.getMdTime() / 1000L, fill.getAmt(), Double::sum);
        if (fill.getSide() == Trade.Side.Bid) {
            this.actAmount.merge(fill.getMdTime() / 1000L, fill.getAmt(), Double::sum);
        }
    }

    @Override
    public void calculate() {
        double factorValue = 0.0;
        for (long t : this.actAmount.keySet()) {
            factorValue += this.actAmount.get(t) / this.totalAmount.get(t);
        }
        this.updateValue(0, Double.isNaN(factorValue) ? 30.0 : factorValue);
    }
}


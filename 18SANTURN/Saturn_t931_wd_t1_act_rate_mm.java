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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t931_wd_t1_act_rate_mm
extends BaseFactor {
    private final Map<Long, Double> totalAmount;
    private final Map<Long, Double> actAmount;

    public Saturn_t931_wd_t1_act_rate_mm(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_act_rate_mm"};
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
        ArrayList<Double> actRate = new ArrayList<Double>();
        for (long t : this.totalAmount.keySet()) {
            actRate.add(this.actAmount.getOrDefault(t, 0.0) / this.totalAmount.get(t));
        }
        double factorValue = MathUtil.calculateMax(actRate) != 0.0 ? MathUtil.calcNaNMean(actRate) / MathUtil.calculateMax(actRate) : Double.NaN;
        this.updateValue(0, Double.isNaN(factorValue) ? 0.6 : factorValue);
    }
}


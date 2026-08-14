/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t931_wd_t1_vdt
extends BaseFactor {
    private final Map<Long, Double> tradeMoneyMap;
    private final Map<Long, Double> tradeQtyMap;
    private double moneySum;
    private double qtySum;

    public Saturn_t931_wd_t1_vdt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_vdt"};
        this.updateMode = 1;
        this.tradeMoneyMap = new HashMap<Long, Double>();
        this.tradeQtyMap = new HashMap<Long, Double>();
        this.moneySum = 0.0;
        this.qtySum = 0.0;
    }

    @Override
    public void update(Fill fill) {
        this.tradeMoneyMap.merge(fill.getMdTime() / 10000L, fill.getAmt(), Double::sum);
        this.tradeQtyMap.merge(fill.getMdTime() / 10000L, fill.getQty(), Double::sum);
        this.moneySum += fill.getAmt().doubleValue();
        this.qtySum += fill.getQty().doubleValue();
    }

    @Override
    public void calculate() {
        double sum = 0.0;
        int count = 0;
        for (long t : this.tradeMoneyMap.keySet()) {
            sum += this.tradeMoneyMap.get(t) / this.tradeQtyMap.get(t);
            ++count;
        }
        double factorValue = this.moneySum / this.qtySum / (sum / (double)count);
        if (this.marketDataManager.isStartsWith3()) {
            double prePx = this.marketDataManager.getPreClose();
            factorValue = ((this.moneySum / this.qtySum / prePx - 1.0) / 2.0 + 1.0) / ((sum / (double)count / prePx - 1.0) / 2.0 + 1.0);
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 1.0 : factorValue);
    }
}


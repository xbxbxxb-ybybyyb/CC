/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  org.apache.commons.lang3.tuple.MutablePair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.LinkedHashMap;
import java.util.Map;
import org.apache.commons.lang3.tuple.MutablePair;

public class Saturn_t931_pj2r_931_Relative_total_strength
extends BaseFactor {
    private final Map<Long, MutablePair<Double, Double>> timeToQtyAndPrice;

    public Saturn_t931_pj2r_931_Relative_total_strength(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Relative_total_strength"};
        this.updateMode = 1;
        this.timeToQtyAndPrice = new LinkedHashMap<Long, MutablePair<Double, Double>>();
    }

    @Override
    public void update(Fill fill) {
        MutablePair qtyAndPrice;
        MutablePair mutablePair = qtyAndPrice = this.timeToQtyAndPrice.computeIfAbsent(fill.getMdTime(), k -> MutablePair.of((Object)0.0, (Object)0.0));
        mutablePair.left = (Double)mutablePair.left + fill.getQty();
        qtyAndPrice.right = fill.getPrice();
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getLxjjFillList().size() > 1) {
            double totalQtyMultiRet = 0.0;
            double preClose = this.marketDataManager.getPreClose();
            double price = this.marketDataManager.getJhjjPrice();
            for (MutablePair<Double, Double> qtyAndPrice : this.timeToQtyAndPrice.values()) {
                double ret = ((Double)qtyAndPrice.right - price) / preClose;
                totalQtyMultiRet += (Double)qtyAndPrice.left * 100.0 * ret;
                price = (Double)qtyAndPrice.right;
            }
            double totalQty = this.marketDataManager.getTotalQty();
            if (totalQty != 0.0) {
                value = totalQtyMultiRet / totalQty;
            }
        }
        this.updateValue(0, value);
    }
}


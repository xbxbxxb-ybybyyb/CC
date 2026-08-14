/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 *  org.apache.commons.lang3.tuple.MutablePair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.lang3.tuple.MutablePair;

public class Saturn_t931_wd_t1_bid_qty_s_density
extends BaseFactor {
    private final HashMap<Long, MutablePair<Double, Long>> buyQtyAndTimeMap = new HashMap();
    private double totalActiveSellQty = 0.0;

    public Saturn_t931_wd_t1_bid_qty_s_density(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_bid_qty_s_density"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        if (fill.getSide() == Trade.Side.Offer) {
            MutablePair qtyAndTime;
            this.totalActiveSellQty += fill.getQty().doubleValue();
            MutablePair mutablePair = qtyAndTime = this.buyQtyAndTimeMap.computeIfAbsent(fill.getBuyNo(), k -> MutablePair.of((Object)0.0, (Object)fill.getMdTime()));
            mutablePair.left = (Double)mutablePair.left + fill.getQty();
        }
    }

    @Override
    public void calculate() {
        if (this.buyQtyAndTimeMap.isEmpty() || this.totalActiveSellQty == 0.0) {
            this.updateValue(0, 0.3);
        } else {
            HashMap<Integer, Double> msQtyMap = new HashMap<Integer, Double>();
            for (MutablePair<Double, Long> qtyAndTime : this.buyQtyAndTimeMap.values()) {
                msQtyMap.merge((int)((Long)qtyAndTime.right / 1000L) % 10, (Double)qtyAndTime.left, Double::sum);
            }
            double max = msQtyMap.values().stream().mapToDouble(qty -> qty / this.totalActiveSellQty).max().orElse(0.3);
            this.updateValue(0, max);
        }
    }
}


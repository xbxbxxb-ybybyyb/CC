/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.ArrayList;
import java.util.Map;

public class Saturn_t940_wd_t10_max_s_qty_rate
extends BaseFactor {
    public Saturn_t940_wd_t10_max_s_qty_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_max_s_qty_rate"};
    }

    public static int compareTo(Long t1, Long t2) {
        return t1.compareTo(t2);
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Fill> fillList = new ArrayList<Fill>(this.marketDataManager.getLxjjFillList());
        fillList.sort((m1, m2) -> Saturn_t940_wd_t10_max_s_qty_rate.compareTo(m1.getMdTime(), m2.getMdTime()));
        double tradeQtySum = 0.0;
        Long second = null;
        double maxQty = 0.0;
        double secQtySum = 0.0;
        for (Fill fill : fillList) {
            long sec = fill.getMdTime() / 1000L;
            if (fill.getBuyNo() < fill.getSellNo()) {
                if (second == null) {
                    second = sec;
                    secQtySum += fill.getQty().doubleValue();
                } else if (second != sec) {
                    if (maxQty < secQtySum) {
                        maxQty = secQtySum;
                    }
                    secQtySum = fill.getQty();
                    second = sec;
                } else {
                    secQtySum += fill.getQty().doubleValue();
                }
            }
            tradeQtySum += fill.getQty().doubleValue();
        }
        if (tradeQtySum == 0.0) {
            this.updateValue(0, 0.1);
        } else {
            this.updateValue(0, maxQty / tradeQtySum);
        }
    }
}


/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_big_bid_d_last
extends BaseFactor {
    public Saturn_t931_wd_t1_big_bid_d_last(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_big_bid_d_last"};
    }

    @Override
    public void calculate() {
        double factorValue = 1.0;
        TreeMap<Long, MarketOrder> lxjjTradeBuyMap = this.marketDataManager.getLxjjTradeBuyMap();
        if (lxjjTradeBuyMap != null) {
            double moneySum = lxjjTradeBuyMap.values().stream().filter(x -> x.getAmt() > 50000.0).mapToDouble(MarketOrder::getAmt).sum();
            double qtySum = lxjjTradeBuyMap.values().stream().filter(x -> x.getAmt() > 50000.0).mapToDouble(MarketOrder::getQty).sum();
            double big_vwap = moneySum / qtySum;
            double lastPx = this.marketDataManager.getLastFill().getPrice();
            if (this.marketDataManager.isStartsWith3()) {
                double prePx = this.marketDataManager.getPreClose();
                factorValue = ((big_vwap / prePx - 1.0) / 2.0 + 1.0) / ((lastPx / prePx - 1.0) / 2.0 + 1.0);
            } else {
                factorValue = big_vwap / lastPx;
            }
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 1.0 : factorValue);
    }
}


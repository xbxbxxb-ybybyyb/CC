/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t931_wd_t1_up_med_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_up_med_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_up_med_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 5.0;
        Map<Long, MarketOrder> buyOrderMap = this.marketDataManager.getTradeBuyMap();
        if (buyOrderMap.size() > 0) {
            double bidQtyMedian = MathUtil.calcMedian(buyOrderMap.values().stream().mapToDouble(MarketOrder::getQty).toArray());
            HashMap<Long, Double> buyOrders = new HashMap<Long, Double>();
            HashMap<Long, Double> sellOrders = new HashMap<Long, Double>();
            for (MarketOrder order : buyOrderMap.values()) {
                if (order.getQty() > bidQtyMedian) {
                    buyOrders.put(order.getNo(), order.getQty());
                } else {
                    for (Fill fill : order.getFillList()) {
                        sellOrders.merge(fill.getSellNo(), fill.getQty(), Double::sum);
                    }
                }
                if (buyOrders.size() <= 0 || sellOrders.size() <= 0) continue;
                double bidMean = buyOrders.values().stream().mapToDouble(Double::doubleValue).average().orElse(Double.NaN);
                double askMean = sellOrders.values().stream().mapToDouble(Double::doubleValue).average().orElse(Double.NaN);
                factorValue = bidMean / askMean;
            }
        }
        factorValue = Double.isNaN(factorValue) ? 5.0 : factorValue;
        this.updateValue(0, factorValue);
    }
}


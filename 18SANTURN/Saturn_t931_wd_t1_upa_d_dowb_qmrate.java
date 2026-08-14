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
import java.util.TreeMap;

public class Saturn_t931_wd_t1_upa_d_dowb_qmrate
extends BaseFactor {
    public Saturn_t931_wd_t1_upa_d_dowb_qmrate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_upa_d_dowb_qmrate"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorVal = 0.4;
        TreeMap<Long, Long> timeMap = new TreeMap<Long, Long>();
        for (Fill fill : this.marketDataManager.getLxjjFillList()) {
            long positive = 0L;
            long negative = 0L;
            if (fill.getBuyNo() > fill.getSellNo()) {
                positive = fill.getBuyNo();
                negative = fill.getSellNo();
            } else {
                positive = fill.getSellNo();
                negative = fill.getBuyNo();
            }
            if (!timeMap.containsKey(positive)) {
                timeMap.put(positive, fill.getMdTime());
            }
            if (timeMap.containsKey(negative)) continue;
            timeMap.put(negative, 0L);
        }
        if (!timeMap.isEmpty()) {
            long time = 93000000L;
            double bidSum = 0.0;
            double askSum = 0.0;
            HashMap<Long, Double> bidQty = new HashMap<Long, Double>();
            HashMap<Long, Double> askQty = new HashMap<Long, Double>();
            double buyMedian = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
            double sellMedian = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
            for (Map.Entry entry : timeMap.entrySet()) {
                Object bid;
                if ((Long)entry.getValue() != 0L) {
                    time = (Long)entry.getValue();
                }
                if ((bid = this.marketDataManager.getLxjjTradeBuyMap().get(entry.getKey())) != null) {
                    if (!(((MarketOrder)bid).getVwap() < buyMedian)) continue;
                    bidSum += ((MarketOrder)bid).getQty().doubleValue();
                    bidQty.merge(time, ((MarketOrder)bid).getQty(), Double::sum);
                    continue;
                }
                MarketOrder ask = this.marketDataManager.getLxjjTradeSellMap().get(entry.getKey());
                if (ask == null || !(ask.getVwap() >= sellMedian)) continue;
                askSum += ask.getQty().doubleValue();
                askQty.merge(time, ask.getQty(), Double::sum);
            }
            double bidMax = Double.NEGATIVE_INFINITY;
            for (Double val : bidQty.values()) {
                bidMax = Math.max(bidMax, val);
            }
            double askMax = Double.NEGATIVE_INFINITY;
            for (Double val : askQty.values()) {
                askMax = Math.max(askMax, val);
            }
            double bid = bidMax / bidSum;
            double ask = askMax / askSum;
            factorVal = bid / (bid + ask);
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.4 : factorVal);
    }
}


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
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_dv_ivl_mean
extends BaseFactor {
    public Saturn_t931_wd_t1_dv_ivl_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_dv_ivl_mean"};
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
            double bidCnt = 0.0;
            double askSum = 0.0;
            double askCnt = 0.0;
            long lastBidTime = -1L;
            long lastAskTime = -1L;
            double buyMedian = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
            double sellMedian = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
            for (Map.Entry entry : timeMap.entrySet()) {
                MarketOrder bid;
                if ((Long)entry.getValue() != 0L) {
                    time = (Long)entry.getValue();
                }
                if ((bid = this.marketDataManager.getLxjjTradeBuyMap().get(entry.getKey())) != null) {
                    if (!(bid.getVwap() < buyMedian)) continue;
                    if (lastBidTime != -1L) {
                        bidSum += (double)TimeUtil.calTimeDelta(lastBidTime, time);
                        bidCnt += 1.0;
                    }
                    lastBidTime = time;
                    continue;
                }
                MarketOrder ask = this.marketDataManager.getLxjjTradeSellMap().get(entry.getKey());
                if (ask == null || !(ask.getVwap() < sellMedian)) continue;
                if (lastAskTime != -1L) {
                    askSum += (double)TimeUtil.calTimeDelta(lastAskTime, time);
                    askCnt += 1.0;
                }
                lastAskTime = time;
            }
            double bid = bidSum / bidCnt;
            double ask = askSum / askCnt;
            factorVal = bid / (bid + ask);
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.4 : factorVal);
    }
}


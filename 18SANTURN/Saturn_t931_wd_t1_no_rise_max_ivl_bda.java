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
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_no_rise_max_ivl_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_no_rise_max_ivl_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_no_rise_max_ivl_bda"};
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
            double bidMax = Double.NEGATIVE_INFINITY;
            double askMax = Double.NEGATIVE_INFINITY;
            long lastBidTime = -1L;
            long lastAskTime = -1L;
            for (Map.Entry entry : timeMap.entrySet()) {
                MarketOrder bid;
                if ((Long)entry.getValue() != 0L) {
                    time = (Long)entry.getValue();
                }
                if ((bid = this.marketDataManager.getLxjjTradeBuyMap().get(entry.getKey())) != null) {
                    if (bid.getMaxPrice() != bid.getMinPrice()) continue;
                    if (lastBidTime != -1L) {
                        bidMax = Math.max(bidMax, (double)TimeUtil.calTimeDelta(lastBidTime, time));
                    }
                    lastBidTime = time;
                    continue;
                }
                MarketOrder ask = this.marketDataManager.getLxjjTradeSellMap().get(entry.getKey());
                if (ask == null || ask.getMaxPrice() != ask.getMinPrice()) continue;
                if (lastAskTime != -1L) {
                    askMax = Math.max(askMax, (double)TimeUtil.calTimeDelta(lastAskTime, time));
                }
                lastAskTime = time;
            }
            factorVal = bidMax / (bidMax + askMax);
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.4 : factorVal);
    }
}


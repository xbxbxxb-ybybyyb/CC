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
import java.util.HashSet;
import java.util.Map;

public class Saturn_t940_wd_t10_big_ask_bda
extends BaseFactor {
    public Saturn_t940_wd_t10_big_ask_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_big_ask_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Double median = MathUtil.calculateSortedMedian(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getQty).sorted().toArray());
        HashSet<Long> buyNoSet = new HashSet<Long>();
        HashSet<Long> sellNoSet = new HashSet<Long>();
        for (MarketOrder order : this.marketDataManager.getLxjjTradeSellMap().values()) {
            if (!(order.getQty() <= median)) continue;
            sellNoSet.add(order.getNo());
            for (Fill fill : order.getFillList()) {
                buyNoSet.add(fill.getBuyNo());
            }
        }
        double value = 0.6;
        if (buyNoSet.size() > 0 && sellNoSet.size() > 0) {
            value = (double)buyNoSet.size() * 1.0 / (double)sellNoSet.size();
        }
        this.updateValue(0, value);
    }
}


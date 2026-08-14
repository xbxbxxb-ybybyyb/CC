/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;

public class Saturn_t940_wd_cs10_bid_d_sum
extends BaseFactor {
    public Saturn_t940_wd_cs10_bid_d_sum(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_cs10_bid_d_sum"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.0075;
        if (this.marketDataManager.getSaturnAfterNotUlLenMap().containsKey(this.marketDataManager.getSymbol()) && this.marketDataManager.getSaturnAfterNotUlLenMap().get(this.marketDataManager.getSymbol()) > 10) {
            Map<String, Integer> sANLM = this.marketDataManager.getSaturnAfterNotUlLenMap();
            HashSet<String> stocksFiltered = new HashSet<String>();
            for (String s : this.marketDataManager.getSaturnStockSet()) {
                if (sANLM.get(s) <= 10) continue;
                stocksFiltered.add(s);
            }
            Map<String, Tick> tickList = this.marketDataManager.getLastTickMap();
            ArrayList<Double> bidAmtList = new ArrayList<Double>();
            double bid_amt = 0.0;
            for (String symbol : stocksFiltered) {
                Tick currentTick = tickList.get(symbol);
                if (null == currentTick) continue;
                bidAmtList.add(currentTick.getWeightedAvgBidPx() * currentTick.getTotalBidQty());
                if (!symbol.equals(this.marketDataManager.getSymbol())) continue;
                bid_amt = currentTick.getWeightedAvgBidPx() * currentTick.getTotalBidQty();
            }
            if (MathUtil.calculateSum(bidAmtList) != 0.0) {
                value = bid_amt / MathUtil.calculateSum(bidAmtList);
            }
        }
        this.updateValue(0, value);
    }
}


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
import java.util.List;
import java.util.Map;

public class Saturn_t931_pj2k_931_Sell1_price_last_up
extends BaseFactor {
    public Saturn_t931_pj2k_931_Sell1_price_last_up(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2k_931_Sell1_price_last_up"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sell1PriceLastUp = 0.0;
        List<Tick> currentTickList = this.marketDataManager.getCurrentTickList();
        if (currentTickList != null) {
            Double lastAsk0Price = null;
            double minAsk0Price = Double.MAX_VALUE;
            for (Tick tick : currentTickList) {
                double ask0Price = tick.getSellQtyPrice().get(0).getPrice();
                if (!(ask0Price > 0.0)) continue;
                lastAsk0Price = ask0Price;
                minAsk0Price = Double.min(ask0Price, minAsk0Price);
            }
            if (lastAsk0Price != null) {
                sell1PriceLastUp = (lastAsk0Price - minAsk0Price) / this.marketDataManager.getPreClose() * 100.0;
            }
            if (sell1PriceLastUp > 45.0) {
                sell1PriceLastUp = 0.0;
            }
        }
        if (this.marketDataManager.isStartsWith3()) {
            sell1PriceLastUp /= 2.0;
        }
        this.updateValue(0, sell1PriceLastUp);
    }
}


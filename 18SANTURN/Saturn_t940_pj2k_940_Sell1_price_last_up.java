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
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_pj2k_940_Sell1_price_last_up
extends BaseFactor {
    public Saturn_t940_pj2k_940_Sell1_price_last_up(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2k_940_Sell1_price_last_up"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double sell1_price_last_up = 0.0;
        List<Tick> currentTickList = this.marketDataManager.getCurrentTickList();
        if (currentTickList != null) {
            Double pre_close = this.marketDataManager.getLastQuote().getPreviousClosingPx();
            ArrayList<Double> sell1_price_walk = new ArrayList<Double>();
            for (Tick tick : currentTickList) {
                if (!(tick.getSellQtyPrice().get(0).getPrice() > 0.0)) continue;
                sell1_price_walk.add(tick.getSellQtyPrice().get(0).getPrice());
            }
            sell1_price_last_up = sell1_price_walk.size() != 0 ? ((Double)sell1_price_walk.get(sell1_price_walk.size() - 1) - MathUtil.calculateMin(sell1_price_walk)) / pre_close * 100.0 : 0.0;
            if (sell1_price_last_up > 45.0) {
                sell1_price_last_up = 0.0;
            }
            if (this.marketDataManager.getSymbol().startsWith("3") && TimeUtil.TimestampToLongDate(this.marketDataManager.getLastQuote().getTimestamp()) >= 20200824L) {
                sell1_price_last_up /= 2.0;
            }
        }
        this.updateValue(0, sell1_price_last_up);
    }
}


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t931_wd_t1_act_big_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_act_big_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_act_big_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value;
        double buySum = 0.0;
        double buyFilterSum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (!marketOrder.getSideSet().contains(Trade.Side.Bid)) continue;
            if (marketOrder.getAmt() > 50000.0) {
                buyFilterSum += marketOrder.getAmt().doubleValue();
            }
            buySum += marketOrder.getAmt().doubleValue();
        }
        double selSum = 0.0;
        double sellFilterSum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeSellMap().values()) {
            if (!marketOrder.getSideSet().contains(Trade.Side.Offer)) continue;
            if (marketOrder.getAmt() > 50000.0) {
                sellFilterSum += marketOrder.getAmt().doubleValue();
            }
            selSum += marketOrder.getAmt().doubleValue();
        }
        double bid = buyFilterSum / buySum;
        double ask = sellFilterSum / selSum;
        double d = value = bid + ask != 0.0 ? bid / (bid + ask) : Double.NaN;
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.45;
        }
        this.updateValue(0, value);
    }
}


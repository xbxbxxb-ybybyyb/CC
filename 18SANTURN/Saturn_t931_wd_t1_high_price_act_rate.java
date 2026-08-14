/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_t1_high_price_act_rate
extends BaseFactor {
    public Saturn_t931_wd_t1_high_price_act_rate(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_high_price_act_rate"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.7;
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        if (fillList.size() > 0) {
            double maxFillPrice = 0.99 * fillList.stream().mapToDouble(Fill::getPrice).max().orElse(0.0);
            double tradeQtySum = 0.0;
            double qtySum = 0.0;
            for (Fill fill : fillList) {
                if (!(fill.getPrice() >= maxFillPrice)) continue;
                tradeQtySum += fill.getQty().doubleValue();
                if (fill.getSide() != Trade.Side.Bid) continue;
                qtySum += fill.getQty().doubleValue();
            }
            value = qtySum / tradeQtySum;
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.7 : value);
    }
}


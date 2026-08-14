/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 *  com.huatai.common.util.DecimalUtil
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.util.DecimalUtil;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t940_wd_t10_act_rate_in_no_rise
extends BaseFactor {
    public Saturn_t940_wd_t10_act_rate_in_no_rise(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_t10_act_rate_in_no_rise"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Double buyQty = 0.0;
        Double sellQty = 0.0;
        for (MarketOrder order : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            double minPrice;
            double maxPrice = order.getMaxPrice();
            if (!DecimalUtil.equal((double)maxPrice, (double)(minPrice = order.getMinPrice()))) continue;
            for (Fill fill : order.getFillList()) {
                if (fill.getSide() == Trade.Side.Bid) {
                    buyQty = buyQty + fill.getQty();
                    continue;
                }
                if (fill.getSide() != Trade.Side.Offer) continue;
                sellQty = sellQty + fill.getQty();
            }
        }
        double value = 0.64;
        if (sellQty > 0.0) {
            value = buyQty / sellQty;
        }
        this.updateValue(0, value);
    }
}


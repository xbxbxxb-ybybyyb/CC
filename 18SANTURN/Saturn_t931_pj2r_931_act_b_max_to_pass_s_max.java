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

public class Saturn_t931_pj2r_931_act_b_max_to_pass_s_max
extends BaseFactor {
    public Saturn_t931_pj2r_931_act_b_max_to_pass_s_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_act_b_max_to_pass_s_max"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double maxSellQty;
        double maxBuyQty = this.marketDataManager.getLxjjTradeBuyMap().values().stream().filter(order -> order.getSideSet().contains(Trade.Side.Bid)).mapToDouble(MarketOrder::getQty).max().orElse(0.0);
        double value = maxBuyQty + (maxSellQty = this.marketDataManager.getLxjjTradeSellMap().values().stream().filter(order -> !order.getSideSet().contains(Trade.Side.Offer)).mapToDouble(MarketOrder::getQty).max().orElse(0.0)) == 0.0 ? 0.5 : maxBuyQty / (maxBuyQty + maxSellQty);
        this.updateValue(0, value);
    }
}


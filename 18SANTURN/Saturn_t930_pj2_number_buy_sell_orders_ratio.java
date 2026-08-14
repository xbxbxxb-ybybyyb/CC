/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_pj2_number_buy_sell_orders_ratio
extends BaseFactor {
    public Saturn_t930_pj2_number_buy_sell_orders_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_pj2_number_buy_sell_orders_ratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        int sellNum = this.marketDataManager.getJhjjTradeSellMap().size();
        int buyNum = this.marketDataManager.getJhjjTradeBuyMap().size();
        double value = buyNum + sellNum == 0 ? 0.0 : (double)buyNum / (double)(buyNum + sellNum);
        this.updateValue(0, value);
    }
}


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;

public class Saturn_t930_wd_jh_buy_vol_split
extends BaseFactor {
    public Saturn_t930_wd_jh_buy_vol_split(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_buy_vol_split"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value;
        Map<Long, MarketOrder> buyOrderMap = this.marketDataManager.getJhjjTradeBuyMap();
        if (buyOrderMap.size() == 0) {
            value = 0.2;
        } else {
            double totalQty = this.marketDataManager.getJhjjTotalQty();
            double sum = buyOrderMap.values().stream().mapToDouble(e -> Math.pow(e.getQty() / totalQty, 2.0)).sum();
            value = Math.sqrt(sum);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.2 : value);
    }
}


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

public class Saturn_t930_wd_jh_buy_up_big_vol_pct
extends BaseFactor {
    public Saturn_t930_wd_jh_buy_up_big_vol_pct(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_buy_up_big_vol_pct"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.77;
        if (this.marketDataManager.getJhjjTotalQty() != 0.0) {
            double sum1 = this.marketDataManager.getJhjjTradeBuyMap().values().stream().filter(f -> f.getAmt() > 50000.0).mapToDouble(MarketOrder::getQty).sum();
            value = sum1 / this.marketDataManager.getJhjjTotalQty();
        }
        this.updateValue(0, value);
    }
}


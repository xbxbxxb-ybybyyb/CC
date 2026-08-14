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

public class Saturn_t931_qyh_T1mtra_amtpertra_inout_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtra_amtpertra_inout_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtra_amtpertra_inout_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double buy_mean = this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getAmt).average().orElse(0.0);
        double sell_mean = this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getAmt).average().orElse(0.0);
        double factorVal = 25000.0;
        if (sell_mean > 0.001) {
            factorVal = buy_mean / sell_mean;
        }
        this.updateValue(0, factorVal);
    }
}


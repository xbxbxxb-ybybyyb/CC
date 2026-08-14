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
import java.util.List;
import java.util.Map;

public class Saturn_t930_wd_jh_act_trade_amt
extends BaseFactor {
    public Saturn_t930_wd_jh_act_trade_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t930_wd_jh_act_trade_amt"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double totalSum = 0.0;
        double currSum = 0.0;
        for (List<Trade> l : this.marketDataManager.getCsTradeMap().values()) {
            for (Trade trade : l) {
                if (trade.getTradeBuyNo() <= trade.getTradeSellNo()) continue;
                totalSum += trade.getTurnover().doubleValue();
                if (!trade.getSymbol().equals(this.marketDataManager.getSymbol())) continue;
                currSum += trade.getTurnover().doubleValue();
            }
        }
        this.updateValue(0, totalSum != 0.0 ? currSum / totalSum : 0.01);
    }
}


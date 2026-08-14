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
import java.util.Map;

public class Saturn_wd_lt1_last_d_10_amt
extends BaseFactor {
    private final double lastAllAmt;

    public Saturn_wd_lt1_last_d_10_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_wd_lt1_last_d_10_amt"};
        this.lastAllAmt = marketDataManager.getParams().getPreLxjjAmt();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double amt10;
        double factorValue = 5.0;
        Tick lastTick = this.marketDataManager.getCurrentLastTick();
        Tick firstTick = this.marketDataManager.getCurrentTickList().stream().filter(tick -> tick.getTotalValueTrade() > 0.0).findFirst().orElse(null);
        if (null != firstTick && null != lastTick && (amt10 = lastTick.getTotalValueTrade() - firstTick.getTotalValueTrade()) != 0.0) {
            factorValue = this.lastAllAmt / amt10;
        }
        this.updateValue(0, factorValue);
    }
}


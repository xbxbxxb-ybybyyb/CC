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
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_k1_o2p_ask_amt
extends BaseFactor {
    public Saturn_t931_wd_k1_o2p_ask_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_k1_o2p_ask_amt"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 2600000.0;
        List<Tick> tickList = this.marketDataManager.getCurrentTickList();
        Tick lastTick = this.marketDataManager.getCurrentLastTick();
        if (tickList != null && lastTick != null && lastTick.getLastPx() > 0.0) {
            for (Tick t : tickList) {
                if (!(t.getLastPx() > 0.0)) continue;
                factorValue = lastTick.getTotalOfferQty() * lastTick.getWeightedAvgOfferPx() - t.getTotalOfferQty() * t.getWeightedAvgOfferPx();
                break;
            }
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 2600000.0 : factorValue);
    }
}


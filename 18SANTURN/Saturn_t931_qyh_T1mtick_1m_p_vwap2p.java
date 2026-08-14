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

public class Saturn_t931_qyh_T1mtick_1m_p_vwap2p
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_p_vwap2p(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_p_vwap2p"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double prev_total_amt = this.marketDataManager.getJhjjTotalAmt();
        double prev_total_vol = this.marketDataManager.getJhjjTotalQty();
        double vwap2p_sum = 0.0;
        int vwap2p_counter = 0;
        double factorValue = 0.0;
        for (Tick curTick : tickList) {
            vwap2p_sum += (curTick.getTotalValueTrade() - prev_total_amt) / (curTick.getTotalVolumeTrade() - prev_total_vol) / curTick.getLastPx();
            ++vwap2p_counter;
            prev_total_amt = curTick.getTotalValueTrade();
            prev_total_vol = curTick.getTotalVolumeTrade();
        }
        factorValue = vwap2p_sum / (double)vwap2p_counter;
        if (Double.isNaN(factorValue)) {
            factorValue = 1.0;
        }
        this.updateValue(0, factorValue);
    }
}


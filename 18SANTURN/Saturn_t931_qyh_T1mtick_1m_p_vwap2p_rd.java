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

public class Saturn_t931_qyh_T1mtick_1m_p_vwap2p_rd
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_p_vwap2p_rd(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_p_vwap2p_rd"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double vwap2p_r_sum = 0.0;
        int vwap2p_r_counter = 0;
        double vwap2p_d_sum = 0.0;
        int vwap2p_d_counter = 0;
        double factorValue = 0.0;
        if (!tickList.isEmpty()) {
            double prev_total_amt = tickList.get(0).getTotalValueTrade();
            double prev_total_vol = tickList.get(0).getTotalVolumeTrade();
            double prev_lastpx = tickList.get(0).getLastPx();
            for (int i = 1; i < tickList.size(); ++i) {
                Tick tick = tickList.get(i);
                double amt = tick.getTotalValueTrade() - prev_total_amt;
                double vol = tick.getTotalVolumeTrade() - prev_total_vol;
                if (tick.getLastPx() - prev_lastpx > 0.0) {
                    vwap2p_r_sum += amt / vol / tick.getLastPx();
                    ++vwap2p_r_counter;
                } else if (tick.getLastPx() - prev_lastpx < 0.0) {
                    vwap2p_d_sum += amt / vol / tick.getLastPx();
                    ++vwap2p_d_counter;
                }
                prev_total_amt = tick.getTotalValueTrade();
                prev_total_vol = tick.getTotalVolumeTrade();
                prev_lastpx = tick.getLastPx();
            }
            factorValue = vwap2p_r_sum / (double)vwap2p_r_counter - vwap2p_d_sum / (double)vwap2p_d_counter;
            if (Double.isNaN(factorValue)) {
                factorValue = 0.001;
            }
        }
        this.updateValue(0, factorValue);
    }
}


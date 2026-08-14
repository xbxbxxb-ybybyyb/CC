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

public class Saturn_t931_qyh_T1mtick_1m_amt_b2s_diff_1
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_amt_b2s_diff_1(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_amt_b2s_diff_1"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double amt_delta = 0.0;
        if (!tickList.isEmpty()) {
            double amt_df_b_tail = tickList.get(tickList.size() - 1).getTotalBidQty() * tickList.get(tickList.size() - 1).getWeightedAvgBidPx();
            double amt_df_s_tail = tickList.get(tickList.size() - 1).getTotalOfferQty() * tickList.get(tickList.size() - 1).getWeightedAvgOfferPx();
            double amt_df_b_head = 0.0;
            double amt_df_s_head = 0.0;
            for (Tick tick : this.marketDataManager.getCurrentTickList()) {
                if (tick.getMdTime() < 92500000L) continue;
                amt_df_b_head = tick.getTotalBidQty() * tick.getWeightedAvgBidPx();
                amt_df_s_head = tick.getTotalOfferQty() * tick.getWeightedAvgOfferPx();
                break;
            }
            if ((amt_delta = amt_df_b_tail - amt_df_s_tail - (amt_df_b_head - amt_df_s_head)) <= -3.0E7) {
                amt_delta = -3.0E7;
            }
            if (amt_delta >= 3.0E7) {
                amt_delta = 3.0E7;
            }
            if (Double.isNaN(amt_delta)) {
                amt_delta = 0.0;
            }
        }
        this.updateValue(0, amt_delta);
    }
}


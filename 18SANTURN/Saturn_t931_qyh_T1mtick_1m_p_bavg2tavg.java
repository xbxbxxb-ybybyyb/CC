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

public class Saturn_t931_qyh_T1mtick_1m_p_bavg2tavg
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_p_bavg2tavg(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_p_bavg2tavg"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double preclose = this.marketDataManager.getPreClose();
        double prev_total_amt = this.marketDataManager.getJhjjTotalAmt();
        double prev_total_vol = this.marketDataManager.getJhjjTotalQty();
        double b12s1_sum = 0.0;
        int b12s1_cnt = 0;
        for (int i = 0; i < tickList.size(); ++i) {
            Tick curTick = tickList.get(i);
            b12s1_sum += ((curTick.getTotalValueTrade() - prev_total_amt) / (curTick.getTotalVolumeTrade() - prev_total_vol) - curTick.getWeightedAvgBidPx()) / preclose;
            ++b12s1_cnt;
            prev_total_amt = curTick.getTotalValueTrade();
            prev_total_vol = curTick.getTotalVolumeTrade();
        }
        double factorValue = b12s1_sum / (double)b12s1_cnt;
        if (this.marketDataManager.getSymbol().startsWith("3")) {
            factorValue /= 2.0;
        }
        if (Double.isNaN(factorValue)) {
            factorValue = 0.03;
        }
        this.updateValue(0, factorValue);
    }
}


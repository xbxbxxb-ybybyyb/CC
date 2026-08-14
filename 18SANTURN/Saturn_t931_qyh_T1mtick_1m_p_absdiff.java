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

public class Saturn_t931_qyh_T1mtick_1m_p_absdiff
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_p_absdiff(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_p_absdiff"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        Double openP = this.marketDataManager.getOpenPxMap().get(this.marketDataManager.getSymbol());
        double precloseP = this.marketDataManager.getPreClose();
        double factorValue = 0.0;
        if (openP != null && openP > 0.5 && tickList.size() > 0) {
            double prev_total_amt = this.marketDataManager.getJhjjTotalAmt();
            double prev_total_vol = this.marketDataManager.getJhjjTotalQty();
            double p_diff_abs_sum = 0.0;
            double prev_p = 0.0;
            for (int i = 0; i < tickList.size(); ++i) {
                Tick curTick = tickList.get(i);
                double cur_p = (curTick.getTotalValueTrade() - prev_total_amt) / (curTick.getTotalVolumeTrade() - prev_total_vol);
                prev_total_amt = curTick.getTotalValueTrade();
                prev_total_vol = curTick.getTotalVolumeTrade();
                if (i == 0) {
                    prev_p = cur_p;
                    continue;
                }
                p_diff_abs_sum += Math.abs(cur_p - prev_p);
                prev_p = cur_p;
            }
            factorValue = p_diff_abs_sum / precloseP;
        } else {
            factorValue = Double.NaN;
        }
        if (Double.isNaN(factorValue)) {
            factorValue = 0.05;
        }
        this.updateValue(0, factorValue);
    }
}


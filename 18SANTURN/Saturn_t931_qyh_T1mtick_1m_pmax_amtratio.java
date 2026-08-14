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
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_qyh_T1mtick_1m_pmax_amtratio
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_pmax_amtratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_pmax_amtratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double prev_total_amt = this.marketDataManager.getJhjjTotalAmt();
        ArrayList<Double> amtList = new ArrayList<Double>();
        double maxLastPrice = Double.MIN_VALUE;
        for (Tick tick : tickList) {
            if (tick.getMdTime() > 93000000L) {
                maxLastPrice = Math.max(maxLastPrice, tick.getLastPx());
            }
            amtList.add(tick.getTotalValueTrade() - prev_total_amt);
            prev_total_amt = tick.getTotalValueTrade();
        }
        double amt1Sum = 0.0;
        double amt_1Sum = 0.0;
        int amt1_cnt = 0;
        int amt_1_cnt = 0;
        double factorValue = 0.0;
        for (int i = 0; i < tickList.size(); ++i) {
            Tick curTick = tickList.get(i);
            if (curTick.getMdTime() <= 93000000L || !(curTick.getLastPx() >= maxLastPrice)) continue;
            if (i == 0) {
                amt_1Sum += ((Double)amtList.get(1)).doubleValue();
                ++amt_1_cnt;
                continue;
            }
            if (i == tickList.size() - 1) {
                if (tickList.get(i - 1).getMdTime() <= 93000000L) continue;
                amt1Sum += ((Double)amtList.get(i - 1)).doubleValue();
                ++amt1_cnt;
                continue;
            }
            if (tickList.get(i - 1).getMdTime() > 93000000L) {
                amt1Sum += ((Double)amtList.get(i - 1)).doubleValue();
                ++amt1_cnt;
            }
            amt_1Sum += ((Double)amtList.get(i + 1)).doubleValue();
            ++amt_1_cnt;
        }
        if (amt1_cnt == 0) {
            factorValue = 1.0;
        } else if (Math.abs(amt1Sum / (double)amt1_cnt) > 0.1 && Double.isNaN(factorValue = amt_1Sum / (double)amt_1_cnt / (amt1Sum / (double)amt1_cnt))) {
            factorValue = 1.0;
        }
        this.updateValue(0, factorValue);
    }
}


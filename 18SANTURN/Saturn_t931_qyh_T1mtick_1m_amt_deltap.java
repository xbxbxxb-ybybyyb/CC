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
import com.huatai.strategy.strong.util.MathUtil;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_qyh_T1mtick_1m_amt_deltap
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_amt_deltap(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_amt_deltap"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double prev_amt = this.marketDataManager.getJhjjTotalAmt();
        double prev_vol = this.marketDataManager.getJhjjTotalQty();
        ArrayList<Double> amtList = new ArrayList<Double>();
        ArrayList<Double> volList = new ArrayList<Double>();
        for (Tick tick : tickList) {
            amtList.add(new BigDecimal(tick.getTotalValueTrade() - prev_amt).setScale(2, 4).doubleValue());
            prev_amt = tick.getTotalValueTrade();
            volList.add(tick.getTotalVolumeTrade() - prev_vol);
            prev_vol = tick.getTotalVolumeTrade();
        }
        double preclose = this.marketDataManager.getPreClose();
        double amt_25 = MathUtil.calcPercentile(amtList, 25.0);
        double amt_75 = MathUtil.calcPercentile(amtList, 75.0);
        double factorValue = 0.0;
        double amt_sum_25 = 0.0;
        double amt_sum_75 = 0.0;
        double vol_sum_25 = 0.0;
        double vol_sum_75 = 0.0;
        for (int i = 0; i < tickList.size(); ++i) {
            if ((Double)amtList.get(i) <= amt_25) {
                amt_sum_25 += ((Double)amtList.get(i)).doubleValue();
                vol_sum_25 += ((Double)volList.get(i)).doubleValue();
                continue;
            }
            if (!((Double)amtList.get(i) >= amt_75)) continue;
            amt_sum_75 += ((Double)amtList.get(i)).doubleValue();
            vol_sum_75 += ((Double)volList.get(i)).doubleValue();
        }
        factorValue = (amt_sum_25 / vol_sum_25 - amt_sum_75 / vol_sum_75) / preclose;
        if (Double.isNaN(factorValue)) {
            factorValue = 0.0;
        }
        this.updateValue(0, factorValue);
    }
}


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
import java.util.List;
import java.util.Map;

public class Saturn_t931_qyh_T1mtick_1m_p_bavg_s
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_p_bavg_s(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_p_bavg_s"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> tickList = this.marketDataManager.getCurrentLxjjTickList();
        double preclose = this.marketDataManager.getPreClose();
        double[] bavg = tickList.stream().mapToDouble(a -> a.getWeightedAvgBidPx() / preclose).toArray();
        double factorValue = MathUtil.calculateStd(bavg);
        if (Double.isNaN(factorValue)) {
            factorValue = 0.001;
        }
        this.updateValue(0, factorValue);
    }
}


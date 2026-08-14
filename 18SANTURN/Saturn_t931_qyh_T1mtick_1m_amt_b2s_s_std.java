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
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_qyh_T1mtick_1m_amt_b2s_s_std
extends BaseFactor {
    public Saturn_t931_qyh_T1mtick_1m_amt_b2s_s_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_qyh_T1mtick_1m_amt_b2s_s_std"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Tick> currentTickList = this.marketDataManager.getCurrentTickList();
        ArrayList<Double> amt1 = new ArrayList<Double>();
        ArrayList<Double> amt_df_bPlusamt_df_s = new ArrayList<Double>();
        int cnt = 0;
        double factorValue = 0.1;
        for (Tick tick : currentTickList) {
            if (tick.getMdTime() < 92500000L) continue;
            double amt_df_b = tick.getTotalBidQty() * tick.getWeightedAvgBidPx();
            double amt_df_s = tick.getTotalOfferQty() * tick.getWeightedAvgOfferPx();
            amt1.add((amt_df_b - amt_df_s) / (amt_df_b + amt_df_s));
            amt_df_bPlusamt_df_s.add(amt_df_b + amt_df_s);
            ++cnt;
        }
        if (MathUtil.calculateMean(amt_df_bPlusamt_df_s) > 10.0) {
            factorValue = MathUtil.calculateStd(amt1);
        }
        if (Double.isNaN(factorValue)) {
            factorValue = 0.1;
        }
        this.updateValue(0, factorValue);
    }
}


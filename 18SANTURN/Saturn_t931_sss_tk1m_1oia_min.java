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
import java.util.Map;

public class Saturn_t931_sss_tk1m_1oia_min
extends BaseFactor {
    public Saturn_t931_sss_tk1m_1oia_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_1oia_min"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Double> oiList = new ArrayList<Double>();
        for (Tick t : this.marketDataManager.getLxjjTickList()) {
            if (t.getMdTime() <= 93000000L || t.getWeightedAvgBidPx() == 0.0 || t.getWeightedAvgOfferPx() == 0.0 || t.getTotalBidQty() == 0.0 || t.getTotalOfferQty() == 0.0) continue;
            double buyAmt = t.getWeightedAvgBidPx() * t.getTotalBidQty();
            double sellAmt = t.getWeightedAvgOfferPx() * t.getTotalOfferQty();
            double oi = (buyAmt - sellAmt) / (buyAmt + sellAmt);
            oiList.add(oi);
        }
        double value = MathUtil.calculateMin(oiList);
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.0;
        }
        this.updateValue(0, value);
    }
}


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

public class Saturn_t931_sss_tk1m_1oi_median
extends BaseFactor {
    public Saturn_t931_sss_tk1m_1oi_median(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_tk1m_1oi_median"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Double> oiList = new ArrayList<Double>();
        for (Tick t : this.marketDataManager.getLxjjTickList()) {
            if (t.getMdTime() <= 93000000L || t.getBuyQtyPrice().get(0).getPrice() == 0.0 || t.getSellQtyPrice().get(0).getPrice() == 0.0) continue;
            Double buyOneAmt = t.getBuyQtyPrice().get(0).getQuantity() * t.getBuyQtyPrice().get(0).getPrice();
            Double sellOneAmt = t.getSellQtyPrice().get(0).getQuantity() * t.getSellQtyPrice().get(0).getPrice();
            oiList.add((buyOneAmt - sellOneAmt) / (buyOneAmt + sellOneAmt));
        }
        double value = MathUtil.calcMedian(oiList.stream().mapToDouble(e -> e).toArray());
        if (Double.isNaN(value) || Double.isInfinite(value)) {
            value = 0.0;
        }
        this.updateValue(0, value);
    }
}


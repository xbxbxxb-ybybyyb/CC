/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_wd_t1_vwap_s10_beta
extends BaseFactor {
    public Saturn_t931_wd_t1_vwap_s10_beta(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_vwap_s10_beta"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        ArrayList<Double> vwaps = new ArrayList<Double>();
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (marketOrder.getFillList().get(0).getMdTime() > 93030000L) continue;
            vwaps.add(marketOrder.getAmt() / marketOrder.getQty());
        }
        double factorVal = 1.0;
        if (vwaps.size() >= 13) {
            List<Double> x = vwaps.subList(10, vwaps.size());
            List<Double> y = vwaps.subList(0, vwaps.size() - 10);
            factorVal = MathUtil.regressionResWithoutIntercept(y, x)[0][0];
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 1.0 : factorVal);
    }
}


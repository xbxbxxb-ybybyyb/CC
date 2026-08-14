/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.Map;
import java.util.TreeMap;

public class Saturn_t931_wd_t1_last10_vdv
extends BaseFactor {
    public Saturn_t931_wd_t1_last10_vdv(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_last10_vdv"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        TreeMap<Long, MarketOrder> marketOrderMap = this.marketDataManager.getLxjjTradeBuyMap();
        int i = 0;
        double sum1 = 0.0;
        double sum2 = 0.0;
        double sum3 = 0.0;
        double sum4 = 0.0;
        for (MarketOrder marketOrder : marketOrderMap.descendingMap().values()) {
            if (!marketOrder.getSideSet().contains(Trade.Side.Bid)) continue;
            if (i < 10) {
                sum1 += marketOrder.getAmt().doubleValue();
                sum2 += marketOrder.getQty().doubleValue();
            }
            sum3 += marketOrder.getAmt().doubleValue();
            sum4 += marketOrder.getQty().doubleValue();
            ++i;
        }
        double vwap_1 = sum1 / sum2;
        double vwap_2 = sum3 / sum4;
        double factorVal = vwap_1 / vwap_2;
        if (this.marketDataManager.isStartsWith3()) {
            double preClose = this.marketDataManager.getPreClose();
            factorVal = ((vwap_1 / preClose - 1.0) / 2.0 + 1.0) / ((vwap_2 / preClose - 1.0) / 2.0 + 1.0);
        }
        this.updateValue(0, Double.isNaN(factorVal) ? 1.0 : factorVal);
    }
}


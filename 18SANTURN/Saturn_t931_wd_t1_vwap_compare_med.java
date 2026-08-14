/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.Map;

public class Saturn_t931_wd_t1_vwap_compare_med
extends BaseFactor {
    public Saturn_t931_wd_t1_vwap_compare_med(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_vwap_compare_med"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Double median = MathUtil.calculateSortedMedian(this.marketDataManager.getLxjjFillList().stream().mapToDouble(Fill::getPrice).sorted().toArray());
        Double tradeMoneySum1 = 0.0;
        Double tradeQtySum1 = 0.0;
        Double tradeMoneySum2 = 0.0;
        Double tradeQtySum2 = 0.0;
        for (Fill fill : this.marketDataManager.getLxjjFillList()) {
            if (fill.getPrice() > median) {
                tradeMoneySum1 = tradeMoneySum1 + fill.getAmt();
                tradeQtySum1 = tradeQtySum1 + fill.getQty();
                continue;
            }
            tradeMoneySum2 = tradeMoneySum2 + fill.getAmt();
            tradeQtySum2 = tradeQtySum2 + fill.getQty();
        }
        double value = 1.007;
        if (tradeQtySum1 * tradeQtySum2 != 0.0) {
            value = tradeMoneySum1 / tradeQtySum1 / (tradeMoneySum2 / tradeQtySum2);
        }
        this.updateValue(0, value);
    }
}


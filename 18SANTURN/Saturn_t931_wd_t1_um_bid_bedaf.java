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
import java.util.Map;

public class Saturn_t931_wd_t1_um_bid_bedaf
extends BaseFactor {
    public Saturn_t931_wd_t1_um_bid_bedaf(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_um_bid_bedaf"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double median = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getQty).toArray());
        double b_sum = 0.0;
        double b_cnt = 0.0;
        double a_sum = 0.0;
        double a_cnt = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (!(marketOrder.getQty() > median)) continue;
            if (marketOrder.getFillList().get(0).getMdTime() <= 93030000L) {
                b_sum += marketOrder.getAmt().doubleValue();
                b_cnt += 1.0;
                continue;
            }
            a_sum += marketOrder.getAmt().doubleValue();
            a_cnt += 1.0;
        }
        double value = b_sum / b_cnt / a_sum * a_cnt;
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 1.0 : value);
    }
}


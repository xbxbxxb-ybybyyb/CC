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

public class Saturn_t931_wd_t1_um_big_up5w_rate_bda
extends BaseFactor {
    public Saturn_t931_wd_t1_um_big_up5w_rate_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_um_big_up5w_rate_bda"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double m1 = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
        double m2 = MathUtil.calcMedian(this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(MarketOrder::getVwap).toArray());
        double ds1Filter = 0.0;
        double ds1Sum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeBuyMap().values()) {
            if (!(marketOrder.getVwap() > m1)) continue;
            if (marketOrder.getAmt() > 50000.0) {
                ds1Filter += marketOrder.getAmt().doubleValue();
            }
            ds1Sum += marketOrder.getAmt().doubleValue();
        }
        double ds2Filter = 0.0;
        double ds2Sum = 0.0;
        for (MarketOrder marketOrder : this.marketDataManager.getLxjjTradeSellMap().values()) {
            if (!(marketOrder.getVwap() > m2)) continue;
            if (marketOrder.getAmt() > 50000.0) {
                ds2Filter += marketOrder.getAmt().doubleValue();
            }
            ds2Sum += marketOrder.getAmt().doubleValue();
        }
        double b = ds1Filter / ds1Sum;
        double a = ds2Filter / ds2Sum;
        double value = 0.55;
        if (a + b != 0.0) {
            value = a / (a + b);
        }
        this.updateValue(0, Double.isNaN(value) || Double.isInfinite(value) ? 0.55 : value);
    }
}


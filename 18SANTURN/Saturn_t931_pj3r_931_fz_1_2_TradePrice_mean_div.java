/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.List;
import java.util.Map;

public class Saturn_t931_pj3r_931_fz_1_2_TradePrice_mean_div
extends BaseFactor {
    public Saturn_t931_pj3r_931_fz_1_2_TradePrice_mean_div(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj3r_931_fz_1_2_TradePrice_mean_div"};
    }

    @Override
    public void calculate() {
        double factorValue = 1.0;
        double zTPrice = this.marketDataManager.getHighPrice();
        List<Fill> fillList = this.marketDataManager.getLxjjFillList();
        long firstZtTime = 0L;
        for (Fill f : fillList) {
            if (f.getPrice() != zTPrice) continue;
            firstZtTime = f.getMdTime();
            break;
        }
        long finalFirstZtTime = firstZtTime;
        double sum1 = 0.0;
        int cnt = 0;
        double sum2 = 0.0;
        for (Fill fill : fillList) {
            if (fill.getMdTime() <= finalFirstZtTime) {
                sum1 += fill.getPrice().doubleValue();
                ++cnt;
                continue;
            }
            sum2 += fill.getPrice().doubleValue();
        }
        double cr1 = sum1 / (double)cnt;
        double cr2 = sum2 / (double)(fillList.size() - cnt);
        if (this.marketDataManager.isStartsWith3()) {
            double preClose = this.marketDataManager.getPreClose();
            factorValue = ((cr1 / preClose - 1.0) / 2.0 + 1.0) / ((cr2 / preClose - 1.0) / 2.0 + 1.0);
        } else {
            factorValue = cr1 / cr2;
        }
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 1.0 : factorValue);
    }
}


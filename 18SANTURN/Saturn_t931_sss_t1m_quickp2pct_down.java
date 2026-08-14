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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Saturn_t931_sss_t1m_quickp2pct_down
extends BaseFactor {
    public Saturn_t931_sss_t1m_quickp2pct_down(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_quickp2pct_down"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> fillList = this.marketDataManager.getFillList();
        double lastPrice = 0.0;
        int priceCnt = 0;
        HashMap<Integer, Double> map = new HashMap<Integer, Double>();
        for (int i = 0; i < fillList.size(); ++i) {
            Fill fill = fillList.get(i);
            if (fill.getMdTime() > 93000000L) {
                if (fill.getPrice() - lastPrice != 0.0) {
                    map.merge(++priceCnt, fill.getPrice() - lastPrice, Double::sum);
                } else if (i == fillList.size() - 1) {
                    map.merge(priceCnt, fill.getPrice() - lastPrice, Double::sum);
                }
            }
            lastPrice = fill.getPrice();
        }
        double sum = 0.0;
        double thrd = -this.marketDataManager.getPreClose().doubleValue() * 0.002 * (double)(this.marketDataManager.isStartsWith3() ? 2 : 1);
        for (Double val : map.values()) {
            if (!(val < thrd)) continue;
            sum += Math.abs(val);
        }
        this.updateValue(0, Double.isNaN(sum) || Double.isInfinite(sum) ? 0.0 : sum);
    }
}


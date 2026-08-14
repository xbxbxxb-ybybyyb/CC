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

public class Saturn_t931_sss_t1m_quickp1num_diff
extends BaseFactor {
    public Saturn_t931_sss_t1m_quickp1num_diff(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_quickp1num_diff"};
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
                    if (i == fillList.size() - 1) {
                        break;
                    }
                } else if (i == fillList.size() - 1) {
                    map.merge(priceCnt, fill.getPrice() - lastPrice, Double::sum);
                }
            }
            lastPrice = fill.getPrice();
        }
        double upCnt = 0.0;
        double downCnt = 0.0;
        double thrd = this.marketDataManager.getPreClose() * 0.001 * (double)(this.marketDataManager.isStartsWith3() ? 2 : 1);
        for (Double val : map.values()) {
            if (val < -thrd) {
                downCnt += 1.0;
            }
            if (!(val > thrd)) continue;
            upCnt += 1.0;
        }
        double sum = upCnt - downCnt;
        this.updateValue(0, Double.isNaN(sum) || Double.isInfinite(sum) ? 0.0 : sum);
    }
}


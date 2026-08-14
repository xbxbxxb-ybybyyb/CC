/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.List;
import java.util.Map;

public class Saturn_t931_sss_t1m_big1p_actbuy
extends BaseFactor {
    public Saturn_t931_sss_t1m_big1p_actbuy(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1m_big1p_actbuy"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<Long, MarketOrder> allTradeBuyMap = this.marketDataManager.getTradeBuyMap();
        double[] amtList = allTradeBuyMap.values().stream().mapToDouble(MarketOrder::getAmt).toArray();
        double threshold = MathUtil.calculateMean(amtList) + MathUtil.calculateStd(amtList);
        List<Fill> allFillList = this.marketDataManager.getFillList();
        double smallBuySum = 0.0;
        double buySum = 0.0;
        for (Fill f : allFillList) {
            if (f.getSellNo() >= f.getBuyNo()) continue;
            if (allTradeBuyMap.get(f.getBuyNo()).getAmt() < threshold) {
                smallBuySum += f.getAmt().doubleValue();
            }
            buySum += f.getAmt().doubleValue();
        }
        double factorValue = smallBuySum / buySum;
        this.updateValue(0, Double.isNaN(factorValue) ? 0.0 : factorValue);
    }
}


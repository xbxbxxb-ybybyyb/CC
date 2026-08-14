/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.OrderInfo;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_cst1_big_bda_rank
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_wd_cst1_big_bda_rank(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_cst1_big_bda_rank"};
        for (Map.Entry<String, Integer> entry : marketDataManager.getSaturnAfterNotUlLenMap().entrySet()) {
            if (entry.getValue() <= 10) continue;
            this.stockSet.add(entry.getKey());
        }
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Map<String, Map<Long, OrderInfo>> buyOrderLxjj = this.marketDataManager.getBuyOrderLxjj();
        Map<String, Map<Long, OrderInfo>> sellOrderLxjj = this.marketDataManager.getSellOrderLxjj();
        ArrayList<Double> pcts = new ArrayList<Double>();
        int index = -1;
        for (String stock : this.stockSet) {
            Map<Long, OrderInfo> buyMap = buyOrderLxjj.get(stock);
            double amtBuySum = 0.0;
            if (buyMap != null && !buyMap.isEmpty()) {
                for (OrderInfo orderInfo : buyMap.values()) {
                    if (!(orderInfo.getAmt() > 200000.0)) continue;
                    amtBuySum += orderInfo.getAmt().doubleValue();
                }
            }
            Map<Long, OrderInfo> sellMap = sellOrderLxjj.get(stock);
            double amtSellSum = 0.0;
            if (sellMap != null && !sellMap.isEmpty()) {
                for (OrderInfo orderInfo : sellMap.values()) {
                    if (!(orderInfo.getAmt() > 200000.0)) continue;
                    amtSellSum += orderInfo.getAmt().doubleValue();
                }
            }
            if (amtSellSum == 0.0) continue;
            double pct = amtBuySum / amtSellSum;
            pcts.add(pct);
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            index = pcts.size() - 1;
        }
        double factorVal = 0.5;
        if (index != -1) {
            List<Double> ranks = MathUtil.calcRankData(pcts, true);
            factorVal = ranks.get(index);
        }
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.5 : factorVal);
    }
}


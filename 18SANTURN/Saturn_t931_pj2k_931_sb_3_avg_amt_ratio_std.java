/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.type.QtyPrice
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.common.type.QtyPrice;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t931_pj2k_931_sb_3_avg_amt_ratio_std
extends BaseFactor {
    public Saturn_t931_pj2k_931_sb_3_avg_amt_ratio_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2k_931_sb_3_avg_amt_ratio_std"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double factorValue = 0.0;
        List<Tick> tickList = this.marketDataManager.getLxjjTickList();
        if (tickList.size() > 0) {
            ArrayList<Double> sbAvgAmtRatioList = new ArrayList<Double>(tickList.size());
            for (Tick tick : tickList) {
                Double buy1Price = tick.getBuyQtyPrice().get(0).getPrice();
                Double sell1Price = tick.getSellQtyPrice().get(0).getPrice();
                if (!(tick.getLastPx() > 0.0) || buy1Price.equals(sell1Price)) continue;
                double buyAmtCum = 0.0;
                double sellAmtCum = 0.0;
                double buyTotOrderNoCum = 0.0;
                double sellTotOrderNoCum = 0.0;
                for (int i = 0; i < 3; ++i) {
                    QtyPrice buyQtyPrice = tick.getBuyQtyPrice().get(i);
                    buyAmtCum += buyQtyPrice.getQuantity() * buyQtyPrice.getPrice();
                    buyTotOrderNoCum += (double)tick.getBuyOrderNum(i).longValue();
                    QtyPrice sellQtyPrice = tick.getSellQtyPrice().get(i);
                    sellAmtCum += sellQtyPrice.getQuantity() * sellQtyPrice.getPrice();
                    sellTotOrderNoCum += (double)tick.getSellOrderNum(i).longValue();
                }
                if (buyTotOrderNoCum == 0.0 || sellTotOrderNoCum == 0.0 || buyAmtCum == 0.0 && sellAmtCum == 0.0) {
                    sbAvgAmtRatioList.add(1.0);
                    continue;
                }
                sbAvgAmtRatioList.add(buyAmtCum / buyTotOrderNoCum / (sellAmtCum / sellTotOrderNoCum));
            }
            factorValue = MathUtil.calculateStd(sbAvgAmtRatioList);
        }
        this.updateValue(0, factorValue);
    }
}


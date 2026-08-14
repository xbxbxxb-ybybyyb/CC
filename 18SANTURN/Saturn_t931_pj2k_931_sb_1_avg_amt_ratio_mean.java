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

public class Saturn_t931_pj2k_931_sb_1_avg_amt_ratio_mean
extends BaseFactor {
    public Saturn_t931_pj2k_931_sb_1_avg_amt_ratio_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2k_931_sb_1_avg_amt_ratio_mean"};
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
                QtyPrice buy1 = tick.getBuyQtyPrice().get(0);
                QtyPrice sell1 = tick.getSellQtyPrice().get(0);
                Double buy1Price = buy1.getPrice();
                Double sell1Price = sell1.getPrice();
                if (!(tick.getLastPx() > 0.0) || buy1Price.equals(sell1Price)) continue;
                double buy1Amt = buy1.getQuantity() * buy1Price;
                double sell1Amt = sell1.getQuantity() * sell1Price;
                double buy1NumOrders = tick.getBuyOrderNum(0).longValue();
                double sell1NumOrders = tick.getSellOrderNum(0).longValue();
                if (buy1NumOrders == 0.0 || sell1NumOrders == 0.0 || buy1Amt == 0.0 && sell1Amt == 0.0) {
                    sbAvgAmtRatioList.add(1.0);
                    continue;
                }
                sbAvgAmtRatioList.add(buy1Amt / buy1NumOrders / (sell1Amt / sell1NumOrders));
            }
            factorValue = MathUtil.calculateMean(sbAvgAmtRatioList);
        }
        this.updateValue(0, factorValue);
    }
}


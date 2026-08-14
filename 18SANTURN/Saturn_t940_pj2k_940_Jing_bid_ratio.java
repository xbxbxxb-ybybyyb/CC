/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Tick;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_pj2k_940_Jing_bid_ratio
extends BaseFactor {
    public Saturn_t940_pj2k_940_Jing_bid_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2k_940_Jing_bid_ratio"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double value = 0.5;
        List<Tick> currentTickList = this.marketDataManager.getCurrentTickList();
        if (currentTickList != null) {
            ArrayList<Double> delta_bid_volume = new ArrayList<Double>();
            ArrayList<Double> delta_trade_volume = new ArrayList<Double>();
            ArrayList<Double> jing_bid_qty = new ArrayList<Double>();
            double totalVolumeTradeMax = Double.NaN;
            for (int i = 0; i < currentTickList.size(); ++i) {
                if (currentTickList.get(i).getLastPx() == 0.0) continue;
                if (Double.isNaN(totalVolumeTradeMax)) {
                    totalVolumeTradeMax = currentTickList.get(i).getTotalVolumeTrade();
                } else if (currentTickList.get(i).getTotalVolumeTrade() > totalVolumeTradeMax) {
                    totalVolumeTradeMax = currentTickList.get(i).getTotalVolumeTrade();
                }
                if (i - 1 < 0) {
                    delta_bid_volume.add(0.0);
                    delta_trade_volume.add(0.0);
                    jing_bid_qty.add(0.0);
                    continue;
                }
                delta_bid_volume.add(currentTickList.get(i).getTotalBidQty() - currentTickList.get(i - 1).getTotalBidQty());
                delta_trade_volume.add(currentTickList.get(i).getTotalVolumeTrade() - currentTickList.get(i - 1).getTotalVolumeTrade());
                jing_bid_qty.add((Double)delta_bid_volume.get(delta_bid_volume.size() - 1) + (Double)delta_trade_volume.get(delta_trade_volume.size() - 1));
            }
            if (jing_bid_qty.size() > 0 && (value = Math.log(MathUtil.calculateSum(jing_bid_qty) / totalVolumeTradeMax)) == 0.0) {
                value = 0.5;
            }
        }
        this.updateValue(0, value);
    }
}


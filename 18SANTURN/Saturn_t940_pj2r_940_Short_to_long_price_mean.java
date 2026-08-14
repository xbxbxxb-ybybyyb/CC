/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_pj2r_940_Short_to_long_price_mean
extends BaseFactor {
    public Saturn_t940_pj2r_940_Short_to_long_price_mean(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Short_to_long_price_mean"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        List<Fill> lxjjFillList = this.marketDataManager.getLxjjFillList();
        double value = 0.0;
        if (lxjjFillList.size() > 0) {
            ArrayList<Double> short_to_long_trades_short = new ArrayList<Double>();
            ArrayList<Double> short_to_long_trades_long = new ArrayList<Double>();
            for (int i = 0; i < lxjjFillList.size(); ++i) {
                if (i + 1 < lxjjFillList.size() && lxjjFillList.get(i).getSide() == Trade.Side.Offer && lxjjFillList.get(i + 1).getSide() == Trade.Side.Bid) {
                    short_to_long_trades_short.add(lxjjFillList.get(i).getPrice());
                }
                if (i - 1 < 0 || lxjjFillList.get(i).getSide() != Trade.Side.Bid || lxjjFillList.get(i - 1).getSide() != Trade.Side.Offer) continue;
                short_to_long_trades_long.add(lxjjFillList.get(i).getPrice());
            }
            double sum = 0.0;
            int count = 0;
            for (int i = 0; i < short_to_long_trades_short.size(); ++i) {
                sum += (Double)short_to_long_trades_long.get(i) - (Double)short_to_long_trades_short.get(i);
                ++count;
            }
            if (count != 0) {
                value = sum / (double)count / this.marketDataManager.getPreClose();
            }
        }
        this.updateValue(0, value);
    }
}


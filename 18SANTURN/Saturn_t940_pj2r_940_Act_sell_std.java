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
import com.huatai.strategy.strong.util.MathUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Saturn_t940_pj2r_940_Act_sell_std
extends BaseFactor {
    public Saturn_t940_pj2r_940_Act_sell_std(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Act_sell_std"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        double preClose = this.marketDataManager.getPreClose();
        List<Fill> fillList = this.marketDataManager.getFillList();
        ArrayList<Double> actSellPxList = new ArrayList<Double>();
        for (Fill f : fillList) {
            if (f.getSide() != Trade.Side.Offer) continue;
            actSellPxList.add(f.getPrice() / preClose - 1.0);
        }
        double value = 0.0;
        if (actSellPxList.size() > 1) {
            value = MathUtil.calculateStd(actSellPxList);
        }
        this.updateValue(0, value);
    }
}


/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t940_pj2r_940_Boosting_trade_ratio
extends BaseFactor {
    private final Set<Long> md_group_MDTime;

    public Saturn_t940_pj2r_940_Boosting_trade_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2r_940_Boosting_trade_ratio"};
        this.updateMode = 2;
        this.md_group_MDTime = new HashSet<Long>();
    }

    @Override
    public void update(Fill fill) {
        long mdTime = fill.getMdTime();
        if (mdTime < 94000000L) {
            this.md_group_MDTime.add(mdTime);
        }
    }

    @Override
    public void calculate() {
        double Boosting_trade_ratio = 0.0;
        if (this.md_group_MDTime.size() > 2) {
            Map<Long, MarketOrder> buyMap = this.marketDataManager.getTradeBuyMap();
            double boosting_trades_qty = 0.0;
            for (MarketOrder mkOrder : buyMap.values()) {
                if (!(mkOrder.getMaxPrice() > mkOrder.getMinPrice()) || !mkOrder.getSideSet().contains(Trade.Side.Bid)) continue;
                boosting_trades_qty += mkOrder.getQty().doubleValue();
            }
            if (this.marketDataManager.getLxjjTotalQty() != 0.0) {
                Boosting_trade_ratio = boosting_trades_qty / this.marketDataManager.getLxjjTotalQty();
            }
        }
        this.updateValue(0, Boosting_trade_ratio);
    }
}


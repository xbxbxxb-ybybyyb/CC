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

public class Saturn_t931_pj2r_931_Boosting_trade_ratio
extends BaseFactor {
    private final Set<Long> mdGroupMDTime;

    public Saturn_t931_pj2r_931_Boosting_trade_ratio(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Boosting_trade_ratio"};
        this.updateMode = 2;
        this.mdGroupMDTime = new HashSet<Long>();
    }

    @Override
    public void update(Fill fill) {
        if (this.mdGroupMDTime.size() <= 2) {
            this.mdGroupMDTime.add(fill.getTimestamp().getTime());
        }
    }

    @Override
    public void calculate() {
        double boostingTradeRatio = 0.0;
        if (this.mdGroupMDTime.size() > 2 && this.marketDataManager.getLxjjTotalQty() != 0.0) {
            double boostingTradesQty = this.marketDataManager.getTradeBuyMap().values().stream().filter(order -> order.getMaxPrice() > order.getMinPrice() && order.getSideSet().contains(Trade.Side.Bid)).mapToDouble(MarketOrder::getQty).sum();
            boostingTradeRatio = boostingTradesQty / this.marketDataManager.getLxjjTotalQty();
        }
        this.updateValue(0, boostingTradeRatio);
    }
}


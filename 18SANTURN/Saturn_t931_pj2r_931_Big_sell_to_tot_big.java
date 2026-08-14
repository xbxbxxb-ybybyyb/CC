/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Saturn_t931_pj2r_931_Big_sell_to_tot_big
extends BaseFactor {
    public Saturn_t931_pj2r_931_Big_sell_to_tot_big(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Big_sell_to_tot_big"};
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        Stream<MarketOrder> buyStream = this.marketDataManager.getLxjjTradeBuyMap().values().stream();
        Stream<MarketOrder> sellStream = this.marketDataManager.getLxjjTradeSellMap().values().stream();
        List<Double> qty = Stream.concat(buyStream, sellStream).map(MarketOrder::getQty).collect(Collectors.toList());
        double bigThred = MathUtil.calculateMean(qty) + MathUtil.calculateStd(qty) * 2.0;
        Double b2tb = this.marketDataManager.getLxjjTradeBuyMap().values().stream().mapToDouble(e -> e.getQty() >= bigThred ? e.getQty() : 0.0).sum();
        Double s2tb = this.marketDataManager.getLxjjTradeSellMap().values().stream().mapToDouble(e -> e.getQty() >= bigThred ? e.getQty() : 0.0).sum();
        double bs2tb = b2tb + s2tb == 0.0 ? 0.0 : s2tb / (s2tb + b2tb);
        this.updateValue(0, Double.isNaN(bs2tb) ? 0.5 : bs2tb);
    }
}


/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Saturn_t940_pj2_lxjj_alt_gamma_bias
extends BaseFactor {
    private final Map<Long, Double> buyOrdersPctChg;
    private final Map<Long, Double> sellOrdersPctChg;
    private double lastPrice;
    private boolean hasJhjjPx;

    public Saturn_t940_pj2_lxjj_alt_gamma_bias(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_pj2_lxjj_alt_gamma_bias"};
        this.updateMode = 1;
        this.lastPrice = 0.0;
        this.buyOrdersPctChg = new HashMap<Long, Double>();
        this.sellOrdersPctChg = new HashMap<Long, Double>();
        this.hasJhjjPx = false;
    }

    @Override
    public void update(Fill fill) {
        long mdTime = this.marketDataManager.getLastFill().getMdTime();
        if (mdTime < 94000000L) {
            if (!this.hasJhjjPx) {
                this.lastPrice = this.marketDataManager.getJhjjPrice();
                this.hasJhjjPx = true;
            }
            double priceDiff = fill.getPrice() - this.lastPrice;
            this.lastPrice = fill.getPrice();
            this.buyOrdersPctChg.merge(fill.getBuyNo(), priceDiff, Double::max);
            this.sellOrdersPctChg.merge(fill.getSellNo(), priceDiff, Double::min);
        }
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getLxjjFillList().size() > 1) {
            TreeMap<Long, MarketOrder> lxjjBuyMap = this.marketDataManager.getLxjjTradeBuyMap();
            TreeMap<Long, MarketOrder> lxjjSellMap = this.marketDataManager.getLxjjTradeSellMap();
            double ff_shares = this.marketDataManager.getFreeFloatCapital();
            value = MathUtil.regressionRes(this.buyOrdersPctChg.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(e -> (Double)e.getValue() * 100.0).collect(Collectors.toList()), lxjjBuyMap.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(e -> ((MarketOrder)e.getValue()).getQty() / ff_shares).collect(Collectors.toList()))[1][0] + MathUtil.regressionRes(this.sellOrdersPctChg.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(e -> (Double)e.getValue() * 100.0).collect(Collectors.toList()), lxjjSellMap.entrySet().stream().sorted(Map.Entry.comparingByKey()).map(e -> ((MarketOrder)e.getValue()).getQty() / ff_shares).collect(Collectors.toList()))[1][0];
        }
        this.updateValue(0, Double.isNaN(value) ? 0.0 : value);
    }
}


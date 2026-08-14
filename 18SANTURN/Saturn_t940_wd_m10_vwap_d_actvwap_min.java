/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade$Side
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashMap;
import java.util.Map;

public class Saturn_t940_wd_m10_vwap_d_actvwap_min
extends BaseFactor {
    private Map<Long, Double> actTradeMoney;
    private Map<Long, Double> actTradeQty;
    private Map<Long, Double> totalTradeMoney;
    private Map<Long, Double> totalTradeQty;

    public Saturn_t940_wd_m10_vwap_d_actvwap_min(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t940_wd_m10_vwap_d_actvwap_min"};
        this.updateMode = 1;
        this.actTradeMoney = new HashMap<Long, Double>();
        this.actTradeQty = new HashMap<Long, Double>();
        this.totalTradeMoney = new HashMap<Long, Double>();
        this.totalTradeQty = new HashMap<Long, Double>();
    }

    @Override
    public void update(Fill fill) {
        long time = fill.getMdTime();
        if (time < 94000000L) {
            long minute = time / 100000L;
            if (fill.getSide() == Trade.Side.Bid) {
                this.actTradeMoney.merge(minute, fill.getAmt(), Double::sum);
                this.actTradeQty.merge(minute, fill.getQty(), Double::sum);
            }
            this.totalTradeMoney.merge(minute, fill.getAmt(), Double::sum);
            this.totalTradeQty.merge(minute, fill.getQty(), Double::sum);
        }
    }

    @Override
    public void calculate() {
        double value = 0.098;
        if (!this.actTradeMoney.isEmpty()) {
            value = Double.MAX_VALUE;
            for (long m : this.actTradeMoney.keySet()) {
                double actVwap;
                double vwap = this.totalTradeMoney.get(m) / this.totalTradeQty.get(m);
                double v = vwap / (actVwap = this.actTradeMoney.get(m) / this.actTradeQty.get(m));
                if (!(v < value)) continue;
                value = v;
            }
        }
        this.updateValue(0, value);
    }
}


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
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_t1_no_act_bda
extends BaseFactor {
    private final Set<Long> buyNoSet = new HashSet<Long>();
    private final Set<Long> sellNoSet = new HashSet<Long>();

    public Saturn_t931_wd_t1_no_act_bda(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_no_act_bda"};
        this.updateMode = 1;
    }

    @Override
    public void update(Fill fill) {
        if (fill.getSide() == Trade.Side.Offer) {
            this.buyNoSet.add(fill.getBuyNo());
            this.sellNoSet.add(fill.getSellNo());
        }
    }

    @Override
    public void calculate() {
        double value = 1.0;
        if (this.sellNoSet.size() != 0) {
            value = (double)this.buyNoSet.size() / (double)this.sellNoSet.size();
        }
        this.updateValue(0, value);
    }
}


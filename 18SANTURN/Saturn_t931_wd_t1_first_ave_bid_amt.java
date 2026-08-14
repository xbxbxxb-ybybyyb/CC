/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_wd_t1_first_ave_bid_amt
extends BaseFactor {
    private final Set<Long> bidBuyNoSet;
    private Double tradeMoney = 0.0;
    private Long firstSecond = null;

    public Saturn_t931_wd_t1_first_ave_bid_amt(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_first_ave_bid_amt"};
        this.updateMode = 1;
        this.bidBuyNoSet = new HashSet<Long>();
    }

    @Override
    public void update(Fill fill) {
        Long second = fill.getMdTime() / 1000L;
        if (this.firstSecond == null || second.equals(this.firstSecond)) {
            this.firstSecond = second;
            this.tradeMoney = this.tradeMoney + fill.getAmt();
            this.bidBuyNoSet.add(fill.getBuyNo());
        }
    }

    @Override
    public void calculate() {
        int bidNum = this.bidBuyNoSet.size();
        double factorValue = bidNum == 0 ? Double.NaN : Math.log(this.tradeMoney / (double)bidNum + 1.0);
        this.updateValue(0, Double.isNaN(factorValue) || Double.isInfinite(factorValue) ? 10.0 : factorValue);
    }
}


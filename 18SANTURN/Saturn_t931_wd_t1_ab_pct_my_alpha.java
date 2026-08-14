/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;

public class Saturn_t931_wd_t1_ab_pct_my_alpha
extends BaseFactor {
    private static final LocalTime End = LocalTime.of(10, 0, 0);
    private final Map<Long, Double> buyNoMaxPriceList;
    private final Map<Long, Double> buyNoMinPriceList;
    private final Map<Long, Double> buyNoFlag;

    public Saturn_t931_wd_t1_ab_pct_my_alpha(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_ab_pct_my_alpha"};
        this.buyNoMaxPriceList = new HashMap<Long, Double>();
        this.buyNoMinPriceList = new HashMap<Long, Double>();
        this.buyNoFlag = new HashMap<Long, Double>();
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        for (Fill fill : this.marketDataManager.getLxjjFillList()) {
            LocalTime tmp = TimeUtil.UDateToLocalTime(fill.getTimestamp());
            if (tmp.compareTo(End) > 0) continue;
            this.buyNoMinPriceList.merge(fill.getBuyNo(), fill.getPrice(), (oldVal, newVal) -> newVal < oldVal ? newVal : oldVal);
            this.buyNoMaxPriceList.merge(fill.getBuyNo(), fill.getPrice(), (oldVal, newVal) -> newVal > oldVal ? newVal : oldVal);
            this.buyNoFlag.merge(fill.getBuyNo(), fill.getBuyNo() > fill.getSellNo() ? 1.0 : 0.0, Double::sum);
        }
        Map<Long, MarketOrder> tradeBuyMap = this.marketDataManager.getTradeBuyMap();
        LinkedList<Double> x = new LinkedList<Double>();
        LinkedList<Double> y = new LinkedList<Double>();
        for (long t : this.buyNoFlag.keySet()) {
            if (!(this.buyNoFlag.get(t) > 0.0)) continue;
            double tmp_x = this.buyNoMaxPriceList.get(t) / this.buyNoMinPriceList.get(t) - 1.0;
            double tmp_y = tradeBuyMap.get(t).getAmt();
            if (Double.isNaN(tmp_x) || Double.isNaN(tmp_y)) continue;
            x.add(tmp_x);
            y.add(tmp_y);
        }
        double factorValue = MathUtil.calculateStd(x) == 0.0 || MathUtil.calculateStd(y) == 0.0 || x.size() < 3 ? Double.NaN : MathUtil.regressionRes(y, x)[0][0];
        this.updateValue(0, Double.isNaN(factorValue /= 10000.0) ? 2.36 : factorValue);
    }
}


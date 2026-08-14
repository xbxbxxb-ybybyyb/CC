/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 *  com.huatai.common.marketdata.Trade$Type
 *  org.apache.commons.lang3.tuple.MutablePair
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.TimeUtil;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.lang3.tuple.MutablePair;

public class Saturn_t931_pj2r_931_Convexity
extends BaseFactor {
    private final Map<Long, MutablePair<Double, Double>> timeInfoMap;
    private Date endTradeTime;

    public Saturn_t931_pj2r_931_Convexity(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_pj2r_931_Convexity"};
        this.updateMode = 3;
        this.timeInfoMap = new HashMap<Long, MutablePair<Double, Double>>();
    }

    @Override
    public void update(Trade trade) {
        Fill fill;
        if (trade.getType() == Trade.Type.Filled && trade.getPrice() > 0.0 && !(fill = this.marketDataManager.getLastFill()).isInJhjjPeriod()) {
            MutablePair timeInfo = this.timeInfoMap.computeIfAbsent(fill.getMdTime(), k -> MutablePair.of((Object)TimeUtil.calTimeDeltaWithMarketOpen(fill.getLocalTime()), (Object)trade.getPrice()));
            timeInfo.right = trade.getPrice();
        }
        this.endTradeTime = trade.getTimestamp();
    }

    @Override
    public void calculate() {
        double value = 0.0;
        if (this.marketDataManager.getLxjjFillList().size() > 1) {
            double jhjjPrice = this.marketDataManager.getJhjjPrice();
            double endTimeDelta = TimeUtil.calTimeDeltaWithMarketOpen(TimeUtil.UDateToLocalTime(this.endTradeTime));
            double totSlope = (this.marketDataManager.getLastFill().getPrice() - jhjjPrice) / endTimeDelta;
            value = this.timeInfoMap.values().stream().mapToDouble(pair -> (((Double)pair.left * totSlope + jhjjPrice) / (Double)pair.right - 1.0) * 100.0).max().orElse(0.0);
        }
        this.updateValue(0, value);
    }
}


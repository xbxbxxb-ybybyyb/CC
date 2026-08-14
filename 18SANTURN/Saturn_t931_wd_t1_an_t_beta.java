/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.Fill;
import com.huatai.strategy.strong.common.marketdata.MarketOrder;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.factor2.MarketOrderInfo;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Saturn_t931_wd_t1_an_t_beta
extends BaseFactor {
    private static final LocalTime End = LocalTime.of(10, 0, 0);
    private final Map<Long, MarketOrderInfo> lxjjTradeSellMap;

    public Saturn_t931_wd_t1_an_t_beta(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_wd_t1_an_t_beta"};
        this.updateMode = 1;
        this.lxjjTradeSellMap = new HashMap<Long, MarketOrderInfo>();
    }

    @Override
    public void update(Fill fill) {
        if (fill.getLocalTime().compareTo(End) <= 0) {
            Long sellNo = fill.getSellNo();
            MarketOrder sellOrder = this.marketDataManager.getLxjjTradeSellMap().get(sellNo);
            if (sellOrder != null) {
                MarketOrderInfo orderInfo = this.lxjjTradeSellMap.computeIfAbsent(sellNo, k -> new MarketOrderInfo());
                orderInfo.setMarketInfo(sellNo, sellOrder.getPrice(), sellOrder.getFillList().size(), sellOrder.getFirstFillMdTime());
            }
        }
    }

    @Override
    public void calculate() {
        List marketOrderList = this.lxjjTradeSellMap.values().stream().sorted(Comparator.comparing(MarketOrderInfo::getPrice, Comparator.reverseOrder()).thenComparing(MarketOrderInfo::getNo, Comparator.reverseOrder())).limit(50L).collect(Collectors.toList());
        LinkedList<Double> x = new LinkedList<Double>();
        LinkedList<Double> y = new LinkedList<Double>();
        for (MarketOrderInfo marketOrder : marketOrderList) {
            x.add(Double.valueOf(marketOrder.getFillListSize()));
            y.add(Double.valueOf(TimeUtil.calTimeDelta(93000000L, (long)marketOrder.getFirstFillMdTime())));
        }
        double factorValue = MathUtil.calculateStd(x) == 0.0 || MathUtil.calculateStd(y) == 0.0 || x.size() < 3 ? Double.NaN : MathUtil.regressionResWithoutIntercept(y, x)[0][0];
        this.updateValue(0, Double.isNaN(factorValue /= 10000.0) ? 0.5 : factorValue);
    }
}


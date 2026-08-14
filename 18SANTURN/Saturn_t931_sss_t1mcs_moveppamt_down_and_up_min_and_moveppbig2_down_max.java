/*
 * Decompiled with CFR 0.151.
 * 
 * Could not load the following classes:
 *  com.huatai.common.marketdata.Trade
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.common.marketdata.Trade;
import com.huatai.strategy.strong.factor2.BaseFactor;
import com.huatai.strategy.strong.saturn.SaturnMarketDataManager;
import com.huatai.strategy.strong.util.MathUtil;
import com.huatai.strategy.strong.util.TimeUtil;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class Saturn_t931_sss_t1mcs_moveppamt_down_and_up_min_and_moveppbig2_down_max
extends BaseFactor {
    private Set<String> stockSet = new HashSet<String>();

    public Saturn_t931_sss_t1mcs_moveppamt_down_and_up_min_and_moveppbig2_down_max(SaturnMarketDataManager marketDataManager, Map<String, Double> factorValueMap) {
        super(marketDataManager, factorValueMap);
        this.factorName = new String[]{"saturn_t931_sss_t1mcs_moveppamt_down_min", "saturn_t931_sss_t1mcs_moveppamt_up_min", "saturn_t931_sss_t1mcs_moveppbig2_down_max"};
        for (Map.Entry<String, Integer> entry : marketDataManager.getSaturnAfterNotUlLenMap().entrySet()) {
            if (entry.getValue() <= 10) continue;
            this.stockSet.add(entry.getKey());
        }
    }

    @Override
    public void update(Trade trade) {
    }

    @Override
    public void calculate() {
        LocalTime localTime = LocalTime.of(9, 30);
        double currFactor1 = Double.NaN;
        double min1 = Double.POSITIVE_INFINITY;
        double currFactor2 = Double.NaN;
        double min2 = Double.POSITIVE_INFINITY;
        double currFactor3 = Double.NaN;
        double max = Double.NEGATIVE_INFINITY;
        for (String stock : this.stockSet) {
            HashMap<Integer, DiffInfo> diff = new HashMap<Integer, DiffInfo>();
            TradeInfo now = null;
            double lastPrice = Double.NaN;
            for (Trade trade : this.marketDataManager.getCsTradeMap().get(stock)) {
                if (trade.getTurnover() > 0.0 && TimeUtil.UDateToLocalTime(trade.getTimestamp()).isAfter(localTime)) {
                    TradeInfo nowTrade;
                    now = nowTrade = new TradeInfo(now, trade, lastPrice);
                    if (diff.containsKey(nowTrade.priceCnt)) {
                        ((DiffInfo)diff.get(nowTrade.priceCnt)).update(trade.getTurnover(), nowTrade.diff);
                    } else {
                        diff.put(nowTrade.priceCnt, new DiffInfo(trade.getTurnover(), nowTrade.diff));
                    }
                }
                if (!(trade.getTurnover() > 0.0)) continue;
                lastPrice = trade.getPrice();
            }
            if (diff.isEmpty()) continue;
            double preClose = this.marketDataManager.getPreClosePxMap().get(stock);
            double last = Double.NaN;
            double diff_sum = 0.0;
            double amt_sum = 0.0;
            double moveDownAmtSum = 0.0;
            double moveDownDiffSum = 0.0;
            double moveUpAmtSum = 0.0;
            double moveUpDiffSum = 0.0;
            ArrayList<Double> amtList = new ArrayList<Double>();
            ArrayList<Double> diffList = new ArrayList<Double>();
            for (DiffInfo diffInfo : diff.values()) {
                if (diffInfo.diff_sum * last < 0.0) {
                    if (diff_sum < 0.0) {
                        moveDownAmtSum += amt_sum;
                        moveDownDiffSum += Math.abs(diff_sum);
                    } else if (diff_sum > 0.0) {
                        moveUpAmtSum += amt_sum;
                        moveUpDiffSum += Math.abs(diff_sum);
                    }
                    amtList.add(amt_sum);
                    diffList.add(diff_sum);
                    diff_sum = diffInfo.diff_sum;
                    amt_sum = diffInfo.amt_sum;
                } else {
                    diff_sum += diffInfo.diff_sum;
                    amt_sum += diffInfo.amt_sum;
                }
                last = diffInfo.diff_sum;
            }
            if (diff_sum < 0.0) {
                moveDownAmtSum += amt_sum;
                moveDownDiffSum += Math.abs(diff_sum);
            } else if (diff_sum > 0.0) {
                moveUpAmtSum += amt_sum;
                moveUpDiffSum += Math.abs(diff_sum);
            }
            amtList.add(amt_sum);
            diffList.add(diff_sum);
            double factor = moveDownAmtSum / moveDownDiffSum * preClose;
            double factor2 = moveUpAmtSum / moveUpDiffSum * preClose;
            double thrd = MathUtil.calculateMean(amtList) + 2.0 * MathUtil.calculateStd(amtList);
            double factor3 = 0.0;
            for (int i = 0; i < amtList.size(); ++i) {
                if (!((Double)amtList.get(i) > thrd) || !((Double)diffList.get(i) < 0.0)) continue;
                factor3 += ((Double)diffList.get(i)).doubleValue();
            }
            factor3 /= preClose;
            if (stock.startsWith("3")) {
                factor *= 2.0;
                factor2 *= 2.0;
                factor3 /= 2.0;
            }
            if (factor < min1) {
                min1 = factor;
            }
            if (factor2 < min2) {
                min2 = factor2;
            }
            if (factor3 > max) {
                max = factor3;
            }
            if (!stock.equals(this.marketDataManager.getSymbol())) continue;
            currFactor1 = factor;
            currFactor2 = factor2;
            currFactor3 = factor3;
        }
        double factorVal = currFactor1 - min1;
        this.updateValue(0, Double.isNaN(factorVal) || Double.isInfinite(factorVal) ? 0.0 : factorVal);
        double factorVal2 = currFactor2 - min2;
        this.updateValue(1, Double.isNaN(factorVal2) || Double.isInfinite(factorVal2) ? 0.0 : factorVal2);
        double factorVal3 = currFactor3 - max;
        this.updateValue(2, Double.isNaN(factorVal3) || Double.isInfinite(factorVal3) ? 0.0 : factorVal3);
    }

    class DiffInfo {
        public double amt_sum;
        public double diff_sum;

        public DiffInfo(double amt, double diff) {
            this.amt_sum = amt;
            this.diff_sum = diff;
        }

        public void update(double amt, double diff) {
            this.amt_sum += amt;
            this.diff_sum += diff;
        }
    }

    class TradeInfo {
        public double price;
        public double diff;
        public int priceCnt;

        public TradeInfo(TradeInfo tradeInfo, Trade trade, double lastPrice) {
            if (tradeInfo == null) {
                this.diff = trade.getPrice() - lastPrice;
                this.priceCnt = this.diff == 0.0 ? 0 : 1;
                this.price = trade.getPrice();
            } else {
                this.diff = trade.getPrice() - tradeInfo.price;
                this.priceCnt = this.diff == 0.0 ? tradeInfo.priceCnt : tradeInfo.priceCnt + 1;
                this.price = trade.getPrice();
            }
        }
    }
}


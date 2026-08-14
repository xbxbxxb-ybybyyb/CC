/*
 * Decompiled with CFR 0.151.
 */
package com.huatai.strategy.strong.factor2;

import com.huatai.strategy.strong.common.marketdata.MarketOrder;

class MarketOrderInfo
implements Comparable<MarketOrder> {
    private Long no;
    private Double price;
    private int fillListSize;
    private double firstFillMdTime;

    public void setMarketInfo(Long no, Double price, int fillListSize, double firstFillMdTime) {
        this.no = no;
        this.price = price;
        this.fillListSize = fillListSize;
        this.firstFillMdTime = firstFillMdTime;
    }

    @Override
    public int compareTo(MarketOrder order) {
        int ret = this.price.compareTo(order.getPrice());
        return -(ret == 0 ? Long.compare(this.no, order.getNo()) : ret);
    }

    public Long getNo() {
        return this.no;
    }

    public Double getPrice() {
        return this.price;
    }

    public int getFillListSize() {
        return this.fillListSize;
    }

    public double getFirstFillMdTime() {
        return this.firstFillMdTime;
    }
}


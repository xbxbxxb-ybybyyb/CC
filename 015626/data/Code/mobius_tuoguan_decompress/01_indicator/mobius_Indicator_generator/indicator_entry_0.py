import os
import sys
from datetime import date

from daily_indicator_generator import *
from generate_history_indicator_for_new_stocks import *

from common.notice import *
lm = LinkMessage()
def LogAndSendMessageInfo(msg):
    logger.info(msg)
    lm.sendMessage(msg)
def LogAndSendMessageError(msg):
    logger.error(msg)
    lm.sendMessage(msg)


if __name__ == '__main__':
    today = date.today().strftime("%Y%m%d")

    today = '20250317'
    minute_shift = 0

    LogAndSendMessageInfo(f"[Mobius截面] {today} offset_{minute_shift} Indicator Entry")
    time_start = time.time()
    generate_daily_indicator(today, minute_shift)

    check_and_generate_indicator_for_index_stock_change(today, minute_shift)

    pre_run(today, minute_shift)
    time_end = time.time()
    LogAndSendMessageInfo(f"[Mobius截面] {today} offset_{minute_shift} Indicator End, time_cost={round((time_end - time_start) / 60, 1)} min")






def view_bar(num, tot, s):
    # 进度条函数
    import sys
    rate = (num + 1) / tot
    rate_num = (int(rate * 100))
    n = rate_num // 3
    r = '\r[%s>%s]%d%%-%s' % ('=' * n, '-' * (33 - n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')

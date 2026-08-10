divdf = IO.read_data([20170101,20230101], alt = '/data/user/015626/data/share/IndexDividends/details/IndexDividends_Details.h5')
md = IO.read_data([20170101,20230101], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5')

rdf = []
for future in ['IC','IF','IH','IM']:
    for year in range(17,23):
        t06 = md.xs(f'IC{year}06.CFE', level = 1).index[-1]
        t09 = md.xs(f'IC{year}09.CFE', level = 1).index[-1]
        divpoint = divdf.xs(f'{future}.CFE', level = 1)['divpoint']
        fake_06_enddate = pd.to_datetime(f'20{year}0616')
        fake_09_enddate = pd.to_datetime(f'20{year}0915')
        columns = ['year','future','real_06_enddate','real_09_enddate','real_div_point','fake_06_enddate', 'fake_09_enddate']
        values = [year, future, t06, t09, divpoint.loc[udt.get_trading_day_offset(t06, 1)[0]:t09].sum(), fake_06_enddate, fake_09_enddate]
        for i in range(-3, 4):
            columns.append(f'fake_t{i}')
            values.append(divpoint.loc[udt.get_trading_day_offset(fake_06_enddate, i)[0]:fake_09_enddate].sum())
        rdf.append(pd.DataFrame(values, index = columns).T)

result = pd.concat(rdf)

result.to_csv('/data/user/015626/data/share/IndexDividends/details/real_div_17_22.csv', index = False)
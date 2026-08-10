import datetime
from multifactor.data.utils import *
import pyodbc

root = 'A:\\weiyc\\data\\Reuters\\CSV\\TRE\\'

conn = pyodbc.connect(driver='{SQL Server}', server='qai97-qadirectcloud-default-0j.database.windows.net',
                      database='qai', uid='0j.sujian.zhi', pwd='j#Bd5kDQzYMouvcO')
cursor = conn.cursor()
# 待完成'TREDetNotesPer', 2012-11 ,  'TREDetConfPer','TRESmartDetPer'，'TRESmartSumPer',2016-03 'TRESumHzn',2018-04,'TRESumPer',2014-02
# 已经完成'TREActChg', 'TREActSurpWin', 'TREDetConfAper', 'TREDetConfHzn','TREDetNotesAper','TREDetNotesHzn','TREDetRestr', 'TREInfo', 'TREOrgNotesAper', 'TREOrgNotesHzn',
# 'TREOrgNotesPer', 'TREPerAdvance', 'TREPerIndex', 'TRERecDetConf', 'TRERecSum', 'TRESmartClusterPer','TRESumAper',
# activationdate_tables = ['TREDetPer']

# effectivedate_tables = []

for table in effectivedate_tables:
    print(table)
    table_csv_path = root + table
    if not os.path.exists(table_csv_path):
        os.makedirs(table_csv_path)
    if table == 'TREDetPer':
        start_month = '2008-01'
    elif table == 'TRESmartDetPer':
        start_month = '2018-08'
    elif table == 'TREDetNotesPer':
        start_month = '2012-11'
    elif table == 'TRESmartSumPer':
        start_month = '2016-03'
    elif table == 'TRESumHzn':
        start_month = '2018-07'
    elif table == 'TRESumPer':
        start_month = '2017-06'
    monthdate_list = pd.date_range(start_month, '2019-11', freq='M')
    for monthdate in monthdate_list:

        # sql = 'SELECT * FROM [dbo].[' + table + '] where AnnounceDate like \'' + date.strftime('%Y-%m-%d') + '%\''
        sql = 'select C.Ticker, C.DsQtName, C.IBESTicker, A.* from ' + table + ' A join TREInfo B on A.EstPermID = B.EstPermID and B.CtryPermID = 100064 join ChinaAShareIBESCodes C on A.EstPermID = C.EstPermID where A.ActivationDate like \'' + monthdate.strftime('%Y-%m') + '%\''

        print(table,monthdate)
        cursor.execute(sql)
        rs = cursor.fetchall()
        if(len(rs) == 0):
            continue

        content_list = []
        for content in rs:
            content_list.append(list(content))

        df = pd.DataFrame(content_list)

        info = cursor.description
        column_names = []
        for i in range(len(info)):
            column_names.append(info[i][0])
        df.columns = column_names

        df['newActivationDate'] = df['ActivationDate'].apply(lambda x:datetime.datetime.strptime(x[:10],'%Y-%m-%d').strftime('%Y%m%d'))
        date_list = df.newActivationDate.unique().tolist()
        for date in date_list:
            print(table, date)
            newdf = df[df.newActivationDate == date]
            newdf = newdf.drop(['newActivationDate'], axis=1)
            newdf.to_csv(os.path.join(table_csv_path, date + '.csv'), encoding='utf-8')
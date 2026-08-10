import datetime
from multifactor.data.utils import *
import pyodbc

root = 'A:\\weiyc\\data\\Reuters\\CSV\\effectivedate\\'

conn = pyodbc.connect(driver='{SQL Server}', server='qai97-qadirectcloud-default-0j.database.windows.net',
                      database='qai', uid='0j.sujian.zhi', pwd='j#Bd5kDQzYMouvcO')
cursor = conn.cursor()
# 待完成, 'TRESumPer'201508
# 已经完成'TREActChg','TREActSurpWin','TREDetConfAper', 'TREDetConfHzn','TREDetNotesAper',
#                          'TREDetNotesHzn','TREDetRestr', 'TREInfo', 'TREOrgNotesAper', 'TREOrgNotesHzn',
# 'TREOrgNotesPer', 'TREPerAdvance', 'TREPerIndex', 'TRERecDetConf', 'TRERecSum','TRESmartClusterPer','TRESumAper',
#                          'TREDetNotesPer','TRESumHzn',
# activationdate_tables = []

effectivedate_tables = ['TRESmartDetPer','TRESmartSumPer']

for table in activationdate_tables:
    print(table)
    table_csv_path = root + table
    if not os.path.exists(table_csv_path):
        os.makedirs(table_csv_path)
    # sql = "SELECT min(Announcedate) FROM [dbo].[" + table + "]"
    sql = "select min(A.ActivationDate) from " + table + " A join ChinaAShareIBESCodes C on A.EstPermID = C.EstPermID"
    cursor.execute(sql)
    rs = cursor.fetchall()
    if rs[0][0] == None:
        none_dir_path = table_csv_path + '\\None'
        if not os.path.exists(none_dir_path):
            os.makedirs(none_dir_path)
        continue
    monthdate_list = pd.date_range(rs[0][0][:7], '2019-11', freq='M')
    for monthdate in monthdate_list:

        # sql = 'SELECT * FROM [dbo].[' + table + '] where AnnounceDate like \'' + date.strftime('%Y-%m-%d') + '%\''
        sql = 'select C.Ticker, C.DsQtName, C.IBESTicker, A.* from ' + table + ' A join ChinaAShareIBESCodes C on A.EstPermID = C.EstPermID where A.ActivationDate like \'' + monthdate.strftime('%Y-%m') + '%\''

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


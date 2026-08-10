import datetime
from multifactor.data.utils import *
import pyodbc
import time

root = 'A:\\weiyc\\data\\Reuters\\CSV\\TRE\\'

conn = pyodbc.connect(driver='{SQL Server}', server='qai97-qadirectcloud-default-0j.database.windows.net',
                      database='qai', uid='0j.sujian.zhi', pwd='j#Bd5kDQzYMouvcO')
cursor = conn.cursor()


date = "'2018-1-2'"
stock = "'600056'"
estpermid = '30064771379'

sql = '''
DECLARE @DATE AS DATE
SET @DATE= ''' + date + '''
DECLARE @ESTPERMID AS BIGINT
SET @ESTPERMID=''' + estpermid + '''
DECLARE @TICKER AS VARCHAR(10)
SET @TICKER=''' + stock + '''

SELECT 
  @DATE AS DATE_, 
  @TICKER AS TICKER, 
  S.* 
FROM 
  TRESmartSumPer S 
  JOIN TREPerAdvance A ON A.EstPermID = S.EstPermID 
  AND @DATE BETWEEN A.EffectiveDate AND ISNULL(A.ExpireDate,'2079-1-1')
  AND S.PerType = A.PerType 
  AND A.Periodicity = 3 
  AND S.PerEndDate > A.PerEndDate 
WHERE 
  S.EstPermID = @ESTPERMID 
  AND @DATE BETWEEN S.EFFECTIVEDATE 
  AND ISNULL(S.EXPIREDATE, '2079-1-1')
'''

start_time = time.time()
cursor.execute(sql)

rs = cursor.fetchall()

content_list = []
for content in rs:
    content_list.append(list(content))

df = pd.DataFrame(content_list)

info = cursor.description
column_names = []
for i in range(len(info)):
    column_names.append(info[i][0])
df.columns = column_names
print(df)
print('time taken:', time.time() - start_time)





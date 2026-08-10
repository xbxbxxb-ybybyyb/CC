from multifactor.data.utils import *
#SELECT top 1 * FROM [dbo].[TREActRpt] order by AnnounceDate asc
start_date, end_date, cdate_list = check_update_date(19000101,20191015)
print(start_date)
print(len(cdate_list))



tables = ['TREAnalysts',
 'TREBrokers',
 'TRECode',
 'TRECode2',
 'TRECoverage']

TREActChg [(1554230, )]
TREActGoFwd [(51320, )]
TREActRpt [(24996322, )]
TREActRst [(33586, )]
TREActSurpWin [(37819829, )]
TREAnalysts [(172020, )]
TREBrokers [(5322, )]
TRECode [(2819, )]
TRECode2 [(2791, )]
TRECoverage [(1947991, )]
TREDetAper [(2632331, )]
TREDetConfAper [(2652189, )]
TREDetConfHzn [(0, )]
TREDetConfPer [(523957817, )]
TREDetHzn [(5365200, )]
TREDetNotesAper [(370655, )]
TREDetNotesHzn [(49098, )]
TREDetNotesPer [(62065886, )]
TREDetPer [(552671546, )]
TREDetRestr [(13845, )]
TREInfo [(106749, )]
TREOrgNotesAper [(0, )]
TREOrgNotesHzn [(0, )]
TREOrgNotesPer [(952392, )]
TREPerAdvance [(3235070, )]
TREPerIndex [(3903840, )]
TRERecDet [(2835153, )]
TRERecDetConf [(7779968, )]
TRERecSum [(3725651, )]
TRESmartClusterPer [(21546774, )]
[TRESmartDetPer] 行数太多，int存不下
TRESmartSumPer [(387778787, )]
TRESumAper [(2303643, )]
TRESumHzn [(5734230, )]
TRESumPer [(560639381, )]
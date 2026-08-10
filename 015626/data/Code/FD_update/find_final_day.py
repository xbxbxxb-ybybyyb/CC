import datetime as dt
import pandas as pd
import os
import numpy as np
from multifactor.IO import IO

#
daily_list =  ['WIND_ASharePledgeproportion', 'WIND_AShareFreeFloatCalendar',
                     'WIND_ChinaMutualFundAssetPortfolio', 'WIND_CMFOtherPortfolio', 'WIND_ChinaMutualFundIndPortfolio','WIND_ChinaMutualFundStockPortfolio',
                     'WIND_ChinaMutualFundBondPortfolio', 'WIND_AShareMarginSubject','WIND_AShareBlockTrade', 
                     'WIND_AShareStrangeTradedetail', 'WIND_AShareStrangeTrade', 'WIND_AShareHolderNumber', 'WIND_AShareFloatHolder',
                      'WIND_AShareInsiderTrade', 'WIND_AShareMajorHolderPlanHold', 'WIND_AShareinstHolderDerData', 
                      'WIND_CMMFPortfolioPTM','WIND_AShareIndustriesCode']
                    
new_daily_list = ['WIND_AShareCapitalization','WIND_AShareFreeFloat', 'WIND_AShareIPO', 'WIND_AShareAgency',
            'WIND_AShareCOCapitaloperation', 'WIND_AshareStockRepo', 'WIND_AShareCorporateFinance', 'WIND_AShareIssueCommAudit',
            'WIND_AShareEquityDivision', 'WIND_AShareStaff', 'WIND_IPOCompRFA', 
            'WIND_IECMemberList', 'WIND_AShareLeadUnderwriter', 'WIND_AShareRightIssue',
            'WIND_AShareSEO', 'WIND_AShareEXRightDividendRecord', 'WIND_AShareCompRestricted', 'WIND_ASharePlacementDetails', 
            'WIND_ASharePlacementInfo', 'WIND_IPOInquiryDetails', 'WIND_AShareIncDescription',
            'WIND_AShareIncQuantityPrice', 'WIND_AShareIncQuantityDetails','WIND_AShareIncExercisePct', 'WIND_AShareIncExecQtyPri',
            'WIND_AShareEsopDescription','WIND_AShareEsopTradingInfo', 'WIND_AShareStaffStructure','WIND_AShareEquityPledgeInfo',
             'WIND_AShareInsideHolder', 'WIND_htzqedbdzzbs','WIND_AIndexIndustriesEODCITICS','WIND_SIndexPerformance','WIND_BOIndexWeightsWIND',
             'WIND_AShareStyleCoefficient','WIND_AShareMjrHolderTrade','WIND_AShareTypeCode','WIND_AShareTradingSuspension','WIND_AShareMainandnoteitems','WIND_AIndexWindIndustriesEOD','WIND_AShareIllegality','WIND_AShareMajorEvent',
             'WIND_ASarePlanTrade']

tech_daily_list = [ 'WIND_AShareTechIndicators', 'WIND_AshareintensitytrendADJ', 'WIND_AShareEnergyindexADJ','WIND_AShareswingReversetrendADJ']

qtr_list = ['WIND_FinNotesDetail','WIND_AShareIBrokerIndicator',
            'WIND_AShareInsuranceIndicator','WIND_AShareBankIndicator',
            'WIND_Top5ByLongTermBorrowing','WIND_AshareOtherreceivables','WIND_AShareFinancialExpense',
            'WIND_AshareInventorydetails','WIND_AshareFinancialaccounts','WIND_Top5ByAccountsReceivable','WIND_AShareAuditOpinion',
            'WIND_AShareSalesSegment','WIND_Top5ByOperatingIncome']
           #daily_list + new_daily_list +  tech_daily_list
table_dict = {'DAILY':daily_list + new_daily_list +  tech_daily_list, 'QUARTERLY': qtr_list}

for table_type in table_dict:
    for table_name in table_dict[table_type]:
        name = table_name[5:]
        path = '/data/group/800080/warehouse/prod/DATABASE/WIND/' + name + '/'
        if os.path.exists(path):
            print(name, path)
                # os.remove(path + name + '.h5')
                # os.rmdir(path)
        
            
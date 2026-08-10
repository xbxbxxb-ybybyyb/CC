import pandas as pd
import os

std_in_dict_shf = {'AG.SHF':0.02,'AL.SHF':0.02,'AO.SHF':0.03,'AU.SHF':0.01,
               'BR.SHF':0,'BU.SHF':0,'CU.SHF':0.02,'FU.SHF':0,'HC.SHF':0.02,'NI.SHF':0.02,
               'PB.SHF':0,'RB.SHF':0.02,'RU.SHF':0.01,'SN.SHF': 0.02,'SP.SHF':0.02, 'SS.SHF':0,           
               'ZN.SHF':0.015}
std_in_dict_dce = {'A.DCE':0.01,'B.DCE':0.01,'C.DCE':0.02,'CS.DCE':0.02,'EB.DCE':0.03,'EG.DCE':0.03,'I.DCE':0.03,'JM.DCE':0.02,'J.DCE':0.02,'JD.DCE':0.02,
                   'L.DCE':0.015,'LH.DCE':0.025,'M.DCE':0.015,'P.DCE':0.03,'PG.DCE':0,'PP.DCE':0,'V.DCE':0.02,'Y.DCE':0.02}
std_in_dict_czc = {'AP.ZCE':0.02,'CF.ZCE':0.02,'CJ.ZCE':0.02,'FG.ZCE':0.02,'MA.ZCE':0.02,'OI.ZCE':0.02,'PF.ZCE':0,
                  'PK.ZCE':0,'PX.ZCE':0.02,'RM.ZCE':0.02,'SA.ZCE':0.02,'SF.ZCE':0,'SH.ZCE':0.02,'SM.ZCE':0.02,'SR.ZCE':0.01,
                  'TA.ZCE':0.02,'UR.ZCE':0.02}
std_in_dict_gfe = {'LC.GFE':0.02,'SI.GFE':0.02,'PS.GFE': 0.02}
std_in_dict_ine = {'NR.INE':0.01,'EC.INE': 0.04,'BC.INE': 0.02,'LU.INE':0.02,'SC.INE':0.02}
std_in_dict_cfe = {'IF.CFE':0.01,'IC.CFE': 0.01,'IH.CFE': 0.01,'IM.CFE':0.01,
                   'T.CFE':0.0015,'TL.CFE':0.003,'TF.CFE':0.001,'TS.CFE':0.0005}
#std_in_dict_shf = {'AG.SHF':0.02,'AL.SHF':0.02,'AO.SHF':0.02,'AU.SHF':0.01,
#               'BR.SHF':0,'BU.SHF':0,'CU.SHF':0.02,'FU.SHF':0,'HC.SHF':0.02,'NI.SHF':0.02,
#               'PB.SHF':0,'RB.SHF':0.02,'RU.SHF':0.02,'SN.SHF': 0.02,'SP.SHF':0.02, 'SS.SHF':0,           
#               'ZN.SHF':0.02}
#std_in_dict_dce = {'A.DCE':0.02,'B.DCE':0.02,'C.DCE':0.02,'CS.DCE':0.02,'EB.DCE':0.02,'EG.DCE':0.02,'I.DCE':0.02,'JM.DCE':0.02,'J.DCE':0.02,
#                   'JD.DCE':0.02,'L.DCE':0.02,'LH.DCE':0.02,'M.DCE':0.02,'P.DCE':0.02,'PG.DCE':0,'PP.DCE':0,'V.DCE':0.02,'Y.DCE':0.02}
#std_in_dict_czc = {'AP.ZCE':0.02,'CF.ZCE':0.02,'CJ.ZCE':0.02,'FG.ZCE':0.02,'MA.ZCE':0.02,'OI.ZCE':0.02,'PF.ZCE':0,
#                  'PK.ZCE':0,'PX.ZCE':0.02,'RM.ZCE':0.02,'SA.ZCE':0.02,'SF.ZCE':0,'SH.ZCE':0.02,'SM.ZCE':0.02,'SR.ZCE':0.02,
#                  'TA.ZCE':0.02,'UR.ZCE':0.02}
#std_in_dict_gfe = {'LC.GFE':0.02,'SI.GFE':0.02,'PS.GFE': 0.02}
#std_in_dict_ine = {'NR.INE':0.02,'EC.INE': 0.04,'BC.INE': 0.02,'LU.INE':0.02,'SC.INE':0.02}

std_in_dict = {**std_in_dict_shf,**std_in_dict_dce,**std_in_dict_czc,**std_in_dict_gfe,**std_in_dict_ine,**std_in_dict_cfe}

std_out_dict_shf = {'AG.SHF':1,'AL.SHF':0.02,'AO.SHF':0.03,'AU.SHF':0.03,
               'BR.SHF':0.2,'BU.SHF':1,'CU.SHF':0.02,'FU.SHF':1,'HC.SHF':0.02,'NI.SHF':0.05,
               'PB.SHF':0.1,'RB.SHF':0.02,'RU.SHF':0.02,'SN.SHF': 0.03,'SP.SHF':0.02, 'SS.SHF':0.02,           
               'ZN.SHF':0.02}
std_out_dict_dce = {'A.DCE':0.02,'B.DCE':0.02,'C.DCE':1,'CS.DCE':1,'EB.DCE':0.03,'EG.DCE':0.03,'I.DCE':1,'JM.DCE':0.04,'J.DCE':1,'JD.DCE':0.02,
                   'L.DCE':0.02,'LH.DCE':0.03,'M.DCE':0.02,'P.DCE':0.03,'PG.DCE':0.03,'PP.DCE':0.03,'V.DCE':0.02,'Y.DCE':0.03}
std_out_dict_czc = {'AP.ZCE':0.04,'CF.ZCE':0.02,'CJ.ZCE':0.02,'FG.ZCE':1,'MA.ZCE':0.03,'OI.ZCE':0.03,'PF.ZCE':1,
                   'PK.ZCE':1,'PX.ZCE':0.02,'RM.ZCE':0.02,'SA.ZCE':0.04,'SF.ZCE':1,'SH.ZCE':0.02,'SM.ZCE':0.02,'SR.ZCE':0.02,
                  'TA.ZCE':0.03,'UR.ZCE':0.03}
std_out_dict_gfe = {'LC.GFE':0.03,'SI.GFE':0.02}
std_out_dict_ine = {'NR.INE':0.02,'EC.INE': 0.08,'BC.INE':0.02,'LU.INE':0.02,'SC.INE':0.03}
#std_out_dict = {**std_in_dict_shf,**std_in_dict_dce,**std_in_dict_czc,**std_in_dict_gfe,**std_in_dict_ine}
#std_out_dict = {**std_out_dict_shf,**std_out_dict_dce,**std_out_dict_czc,**std_out_dict_gfe,**std_out_dict_ine}

std_out_dict = {}

lw = 32
sw = 10
daily_ret_out = 0.03
cap = 5e5
feecost = 5e-4
tickcost = 0
feetotal = feecost + tickcost
basis_thd = 0.05

para_dict = {'lw': lw,
             'sw': sw,
             'daily_ret_out': daily_ret_out,
             'cap': cap,
             'feecost': feecost,
             'tickcost': tickcost,
             'feetotal': feetotal,
             'std_in_dict': std_in_dict,
             'std_out_dict': std_out_dict,
             'basis_thd': basis_thd
            }
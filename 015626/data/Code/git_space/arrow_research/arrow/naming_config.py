import os
import datetime
import platform

# trade variable
threshold = 0.15    #绝对阈值
daily_max_num = 50    #每日最大买入上限
daily_min_num = 0 
late_trade_threshold = -0.2

trade_universe_filter = [1, 3, 5]

is_filte_open = True

link_user_ids = ['015626']

# insight variable
auction_start_time = datetime.time(9, 15)
auction_end_time = datetime.time(9, 26, 30)
data_end_time = datetime.time(15, 1, 30)

name_dict = {'tick':'Stock', 'order':'Order', 'order_raw':'Order_RAW', 'transaction':'Transaction'}

trade_root = '/dfs/group/800466/trade/arrow_prod/'
hot_root = os.path.join(trade_root,'hot')
hot_today_root = os.path.join(trade_root,'hot_today')
history_root = os.path.join(trade_root,'history')

eod_path = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5'

data_root = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/'
hot_data_root = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/'
today_data_root = '/dfs/group/800466/warehouse/Arrow/today_data/'
universe_path = os.path.join(trade_root, 'universe', 'arrow_universe.pkl')
risk_blacklist_path = os.path.join(trade_root, 'material', 'risk_blacklist.csv')

# 盘前数据路径， 每晚同步
preprod_data_path = '/data/group/800466/trade/Arrow/trade_files/data_files/history/'

histfactor_days = 60
histfactor_path = os.path.join(trade_root, 'factor', 'h5', 'arrow_factor.h5')
histfactor_dataset = 'arrow_factor'
rawfactor_path = os.path.join(trade_root, 'factor', 'h5', 'arrow_factor.h5')
rawfactor_dataset = 'arrow_factor'
factorinput_path = os.path.join(trade_root, 'factor', 'h5', 'factor_input.h5')
factorinput_dataset = 'factor_input'
factor_savepath = os.path.join(trade_root, 'factor', 'csv')
plan_savepath = os.path.join(trade_root, 'plan') 

# model config
model_name = 'model_20240508'
# model_list = ['lr_cla','lasso_reg','lgbm_cla','lgbm_reg','mlp_reg','mlp_cla']
model_list = ['lasso_reg','lgbm_reg','mlp_reg']
stack_model = 'lasso_reg'
model_root = os.path.join('/data/group/800466/trade/Arrow/trade_files/model', model_name)
stack_model_root = os.path.join(model_root, 'stack_model_reg')
model_value_path = os.path.join(trade_root, 'model', 'model_value')

# short model config
short_model_name = 'model_20240508_open'
# model_list = ['lr_cla','lasso_reg','lgbm_cla','lgbm_reg','mlp_reg','mlp_cla']
short_model_list = ['lasso_reg','lgbm_reg','mlp_reg']
short_stack_model = 'lasso_reg'
short_model_root = os.path.join('/data/group/800466/trade/Arrow/trade_files/model', short_model_name)
short_stack_model_root = os.path.join(short_model_root, 'stack_model_reg')
short_model_value_path = os.path.join(trade_root, 'model', 'short_model_value')

factor_final_list = ['factor_1', 'factor_10', 'factor_101', 'factor_102', 'factor_103', 'factor_104', 'factor_106', 'factor_107', 'factor_108', 'factor_11', 'factor_110', 'factor_111', 'factor_113', 'factor_114', 'factor_115', 'factor_116', 'factor_117', 'factor_118', 'factor_119', 'factor_120', 'factor_121', 'factor_122', 'factor_123', 'factor_124', 'factor_125', 'factor_126', 'factor_127', 'factor_128', 'factor_129', 'factor_13', 'factor_139', 'factor_14', 'factor_143', 'factor_144', 'factor_145', 'factor_15', 'factor_156', 'factor_157', 'factor_158', 'factor_16', 'factor_163', 'factor_17', 'factor_171', 'factor_172', 'factor_173', 'factor_174', 'factor_175', 'factor_176', 'factor_177', 'factor_178', 'factor_179', 'factor_18', 'factor_180', 'factor_181', 'factor_182', 'factor_183', 'factor_184', 'factor_185', 'factor_186', 'factor_187', 'factor_189', 'factor_19', 'factor_190', 'factor_191', 'factor_192', 'factor_193', 'factor_194', 'factor_195', 'factor_196', 'factor_197', 'factor_2', 'factor_20', 'factor_202', 'factor_203', 'factor_204', 'factor_205', 'factor_207', 'factor_208', 'factor_209', 'factor_21', 'factor_210', 'factor_211', 'factor_212', 'factor_213', 'factor_214', 'factor_215', 'factor_216', 'factor_217', 'factor_218', 'factor_219', 'factor_22', 'factor_220', 'factor_221', 'factor_222', 'factor_223', 'factor_224', 'factor_226', 'factor_227', 'factor_229', 'factor_23', 'factor_230', 'factor_231', 'factor_232', 'factor_233', 'factor_235', 'factor_236', 'factor_238', 'factor_239', 'factor_24', 'factor_240', 'factor_241', 'factor_242', 'factor_243', 'factor_244', 'factor_245', 'factor_246', 'factor_247', 'factor_248', 'factor_249', 'factor_25', 'factor_250', 'factor_251', 'factor_252', 'factor_253', 'factor_254', 'factor_255', 'factor_256', 'factor_257', 'factor_258', 'factor_259', 'factor_26', 'factor_260', 'factor_261', 'factor_262', 'factor_263', 'factor_264', 'factor_265', 'factor_266', 'factor_267', 'factor_268', 'factor_269', 'factor_27', 'factor_270', 'factor_271', 'factor_272', 'factor_273', 'factor_274', 'factor_275', 'factor_276', 'factor_277', 'factor_278', 'factor_279', 'factor_28', 'factor_280', 'factor_281', 'factor_282', 'factor_283', 'factor_284', 'factor_285', 'factor_286', 'factor_287', 'factor_29', 'factor_3', 'factor_302', 'factor_303', 'factor_305', 'factor_306', 'factor_31', 'factor_32', 'factor_326', 'factor_327', 'factor_329', 'factor_33', 'factor_330', 'factor_331', 'factor_332', 'factor_333', 'factor_336', 'factor_338', 'factor_339', 'factor_34', 'factor_340', 'factor_341', 'factor_343', 'factor_346', 'factor_347', 'factor_35', 'factor_350', 'factor_354', 'factor_358', 'factor_359', 'factor_36', 'factor_362', 'factor_364', 'factor_37', 'factor_38', 'factor_39', 'factor_4', 'factor_40', 'factor_400', 'factor_401', 'factor_402', 'factor_403', 'factor_404', 'factor_405', 'factor_406', 'factor_407', 'factor_408', 'factor_409', 'factor_41', 'factor_410', 'factor_411', 'factor_412', 'factor_413', 'factor_414', 'factor_415', 'factor_416', 'factor_417', 'factor_418', 'factor_42', 'factor_420', 'factor_421', 'factor_422', 'factor_423', 'factor_424', 'factor_425', 'factor_426', 'factor_427', 'factor_428', 'factor_429', 'factor_43', 'factor_430', 'factor_431', 'factor_434', 'factor_436', 'factor_438', 'factor_439', 'factor_44', 'factor_440', 'factor_441', 'factor_445', 'factor_45', 'factor_46', 'factor_47', 'factor_48', 'factor_49', 'factor_50', 'factor_500', 'factor_501', 'factor_502', 'factor_503', 'factor_504', 'factor_505', 'factor_506', 'factor_507', 'factor_508', 'factor_509', 'factor_51', 'factor_510', 'factor_511', 'factor_512', 'factor_513', 'factor_514', 'factor_515', 'factor_516', 'factor_517', 'factor_518', 'factor_519', 'factor_52', 'factor_520', 'factor_521', 'factor_522', 'factor_523', 'factor_524', 'factor_525', 'factor_526', 'factor_527', 'factor_528', 'factor_529', 'factor_53', 'factor_530', 'factor_531', 'factor_532', 'factor_533', 'factor_534', 'factor_535', 'factor_536', 'factor_538', 'factor_54', 'factor_542', 'factor_543', 'factor_544', 'factor_545', 'factor_546', 'factor_547', 'factor_548', 'factor_549', 'factor_550', 'factor_551', 'factor_552', 'factor_553', 'factor_554', 'factor_555', 'factor_556', 'factor_557', 'factor_558', 'factor_559', 'factor_56', 'factor_560', 'factor_561', 'factor_562', 'factor_563', 'factor_564', 'factor_565', 'factor_57', 'factor_570', 'factor_571', 'factor_58', 'factor_580', 'factor_581', 'factor_582', 'factor_583', 'factor_584', 'factor_585', 'factor_586', 'factor_587', 'factor_588', 'factor_589', 'factor_59', 'factor_590', 'factor_591', 'factor_592', 'factor_593', 'factor_594', 'factor_595', 'factor_596', 'factor_597', 'factor_598', 'factor_599', 'factor_6', 'factor_60', 'factor_600', 'factor_601', 'factor_602', 'factor_604', 'factor_61', 'factor_62', 'factor_63', 'factor_64', 'factor_65', 'factor_66', 'factor_67', 'factor_68', 'factor_69', 'factor_7', 'factor_70', 'factor_700', 'factor_701', 'factor_702', 'factor_703', 'factor_704', 'factor_705', 'factor_706', 'factor_707', 'factor_708', 'factor_709', 'factor_71', 'factor_710', 'factor_711', 'factor_712', 'factor_713', 'factor_714', 'factor_715', 'factor_716', 'factor_717', 'factor_718', 'factor_719', 'factor_72', 'factor_720', 'factor_721', 'factor_722', 'factor_723', 'factor_724', 'factor_725', 'factor_726', 'factor_727', 'factor_728', 'factor_729', 'factor_73', 'factor_730', 'factor_731', 'factor_732', 'factor_733', 'factor_734_0', 'factor_734_1', 'factor_734_2', 'factor_734_3', 'factor_735_0', 'factor_735_1', 'factor_735_2', 'factor_736_0', 'factor_736_1', 'factor_736_2', 'factor_736_3', 'factor_736_4', 'factor_74', 'factor_75', 'factor_76', 'factor_77', 'factor_8', 'factor_80', 'factor_81', 'factor_82', 'factor_83', 'factor_84', 'factor_85', 'factor_86', 'factor_87', 'factor_88', 'factor_89', 'factor_90', 'factor_91', 'factor_92', 'factor_93', 'factor_94', 'factor_95', 'factor_96', 'factor_97', 'factor_amount_t_1', 'factor_htc_10wc', 'factor_htc_10wm', 'factor_htc_abspath_ratio', 'factor_htc_buy10wc', 'factor_htc_buy10wm', 'factor_htc_buyc', 'factor_htc_buym', 'factor_htc_c', 'factor_htc_cancel_buy10wm', 'factor_htc_cancel_buyc', 'factor_htc_cancel_buym', 'factor_htc_cancel_sell10wm', 'factor_htc_cancel_sellc', 'factor_htc_cancel_sellm', 'factor_htc_m', 'factor_htc_order_buy10wc', 'factor_htc_order_buy10wm', 'factor_htc_order_buy10wm_market_tranm', 'factor_htc_order_buy10wm_tranm', 'factor_htc_order_buyc', 'factor_htc_order_buym', 'factor_htc_order_buym_market_tranm', 'factor_htc_order_buym_tranm', 'factor_htc_order_sell10wc', 'factor_htc_order_sell10wm', 'factor_htc_order_sell10wm_market_tranm', 'factor_htc_order_sell10wm_tranm', 'factor_htc_order_sellc', 'factor_htc_order_sellm', 'factor_htc_order_sellm_market_tranm', 'factor_htc_order_sellm_tranm', 'factor_htc_ratio', 'factor_htc_sell10wc', 'factor_htc_sell10wm', 'factor_htc_sellc', 'factor_htc_sellm', 'factor_htc_tick_numratio', 'factor_openPct', 'factor_order_bo10w_buym', 'factor_order_bo10w_buym_tranm', 'factor_order_bo10w_sellm', 'factor_order_bo10w_sellm_tranm', 'factor_order_bo_buyc', 'factor_order_bo_buym', 'factor_order_bo_buym_tranm', 'factor_order_bo_c', 'factor_order_bo_m', 'factor_order_bo_sellc', 'factor_order_bo_sellm', 'factor_order_bo_sellm_tranm', 'factor_order_so10w_buym', 'factor_order_so10w_buym_tranm', 'factor_order_so10w_sellm', 'factor_order_so10w_sellm_tranm', 'factor_order_so_buyc', 'factor_order_so_buym', 'factor_order_so_buym_tranm', 'factor_order_so_c', 'factor_order_so_m', 'factor_order_so_sellc', 'factor_order_so_sellm', 'factor_order_so_sellm_tranm', 'factor_oth_10wc', 'factor_oth_10wm', 'factor_oth_buy10wc', 'factor_oth_buy10wm', 'factor_oth_buyc', 'factor_oth_buym', 'factor_oth_c', 'factor_oth_cancel_buy10wm', 'factor_oth_cancel_buyc', 'factor_oth_cancel_buym', 'factor_oth_cancel_sell10wm', 'factor_oth_cancel_sellc', 'factor_oth_cancel_sellm', 'factor_oth_m', 'factor_oth_order_buy10wc', 'factor_oth_order_buy10wm', 'factor_oth_order_buy10wm_market_tranm', 'factor_oth_order_buy10wm_tranm', 'factor_oth_order_buyc', 'factor_oth_order_buym', 'factor_oth_order_buym_market_tranm', 'factor_oth_order_buym_tranm', 'factor_oth_order_sell10wc', 'factor_oth_order_sell10wm', 'factor_oth_order_sell10wm_market_tranm', 'factor_oth_order_sell10wm_tranm', 'factor_oth_order_sellc', 'factor_oth_order_sellm', 'factor_oth_order_sellm_market_tranm', 'factor_oth_order_sellm_tranm', 'factor_oth_ratio', 'factor_oth_sell10wc', 'factor_oth_sell10wm', 'factor_oth_sellc', 'factor_oth_sellm', 'factor_oth_tick_numratio', 'factor_tran_bo10w_buym', 'factor_tran_bo10w_sellm', 'factor_tran_bo_buym', 'factor_tran_bo_m', 'factor_tran_bo_sellm', 'factor_tran_so10w_buym', 'factor_tran_so10w_sellm', 'factor_tran_so_buym', 'factor_tran_so_m', 'factor_tran_so_sellm']
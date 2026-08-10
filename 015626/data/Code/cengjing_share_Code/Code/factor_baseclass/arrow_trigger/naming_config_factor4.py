import os
import datetime
import platform

# trade variable
threshold = 0.15    #绝对阈值
daily_max_num = 50    #每日最大买入上限
daily_min_num = 3 

# insight variable
auction_start_time = datetime.time(9, 15)
auction_end_time = datetime.time(9, 26, 30)
data_end_time = datetime.time(15, 1, 30)

factor_final_list = ['factor_1', 'factor_10', 'factor_101', 'factor_102', 'factor_103', 'factor_104', 'factor_106', 'factor_107', 'factor_108', 'factor_11', 'factor_110', 'factor_111', 'factor_113', 'factor_114', 'factor_115', 'factor_117', 'factor_118', 'factor_119', 'factor_121', 'factor_123', 'factor_125', 'factor_127', 'factor_129', 'factor_13', 'factor_139', 'factor_14', 'factor_143', 'factor_144', 'factor_145', 'factor_15', 'factor_156', 'factor_157', 'factor_158', 'factor_16', 'factor_163', 'factor_17', 'factor_171', 'factor_172', 'factor_174', 'factor_175', 'factor_177', 'factor_178', 'factor_179', 'factor_18', 'factor_180', 'factor_181', 'factor_182', 'factor_183', 'factor_184', 'factor_185', 'factor_186', 'factor_187', 'factor_189', 'factor_19', 'factor_191', 'factor_195', 'factor_196', 'factor_197', 'factor_2', 'factor_20', 'factor_202', 'factor_203', 'factor_204', 'factor_205', 'factor_207', 'factor_208', 'factor_21', 'factor_210', 'factor_211', 'factor_213', 'factor_214', 'factor_215', 'factor_216', 'factor_217', 'factor_218', 'factor_219', 'factor_22', 'factor_220', 'factor_221', 'factor_222', 'factor_223', 'factor_224', 'factor_226', 'factor_227', 'factor_23', 'factor_231', 'factor_232', 'factor_233', 'factor_235', 'factor_236', 'factor_239', 'factor_240', 'factor_241', 'factor_242', 'factor_243', 'factor_244', 'factor_249', 'factor_25', 'factor_250', 'factor_251', 'factor_252', 'factor_253', 'factor_254', 'factor_258', 'factor_259', 'factor_26', 'factor_260', 'factor_261', 'factor_262', 'factor_267', 'factor_268', 'factor_269', 'factor_270', 'factor_271', 'factor_272', 'factor_276', 'factor_277', 'factor_278', 'factor_279', 'factor_280', 'factor_281', 'factor_282', 'factor_283', 'factor_284', 'factor_286', 'factor_287', 'factor_29', 'factor_3', 'factor_306', 'factor_31', 'factor_32', 'factor_326', 'factor_327', 'factor_33', 'factor_330', 'factor_331', 'factor_332', 'factor_333', 'factor_336', 'factor_34', 'factor_340', 'factor_341', 'factor_346', 'factor_35', 'factor_354', 'factor_358', 'factor_36', 'factor_37', 'factor_38', 'factor_39', 'factor_40', 'factor_41', 'factor_42', 'factor_43', 'factor_44', 'factor_45', 'factor_46', 'factor_47', 'factor_48', 'factor_49', 'factor_50', 'factor_51', 'factor_52', 'factor_53', 'factor_54', 'factor_56', 'factor_57', 'factor_58', 'factor_59', 'factor_6', 'factor_60', 'factor_61', 'factor_62', 'factor_64', 'factor_65', 'factor_66', 'factor_67', 'factor_68', 'factor_69', 'factor_7', 'factor_70', 'factor_71', 'factor_73', 'factor_74', 'factor_75', 'factor_76', 'factor_77', 'factor_8', 'factor_80', 'factor_81', 'factor_82', 'factor_83', 'factor_84', 'factor_85', 'factor_86', 'factor_87', 'factor_88', 'factor_89', 'factor_91', 'factor_95', 'factor_96', 'factor_97']
rule_blacklist_columns = ['filter_1', 'filter_2', 'filter_3', 'open_to_preclose', 'bsp', 's1_high_to_limit', 's2_high_to_limit',
        'last_day_amount_ratio', 'last_day_close_to_open', 'last_day_high_to_open', 'last_day_high_to_close',
        'last_day_xyx', 'last_day_tail5_ll', 'dby_high_to_low', 'amount', 'last_day_rolling_60min_drawdown',
        'last_day_tail10_close_to_low']

name_dict = {'tick':'Stock', 'order':'Order', 'order_raw':'Order_RAW', 'transaction':'Transaction'}

trade_root = '/arch1/group/800466/warehouse/Arrow/arrow/'
hot_root = os.path.join(trade_root,'hot')
history_root = os.path.join(trade_root,'history')

eod_path = '/data/group/800080/warehouse/test/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5'

data_root = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/'
hot_data_root = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/'
today_data_root = ''
universe_path = '/data/user/000072/share/for_wyc/arrow/universe/universe_20230509.pkl'

mad_periods = [5, 60]
factor_clip_scope_days = 120
histfactor_days = 59
histfactor_path = os.path.join(trade_root, 'factor4', 'h5', 'arrow_factor_distribution_v3.h5')
histfactor_dataset = 'arrow_factor_distribution_v3'
rawfactor_path = os.path.join(trade_root, 'factor4', 'h5', 'arrow_factor.h5')
rawfactor_dataset = 'arrow_factor'
factorinput_path = os.path.join(trade_root, 'factor4', 'h5', 'factor_clip_v3_95_mad_5_60.h5')
factorinput_dataset = 'factor_clip_v3_95_mad_5_60'
factor_savepath = os.path.join(trade_root, 'factor4', 'csv')
plan_savepath = os.path.join(trade_root, 'plan')

# model config
model_name = '20230220_factor_clip_v3_95_mad_5_60'
model_list = ['lr_cla','lasso_reg','lgbm_cla','lgbm_reg','mlp_reg','mlp_cla']
stack_model = 'lasso_reg'
# model_root = os.path.join(trade_root, 'model', 'model_file', model_name)
model_root = os.path.join('/arch1/group/800466/warehouse/Arrow/arrow/', 'model', 'model_file', model_name)
stack_model_root = os.path.join(model_root, 'stack_model')
model_value_path = os.path.join(trade_root, 'model', 'model_value')

# factor clip
right_95_list = '143 144 145 83 81 21 121 122 123 124 125 126 43 70 80'
right_95_list = [f'factor_{x}' for x in right_95_list.split(' ')]
left_5_list = '51 52 81 83 22 121 122 125 126 63 70 80 182 25 26'
left_5_list = [f'factor_{x}' for x in left_5_list.split(' ')]
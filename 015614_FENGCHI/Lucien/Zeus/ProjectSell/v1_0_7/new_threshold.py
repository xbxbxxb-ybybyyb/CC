# coding: utf-8
# Author：fengchi863
# Date ：2023/4/19 15:30

"""
save new threshold
"""
import json
# sell v3 Next 四个模型
best_threshold = -0.000238
junk_path = '/data/user/015614/junkData/LgbRffsNextRegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

best_threshold = 0.003978
junk_path = '/data/user/015614/junkData/XgbRffsNextRegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

best_threshold = 0.000573
junk_path = '/data/user/015614/junkData/LgbFSV8NextRegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

best_threshold = 0.002574
junk_path = '/data/user/015614/junkData/XgbFSV10NextRegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

# sell v1 四个模型
best_threshold = 0.001952
junk_path = '/data/user/015614/junkData/LgbRffsRegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

best_threshold = 0.002109
junk_path = '/data/user/015614/junkData/XgbRffsRegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

best_threshold = 0.000454
junk_path = '/data/user/015614/junkData/LgbFSV10RegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)

best_threshold = 0.003454
junk_path = '/data/user/015614/junkData/XgbFSV10RegModel/'
with open(junk_path + '_score_threshold.json', 'w') as f:
    json.dump([best_threshold], f, ensure_ascii=False, indent=2)
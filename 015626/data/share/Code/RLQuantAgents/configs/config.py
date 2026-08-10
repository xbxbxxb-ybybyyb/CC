from __future__ import annotations

TRAIN_START_DATE = "2017-01-01"
TRAIN_END_DATE = "2021-12-31"

TEST_START_DATE = "2022-01-01"
TEST_END_DATE = "2022-12-31"

TRADE_START_DATE = "2023-01-01"
TRADE_END_DATE = "2023-12-31"

FACTOR_NUM = 824

A2C_PARAMS = {"n_steps":5, "ent_coef":0.01, "learning_rate": 1e-4}
PPO_PARAMS = {
    "n_steps": 2048,
    "ent_coef":0.01,
    "learning_rate":1e-4,
    "batch_size":64
}
GRPO_PARAMS = {
    "n_steps": 2048,
    "ent_coef":0.01,
    "learning_rate":1e-4,
    "batch_size":64
}
DDPG_PARAMS = {
    "batch_size":128,
    "buffer_size":50000,
    "learning_rate":1e-4
}
TD3_PARAMS={
    "batch_size":100,
    "buffer_size":50000,
    "learning_rate":1e-4,
}
SAC_PARAMS={
    "batch_size":64,
    "buffer_size":100000,
    "learning_rate":8e-5,
    "learning_start":100,
    "ent_coef":"auto_0.1"
}
ERL_PARAMS={
    "learning_rate":3e-5,
    "batch_size":2048,
    "gamma":0.985,
    "seed":312,
    "net_dimension":512,
    "target_step":5000,
    "eval_gap":30,
    "eval_times":64
}
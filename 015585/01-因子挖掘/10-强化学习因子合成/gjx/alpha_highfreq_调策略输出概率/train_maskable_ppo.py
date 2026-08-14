import json
import os
from typing import Optional, Tuple
from datetime import datetime
import fire

import numpy as np
from alphagen.models.mask_ppo import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
from alphagen.data.calculator import AlphaCalculator

from alphagen.data.expression import *
from alphagen.models.alpha_pool import AlphaPool, AlphaPoolBase
from alphagen.rl.env.wrapper import AlphaEnv
from alphagen.rl.policy import LSTMSharedNet
from alphagen.utils.random import reseed_everything
from alphagen.rl.env.core import AlphaEnvCore
from alphagen_qlib.calculator import QLibStockDataCalculator
from alphagen_qlib.stock_data import StockData,FeatureType,TargetType


class CustomCallback(BaseCallback):
    def __init__(self,
                 save_freq: int,
                 show_freq: int,
                 save_path: str,
                 valid_calculator: AlphaCalculator,
                 test_calculator: AlphaCalculator,
                 name_prefix: str = 'rl_model',
                 timestamp: Optional[str] = None,
                 verbose: int = 0):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.show_freq = show_freq
        self.save_path = save_path
        self.name_prefix = name_prefix

        self.valid_calculator = valid_calculator
        self.test_calculator = test_calculator

        if timestamp is None:
            self.timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        else:
            self.timestamp = timestamp

    def _init_callback(self) -> None:
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        return True

    # 都在alpha_pool.py这个额文件里定义了，本来也是返回pool的情况
    def _on_rollout_end(self) -> None:
        assert self.logger is not None
        self.logger.record('pool/size', self.pool.size)
        self.logger.record('pool/significant', (np.abs(self.pool.weights[:self.pool.size]) > 1e-4).sum())
        self.logger.record('pool/best_ic_ret', self.pool.best_ic_ret)
        self.logger.record('pool/worst_ic_ret', self.pool.worst_ic_ret)
        self.logger.record('pool/abs_mean_ic_ret', self.pool.abs_mean_ic_ret)
        self.logger.record('pool/eval_cnt', self.pool.eval_cnt)
        # valid
        best_ic_ret, worst_ic_ret, abs_mean_ic_ret = self.pool.test_pool(self.valid_calculator)
        self.logger.record('valid/best_ic_ret', best_ic_ret)
        self.logger.record('valid/worst_ic_ret', worst_ic_ret)
        self.logger.record('valid/abs_mean_ic_ret', abs_mean_ic_ret)

        # test
        best_ic_ret, worst_ic_ret, abs_mean_ic_ret = self.pool.test_pool(self.test_calculator)
        self.logger.record('test/best_ic_ret', best_ic_ret)
        self.logger.record('test/worst_ic_ret', worst_ic_ret)
        self.logger.record('test/abs_mean_ic_ret', abs_mean_ic_ret)

        self.save_checkpoint()

    def save_checkpoint(self):
        path = os.path.join(self.save_path, f'{self.name_prefix}_{self.timestamp}', f'{self.num_timesteps}_steps')
        self.model.save(path)   # type: ignore
        if self.verbose > 1:
            print(f'Saving model checkpoint to {path}')
        with open(f'{path}_pool.json', 'w') as f:
            json.dump(self.pool.to_dict(), f)

    def show_pool_state(self):
        state = self.pool.state
        n = len(state['exprs'])
        print('---------------------------------------------')
        for i in range(n):
            expr_str = str(state['exprs'][i])
            ic_ret = state['ics_ret'][i]
            print(f'> Alpha #{i}: {expr_str}, {ic_ret}')
        print(f'>> Ensemble ic_ret: {state["best_ic_ret"]}')
        print('---------------------------------------------')

    @property
    def pool(self) -> AlphaPoolBase:
        return self.env_core.pool

    @property
    def env_core(self) -> AlphaEnvCore:
        return self.training_env.envs[0].unwrapped  # type: ignore


def main(
    seed: int = 0,
    pool_capacity: int = 10,
    steps: int = 200_000
):
    reseed_everything(seed)

    device = torch.device('cuda:0')
    target = Feature(TargetType.label)


    # You can re-implement AlphaCalculator instead of using QLibStockDataCalculator.
    data_train = StockData(start_time='2018-01-01',
                           end_time='2018-12-31',
                           file_path='./high_data.pkl',
                           target_path='./label.pkl',
                           n_windows=72)  # 降频之后有多少这个维度的数据
    data_valid = StockData(start_time='2019-01-01',
                           end_time='2019-06-30',
                           file_path='./high_data.pkl',
                           target_path='./label.pkl',
                           n_windows=72)
    data_test = StockData(start_time='2019-07-01',
                          end_time='2019-12-31',
                          file_path='./high_data.pkl',
                          target_path='./label.pkl',
                          n_windows=72)
    calculator_train = QLibStockDataCalculator(data_train, target)
    calculator_valid = QLibStockDataCalculator(data_valid, target)
    calculator_test = QLibStockDataCalculator(data_test, target)

    pool = AlphaPool(
        capacity=pool_capacity,
        calculator=calculator_train,
        ic_lower_bound=None,
        l1_alpha=0.03
    )
    env = AlphaEnv(pool=pool, device=device, print_expr=True)

    name_prefix = f"new_{pool_capacity}_{seed}"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    checkpoint_callback = CustomCallback(
        save_freq=10000,
        show_freq=10000,
        save_path='./path/for/checkpoints',
        valid_calculator=calculator_valid,
        test_calculator=calculator_test,
        name_prefix=name_prefix,
        timestamp=timestamp,
        verbose=1
    )

    model = MaskablePPO(
        'MlpPolicy',
        env,
        policy_kwargs=dict(
            features_extractor_class=LSTMSharedNet,
            features_extractor_kwargs=dict(
                n_layers=2,
                d_model=128,
                dropout=0.1,
                device=device,
            ),
        ),
        gamma=1.,
        ent_coef=0.05,
        batch_size=128,
        tensorboard_log='./path/for/tb/log',
        device=device,
        verbose=1,
        n_steps=1024,
    )
    model.learn(
        total_timesteps=steps,
        callback=checkpoint_callback,
        tb_log_name=f'{name_prefix}_{timestamp}',
    )


def fire_helper(
    seed: Union[int, Tuple[int]],
    pool: int,
    step: int = None
):
    if isinstance(seed, int):
        seed = (seed, )
    default_steps = {
        10: 250_000,
        20: 300_000,
        50: 350_000,
        100: 250_000
    }
    for _seed in seed:
        main(_seed,
             pool,
             default_steps[int(pool)] if step is None else int(step)
             )


if __name__ == '__main__':
    # fire.Fire(fire_helper)
    fire.Fire(fire_helper(seed=2, pool=100))
# -*- coding: utf-8 -*-
# @Time   :  2024/7/22 11:40
# @Author :  liuzy

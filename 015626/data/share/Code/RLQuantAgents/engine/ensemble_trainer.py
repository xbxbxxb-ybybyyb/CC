import time
import numpy as np
from models.PPO import PPOAgent
from models.TD3 import TD3Agent
from models.DDPG import DDPGAgent
from models.A2C import A2CAgent
from models.SAC import SACAgent
from models.GRPO import GRPOAgent
from configs import config

MODELS = {"a2c": A2CAgent, "ddpg": DDPGAgent, "sac": SACAgent, "td3": TD3Agent, "ppo": PPOAgent, "grpo": GRPOAgent}

MODEL_KWARGS = {x: config.__dict__[f"{x.upper()}_PARAMS"] for x in MODELS.keys()}


class DRLAgent(object):
    def __init__(self, env):
        self.env = env

    def get_model(self, model_name, policy="MlpPolicy", policy_kwargs=None, model_kwargs=None, verbose=1, seed=None):
        if model_name not in MODELS:
            raise ValueError(
                f"Model '{model_name}' not found in MODELS."
            )
        if model_kwargs is None:
            model_kwargs = MODEL_KWARGS[model_name]
        # if "action_noise" in model_kwargs:
        #     n_actions = self.env.action_space.shape[-1]
        #     model_kwargs['action_noise'] = NOISE[model_kwargs['action_noise']](
        #         mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions)
        #     )
        print(model_kwargs)
        return MODELS[model_name](policy=policy, env=self.env, verbose=verbose, policy_kwargs=policy_kwargs, seed=seed,
                                  **model_kwargs)
    @staticmethod
    def train_model(
            model
    ):
        model = model.learn()
        return model
    # @staticmethod
    # def DRL_prediction(model, environment, deterministic=True):

from env_4fps import env_4fps
from stable_baselines3 import PPO, SAC
import gymnasium as gym
import numpy as np
import os
import matplotlib.pyplot as plt
import torch
import time
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.noise import NormalActionNoise
import optuna
print(torch.cuda.is_available())

def get_mean_eval_reward(learning_rate, tau, gamma, 
                         repetitions=1, eval_episodes=3, timesteps=10000): # ActionNoise_sigma
    MEANS = []
    for i in range(repetitions):
        name = f"SAC_hyperparams_lr{learning_rate}_tau{tau}_gamma{gamma}_rep{i}" # _sigma{ActionNoise_sigma}
        print(f"starting trail: {name}")
        #mean = np.array([0.0, 0.0])
        #sigma = np.array([ActionNoise_sigma, ActionNoise_sigma])
        #action_noise = NormalActionNoise(mean, sigma)

        model = SAC("MlpPolicy", env, verbose=1, device="cpu", policy_kwargs=policy_kwargs, 
                    learning_rate=learning_rate, tau=tau, gamma=gamma) # action_noise=action_noise
        model.learn(total_timesteps=timesteps)
        model.save(name)

        model.policy.set_training_mode(False)
        model.action_noise = None
        mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=eval_episodes)
        print(f"mean_reward: {mean_reward}, std_reward: {std_reward} with {name}")
        MEANS.append(mean_reward)
    return min(MEANS)

def objective(trial):
    learning_rate     = trial.suggest_float('learning_rate', 1e-5, 1e-3, log=True)
    tau               = trial.suggest_float('tau', 0.001, 0.1)
    gamma             = trial.suggest_float('gamma', 0.7, 0.999)
    #ActionNoise_sigma = trial.suggest_float('ActionNoise_sigma', 0, 0.15)
    # batch size 64, 128, 256, 512 later...
    return get_mean_eval_reward(learning_rate, tau, gamma) # ActionNoise_sigma


env = Monitor(env_4fps(plot=True, save_steps=True, smooth=True))

policy_kwargs = dict(
    net_arch=dict(
        pi=[256, 256, 256, 256],  # For the actor network
        vf=[256, 256, 256, 256],   # For the critic network
        qf=[256, 256, 256, 256]   # For the critic network
    ),
    activation_fn=torch.nn.ReLU
)

sampler = optuna.samplers.TPESampler(n_ei_candidates=10000, seed=0)
study = optuna.create_study(
    study_name="study_20_03_25_10k", 
    storage="sqlite:///SAC_hyperparams.db", 
    load_if_exists=True, 
    direction="maximize", 
    sampler=sampler
)
study.optimize(objective, n_trials=100)
print(study.best_params)
#from real_env import Real_env
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
print(torch.cuda.is_available())

#env = Monitor(Real_env(plot=True, save_steps=True))
env = Monitor(env_4fps(plot=True, save_steps=True, smooth=True))

#check_env(env, warn=True, skip_render_check=True)

#model = SAC.load("SAC_5fps_003", env=env)
#model = SAC("MlpPolicy", env, verbose=1, device="cpu", batch_size=128, tau=0.002, gamma=0.95) # cuda$

policy_kwargs = dict(
    net_arch=dict(
        pi=[256, 256, 256, 256],  # For the actor network
        vf=[256, 256, 256, 256],   # For the critic network
        qf=[256, 256, 256, 256]   # For the critic network
    ),
    activation_fn=torch.nn.ReLU
)



"""########## eval ##############
model = SAC.load("SAC_5fps_smooth1_002", env=env)
model.policy.set_training_mode(False)
    
# Run evaluation episodes (here, using the evaluate_policy helper)
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=5)
print(f"Iteration {0}: mean reward {mean_reward:.2f} ± {std_reward:.2f}")

# If you intend to continue training afterwards, switch back to training mode:
model.policy.set_training_mode(True)
assert False
##############################"""



model = SAC.load("SAC_5fps_smooth1_002", env=env)
#model = SAC("MlpPolicy", env, verbose=1, device="cpu", policy_kwargs=policy_kwargs, gamma=0.8) # cuda #  gamma=0.97, batch_size=128


#print(model.policy)

for i in range(1000):
    model.learn(total_timesteps=2000) # , reset_num_timesteps=False
    model.save("SAC_5fps_smooth1_002") ### !!!!!!!   pip install --upgrade cloudpickle
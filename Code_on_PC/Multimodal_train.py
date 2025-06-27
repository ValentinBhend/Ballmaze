from Multimodal_env import env_multimodal
from Multimodal_maze_layout import Maze_layout

from stable_baselines3 import SAC
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
import torch
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import gymnasium as gym
import os
from Multimodel_utils import CustomCombinedExtractor_V1, BallmazeReplayBuffer
from datetime import datetime
import time
import pickle


maze_layout = Maze_layout()
env = Monitor(env_multimodal(maze_layout, plot=False, save_steps=False, save_img=False, Pi5=True))

policy_kwargs = dict(
    features_extractor_class=CustomCombinedExtractor_V1,
    net_arch=dict(
        pi=[500, 300], 
        vf=[500, 300],
        qf=[500, 300]
        )
)


filename = "sac_Pi5_005"

if os.path.exists(filename + ".zip"):
    print("loading existing model")
    model = SAC.load(filename + ".zip", env=env, device="cuda")
    model.learning_starts = 0
    model.load_replay_buffer(filename + "replay_buffer" + ".pkl")
    print(f"replay buffer: {model.replay_buffer.size()}")
    # with open(filename + "model_infos" + ".pkl", 'rb') as f:
    #     model_infos = pickle.load(f)
    # print(model_infos)
else:
    print("creating new model")
    model_infos = {"steps taken": 0, 
                   "time used": 0, 
                   "params": {
                       "learning_rate": 3e-4,
                       "buffer_size": 20_000_000,
                       "learning_starts": 600,
                       "batch_size": 512,
                       "tau": 0.005,
                       "gamma": 0.98,
                       "train_freq": (1, "episode"),
                       "gradient_steps": -1,
                       }
                  }
    print(model_infos)
    model = SAC("MultiInputPolicy", env, 
                verbose=1, 
                device="cuda",
                policy_kwargs=policy_kwargs,
                replay_buffer_class=BallmazeReplayBuffer,
                replay_buffer_kwargs={"maze_layout": maze_layout},
                **model_infos["params"]
                )


print("STARTING TRAIN")
for i in range(10000):
    hour = datetime.now().hour
    if hour >= 23 or hour < 8:
        print("going to sleep")
    while hour >= 23 or hour < 8:
        time.sleep(60)
        hour = datetime.now().hour

    print(f"###########################    {i} iteration       ############################")
    N = 20_000
    t0 = time.time()

    model.learn(total_timesteps=N)
    model.learning_starts = 0
    model.save_replay_buffer(filename + "replay_buffer" + ".pkl")
    model.save(filename + ".zip")
    # model_infos["steps taken"] += N
    # model_infos["time used"] += time.time() - t0
    # with open(filename + "model_infos" + ".pkl", 'wb') as f:
    #     pickle.dump(model_infos, f)
    # print(model_infos)

# print("STARTING EVAL")
# model.policy.set_training_mode(False)
# mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
# print(f"mean_reward: {mean_reward}, std_reward, {std_reward}")
from Multimodal_env import env_multimodal
from Multimodal_maze_layout import Maze_layout
from Multimodal_dummy_env import CNN_dummy_env

from stable_baselines3 import SAC
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
import torch
from gymnasium import spaces
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import gymnasium as gym
import os
from stable_baselines3.common.buffers import DictReplayBuffer, ReplayBuffer
import numpy as np



from typing import Any, Optional, Union
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.type_aliases import (
    DictReplayBufferSamples,
    DictRolloutBufferSamples,
    ReplayBufferSamples,
    RolloutBufferSamples,
)
from collections.abc import Generator
from collections import OrderedDict



class CustomCombinedExtractor_V1(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict):
        # We do not know features-dim here before going over all the items,
        # so put something dummy for now. PyTorch requires calling
        # nn.Module.__init__ before adding modules
        super().__init__(observation_space, features_dim=1)

        extractors = {}

        total_concat_size = 0
        # We need to know size of the output of this extractor,
        # so go over all the spaces and compute output feature sizes
        for key, subspace in observation_space.spaces.items():
            if key == "image":
                extractors[key] = nn.Sequential(
                            # First block
                            nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3, stride=1, padding=1),
                            nn.BatchNorm2d(8),
                            nn.LeakyReLU(0.1),
                            
                            # Second block
                            nn.Conv2d(in_channels=8, out_channels=16, kernel_size=3, stride=2, padding=1),  # Strided conv
                            nn.BatchNorm2d(16),
                            nn.LeakyReLU(0.1),
                            
                            # Third block
                            nn.Conv2d(in_channels=16, out_channels=16, kernel_size=3, stride=2, padding=1),  # Strided conv
                            nn.BatchNorm2d(16),
                            nn.LeakyReLU(0.1),
                            
                            # Fourth block with more aggressive reduction
                            nn.Conv2d(in_channels=16, out_channels=18, kernel_size=3, stride=2, padding=1),  # Additional stride reduction
                            nn.BatchNorm2d(18), # same as out-channels
                            nn.LeakyReLU(0.1),
                            
                            nn.Flatten()
                        )
            elif key == "vector":
                # Run through a simple MLP
                extractors[key] = nn.Linear(subspace.shape[0], 16)

        self.extractors = nn.ModuleDict(extractors)

        # Update the features dim manually
        total_concat_size = 288 + 16
        self._features_dim = total_concat_size

    def forward(self, observations) -> torch.Tensor:
        encoded_tensor_list = []

        # self.extractors contain nn.Modules that do all the processing.
        for key, extractor in self.extractors.items():
            encoded_tensor_list.append(extractor(observations[key]))
        # Return a (B, self._features_dim) PyTorch tensor, where B is batch dimension.
            output = torch.cat(encoded_tensor_list, dim=1)
        #print("Feature extractor output shape:", output.shape[1])  # Debugging
        assert output.shape[1] == self._features_dim
        return output


class BallmazeReplayBuffer(DictReplayBuffer):
    def __init__(self, buffer_size, observation_space, action_space, maze_layout, device = "auto", n_envs = 1, optimize_memory_usage = False, handle_timeout_termination = True):
        self.maze_layout = maze_layout
        observation_space_small = spaces.Dict({
            'image': spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32),
            'vector': observation_space.spaces['vector']
        })
        super().__init__(buffer_size, observation_space_small, action_space, device, n_envs, optimize_memory_usage, handle_timeout_termination)

    def image_small_to_image(self, obs_img_small): # TODO: vectorize maze_layout.get_surrounding_img
        obs_img_small_np = obs_img_small.numpy(force=True)
        #img_np = self.maze_layout.get_surrounding_img(obs_img_small_np)
        all_img_np = np.array([self.maze_layout.get_surrounding_img(obs_img_small_np[i]) for i in range(len(obs_img_small_np))])
        all_img_np = all_img_np.transpose(0, 3, 1, 2)
        return torch.tensor(all_img_np, dtype=obs_img_small.dtype, device=obs_img_small.device)
    
    def add(
        self,
        obs: dict[str, np.ndarray],
        next_obs: dict[str, np.ndarray],
        action: np.ndarray,
        reward: np.ndarray,
        done: np.ndarray,
        infos: list[dict[str, Any]],
    ) -> None:
        assert len(obs["image"]) == 1, "Batch-adding not added to the BallmazeReplayBuffer not implemented"
        position = infos[0]["position"]
        last_position = infos[0]["last_position"]
        #assert round(last_position[0]*100) == obs["image"][0,0,0,0], "only for Dummy-env, delete in use"
        #assert round(position[0]*100) == next_obs["image"][0,0,0,0], "only for Dummy-env, delete in use"
        obs_small = OrderedDict([("image", last_position), ("vector", obs["vector"])])
        next_obs_small = OrderedDict([("image", position), ("vector", next_obs["vector"])])
        super().add(obs_small, next_obs_small, action, reward, done, infos)
    
    def sample(
        self,
        batch_size: int,
        env: Optional[VecNormalize] = None,
    ) -> DictReplayBufferSamples:
        sample_small =  super().sample(batch_size, env=env)
        obs_img_small = sample_small.observations["image"]
        obs_img = self.image_small_to_image(obs_img_small)
        obs = {"image": obs_img, "vector": sample_small.observations["vector"]}
        next_obs_img_small = sample_small.next_observations["image"]
        next_obs_img = self.image_small_to_image(next_obs_img_small)
        next_obs = {"image": next_obs_img, "vector": sample_small.next_observations["vector"]}
        sample = DictReplayBufferSamples(obs, sample_small.actions, next_obs, sample_small.dones, sample_small.rewards)
        return sample



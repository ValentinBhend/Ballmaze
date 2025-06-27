import gymnasium as gym
import numpy as np

class CNN_dummy_env(gym.Env):
    def __init__(self):
        low_vec = np.array([0.0, 0.0, -1.0, -1.0], dtype=np.float32)
        high_vec = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)

        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

        self.observation_space = gym.spaces.Dict({
            'image': gym.spaces.Box(low=0, high=255, shape=(29, 29, 3), dtype=np.uint8), # np.uint8
            'vector': gym.spaces.Box(low=low_vec, high=high_vec, dtype=np.float32)
        })

    def step(self, actions):
        self.current_timestep += 1
        self.last_position = self.position
        self.position = np.array([self.current_timestep / 100, self.current_timestep / 100])
        reward = np.random.rand() + np.mean(actions)
        terminated = truncated = False
        if self.current_timestep > 90:
            terminated = True
        return self._get_obs(), float(reward), terminated, truncated, self._get_info()
        
    def reset(self, seed=None, options=None):
        self.current_timestep = 0
        self.position = np.array([self.current_timestep / 100, self.current_timestep / 100])
        self.last_position = np.array([self.current_timestep / 100, self.current_timestep / 100])
        return self._get_obs(), self._get_info()

    def _get_obs(self):
        obs1 = np.random.rand(2)
        obs2 = np.random.rand(2) * 2 - 1
        obs_vec = np.concatenate((obs1, obs2)).astype(np.float32)
        obs_img = np.ones((29, 29, 3)).astype(np.uint8) # np.uint8
        obs_vec[0] = self.current_timestep / 100
        obs_img[0,0,0] = self.current_timestep

        obs = {
            'image': obs_img,
            'vector': obs_vec
        }

        return obs
    
    def _get_info(self):
        return {"position": self.position, "last_position": self.last_position}


if __name__ == "__main__": # Example usage
    from stable_baselines3 import SAC
    from stable_baselines3.common.env_checker import check_env
    from stable_baselines3.common.evaluation import evaluate_policy
    from stable_baselines3.common.monitor import Monitor
    env = Monitor(CNN_dummy_env())
    check_env(env)
    model = SAC("MultiInputPolicy", env, verbose=2, device="cpu", buffer_size=10000) # the default buffer_size of 1e6 needs too much memory. Maybe create a costum replay buffer class with compression of one-hot encoded channels. 
    model.learn(total_timesteps=1000)
    model.policy.set_training_mode(False)
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=2)
    print(f"mean_reward: {mean_reward}, std_reward, {std_reward}")
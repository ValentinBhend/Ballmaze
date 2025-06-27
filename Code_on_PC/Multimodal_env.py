from TCPClient import TCPClient
import gymnasium as gym
import numpy as np
import sys
import time
import cv2
import matplotlib.pyplot as plt
import csv

class env_multimodal(gym.Env):
    MAX_TIMESTEP = 1500#250
    STEP_REWARD = -0.001#-0.01
    SAME_PUNISH = -0.01
    NO_MOVE_PUNISH = -0.01
    END_REWARD = -4
    BACKWARDS_MULTIPLIER = 1.02 # > 1
    DONE_REWARD = 10

    def __init__(self, maze_layout, plot=False, save_steps=False, save_img=False, Pi5=False):
        self.maze_layout = maze_layout
        self.plot = plot
        self.save_steps = save_steps
        self.save_img = save_img
        self.Pi5 = Pi5
        self.recorded_angles = 40 if Pi5 else 8
        if save_steps:
            print(f"\033[31mSave to csv not tested yet\033[0m")
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        self.observation_space = gym.spaces.Dict({
            'image': gym.spaces.Box(low=0, high=255, 
                                    shape=(self.maze_layout.surrounding_img_size, self.maze_layout.surrounding_img_size, 3), dtype=np.uint8),
            'vector': gym.spaces.Box(low=-1.0, high=1.0, shape=(self.recorded_angles,), dtype=np.float32)
        })

        self.pi = TCPClient() # PiIP="192.168.105.150" replace with Pi IP
        if self.plot:
            self.init_plot()
        if self.save_steps:
            self.init_savefile()

        self.t1 = self.t2 = self.t3 = self.t4 = time.time() # temp for benchmarking
        self.t_steps = []
    
    def init_plot(self):
        self.plot_rewards = []
        self.plot_timesteps = []
        self.fig = plt.figure(figsize=(8, 6))
        gs = self.fig.add_gridspec(2, 2, height_ratios=[1, 3])
        self.ax_reward = self.fig.add_subplot(gs[0, :])
        #fig, (ax_full, ax_part) = plt.subplots(1, 2) # , figsize=(10, 5)
        ax_full = self.fig.add_subplot(gs[1, 0])
        ax_part = self.fig.add_subplot(gs[1, 1])
        ax_full.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, left=False, right=False, labelleft=False)
        ax_part.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, left=False, right=False, labelleft=False)
        self.ax_reward.set_xlabel("Timesteps")
        self.ax_reward.set_ylabel("Total reward")
        #self.ax_reward.set_ylim(-2, 2)
        ax_full.set_title("Position in maze")
        ax_part.set_title("Agent view")
        self.fig.patch.set_facecolor('#87cefa')
        #ax_reward.plot(self.plot_timesteps, self.plot_rewards, marker='o', color='blue')
        self.line_reward, = self.ax_reward.plot(self.plot_timesteps, self.plot_rewards, 
                                                marker='o', color='blue', 
                                                markersize=2, linewidth=0.8)
        self.ax_reward.axhline(y=0, color='gray', linestyle='dashed', linewidth=1)
        self.plot_img_full = ax_full.imshow(self.maze_layout.empty_full_img)
        self.plot_img_part = ax_part.imshow(self.maze_layout.get_surrounding_img([1,0]))
        plt.ion()
        plt.tight_layout()
        plt.show()
    
    def init_savefile(self):
        self.csv_filename = f"steps_replay_multimodal_{int(time.time())}"
        header = ["position_x", "position_y", "move_x", "move_y", "reward"]
        with open(self.csv_filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    
    def append_csv(self, action, reward):
        if self.position is None:
            #print("WROTE DUMMY CSV, Position is None")
            row = [-1,-1,-1,-1,-1]
        else:
            row = [*self.position, *action, reward]
        with open(self.csv_filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def update_plot(self):
        self.plot_rewards.append(self.total_reward)
        self.plot_timesteps.append(self.current_timestep)
        self.line_reward.set_data(self.plot_timesteps, self.plot_rewards)
        self.ax_reward.relim()
        self.ax_reward.autoscale_view()
        self.ax_reward.set_ylim(min(-2,min(self.plot_rewards)*1.1), max(2,max(self.plot_rewards)*1.1))
        if self.position is not None:
            self.plot_img_full.set_data(self.maze_layout.get_plot_img(self.position))
            self.plot_img_part.set_data(self.maze_layout.get_surrounding_img(self.position))
        #plt.draw()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.00001) # this is needed, otherwise pyplot will not show it

    def box_reward(self):
        new_box_reward = self.maze_layout.get_box_reward(self.position)
        if new_box_reward == 0: # value for walls & holes
            return 0
        reward = new_box_reward - self.last_box_reward
        if reward > 10: # likely wrong image detection
            return 0
        self.last_box_reward = new_box_reward
        if reward < 0:
            return reward * self.BACKWARDS_MULTIPLIER
        else:
            return reward
    
    def rescale_actions_smooth(self, actions_normalized):
        max_step = 0.08 if self.Pi5 else 1.0
        ax, ay = actions_normalized
        x0, y0 = self.last_angles
        x1 = x0 + ax * max_step
        y1 = y0 + ay * max_step
        x1 = min(1, max(-1, x1))
        y1 = min(1, max(-1, y1))
        return np.array([x1,y1])
    
    def get_position(self, retries=8):
        for i in range(retries):
            new_pos = self.pi.get_position()
            if new_pos is not None:
                return new_pos
        return new_pos
    
    def send_actions_get_position(self, actions, retries=8):
        same_punish = 0
        actions_rescaled = self.rescale_actions_smooth(actions)
        if np.array_equal(self.last_angles, actions_rescaled):
            same_punish = self.SAME_PUNISH
        self.last_angles = actions_rescaled
        speed = 50 if self.Pi5 else 3.5
        #print(f"sending act: {actions_rescaled}")
        new_pos = self.pi.set_xy_get_position(*actions_rescaled, speed=speed, save_img=self.save_img)
        if new_pos is None:
            return self.get_position(retries=retries-1), same_punish
        return new_pos, same_punish

    def step(self, actions):
        t = time.time()
        self.t_steps.append(t-self.t1)
        self.t1 = t

        reward = self.STEP_REWARD
        terminated = truncated = False
        self.current_timestep += 1
        #print(f"ENV TIME: {(self.t1-self.t2)*1000}ms")
        self.last_position = self.position.copy()
        self.t2 = time.time()
        self.position, same_punish = self.send_actions_get_position(actions)
        self.t3 = time.time()
        #self.t2 = time.time()
        #print(f"PI INTERATCTION TIME: {(self.t2-self.t1)*1000}ms")

        if self.maze_layout.special_variables["no_hole"]:
            if (self.position is None) and (self.last_box_reward >= 90):
                terminated = True
                reward = self.DONE_REWARD + (99 - self.last_box_reward)
            elif self.position is None:
                print("WARNING: POSITION IS NONE")
            else:
                reward += self.box_reward()
                if self.current_timestep > self.MAX_TIMESTEP:
                    truncated = True
        else:
            if self.position is None:
                terminated = True
                reward = self.END_REWARD
            else:
                reward += self.box_reward()
                if self.current_timestep > self.MAX_TIMESTEP:
                    truncated = True
        
        reward += same_punish

        if (self.last_position is not None) and (self.position is not None):
            if np.linalg.norm(self.last_position - self.position) < 0.0001:
                reward += self.NO_MOVE_PUNISH
                #print(f"nomove {np.linalg.norm(self.last_position - self.position)}")

        self.total_reward += reward
        
        if self.plot:
            self.update_plot()

        #print(f"step reward: {reward}")
        if self.save_steps:
            self.append_csv(actions, reward)
        
        obs = self._get_obs()
        info = self._get_info()

        t_alg = self.t1 - self.t4
        self.t4 = time.time()
        t_env = (self.t2 - self.t1) + (self.t4 - self.t3)
        t_pi = self.t3 - self.t2
        #print(f"alg: {1000*t_alg:.3f}ms, env: {1000*t_env:.3f}ms, pi: {1000*t_pi:.3f}ms")
        #print(self.current_timestep)
        # if (t_pi > 0.05) and not (terminated or truncated):
        #     print(f"Pi time: {t_pi*1000}ms at timestep {self.current_timestep}")
        return obs, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        if len(self.t_steps) > 10:
            trimmed = sorted(self.t_steps, reverse=True)[5:]
            t_avg = sum(trimmed) / len(trimmed)
            print(f"Episode fps = {1/t_avg:.1f}")
        self.t_steps = []
        self.plot_rewards = []
        self.plot_timesteps = []
        self.current_timestep = 0
        self.total_reward = 0
        self.max_box_reward = 0
        self.last_angles = np.array([0.62, 0.24])
        self.angles_buffer = np.zeros(self.recorded_angles, dtype=np.float32)
        self.position = self.pi.reset()
        self.last_position = self.position.copy()
        self.last_box_reward = self.maze_layout.get_box_reward(self.position)
        if self.plot:
            self.update_plot()
        if self.position is None:
            print("SHOULD NOT HAPPEN, PI RESET WRONG")
        return self._get_obs(), self._get_info()
    
    def update_angles_buffer(self):
        new_angles = self.last_angles.astype(np.float32)
        new_buffer = np.zeros(self.recorded_angles, dtype=np.float32)
        new_buffer[:self.recorded_angles-2] = self.angles_buffer[2:]
        new_buffer[self.recorded_angles-2:] = new_angles
        self.angles_buffer = new_buffer.copy()

    def _get_obs(self):
        self.update_angles_buffer() 
        obs_vec = self.angles_buffer.astype(np.float32)
        if self.position is None:
            self.position = self.last_position.copy()
        obs_img = self.maze_layout.get_surrounding_img(self.position)
        obs = {
            'image': obs_img,
            'vector': obs_vec
        }
        return obs
    
    def _get_info(self):
        if self.position is None:
            self.position = self.last_position.copy()
        if self.last_position is None:
            print(f"WARNING: last position is None (pos: {self.position}, timestep: {self.current_timestep})")
        return {"position": self.position, "last_position": self.last_position}
    
    def close(self): # not used, try if there are problems with model.save in stable-baselines3
        pass
        plt.ioff()       
        plt.close('all')
        self.pi = None
        plt.ioff()
        plt.pause(1)
        plt.close('all')
        plt.pause(1)
        time.sleep(1)


if __name__ == "__main__": # Usage example
    from Multimodal_maze_layout import Maze_layout
    maze_layout = Maze_layout()
    env = env_multimodal(maze_layout, plot=True)
    env.reset()

    env.step([0,0])

    for _ in range(1000):
        act = np.random.rand(2)*2-1
        print(act)
        obs, reward, terminated, truncated, info = env.step(act)
        time.sleep(0.25)
        if terminated or truncated:
            print("reset")
            obs, info = env.reset()
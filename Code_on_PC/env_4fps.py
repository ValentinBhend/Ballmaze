from pi_interactions import Pi
import gymnasium as gym
import numpy as np
import sys
import time
import cv2
import matplotlib.pyplot as plt
import csv

class env_4fps(gym.Env):
    MAX_TIMESTEP = 300
    STEP_REWARD = -0.01
    
    BOX_REWARD_ARRAY = np.array([[28,27,26, 0,22,21,20,17,16, 0], 
                                 [29, 0,25,24,23,20,19,18,15,14], 
                                 [30,63,63, 0,60,59,58,11,12,13], 
                                 [31, 0,63,62,61,56,57,10, 0,13], 
                                 [32,64,64, 0,55,55, 0, 9, 8, 7], 
                                 [33,34,65,66, 0,54,53, 0, 5, 6], 
                                 [ 0,35,74,67,68,69,52, 0, 4, 3], 
                                 [37,36,73,72,71,70,51,50, 0, 2], 
                                 [38, 0,42,43, 0, 0,50,49, 0, 1], 
                                 [39,40,41,44,45,46,47,48,48, 0]])
    BOX_REWARD_ARRAY = np.flip(np.transpose(BOX_REWARD_ARRAY), axis=1)
    MAX_REWARD = np.max(BOX_REWARD_ARRAY)

    def __init__(self, plot=False, save_steps=False, smooth=True):
        self.plot = plot
        self.save_steps = save_steps
        self.smooth = smooth
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        low = np.array([0.0, 0.0, -1.0, -1.0], dtype=np.float32)
        high = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.observation_space = gym.spaces.Box(low=low, high=high, dtype=np.float32)

        self.current_timestep = 0
        self.total_reward = 0
        self.max_box_reward = 0
        self.position = None
        self.pi = Pi()
        self.get_transformation()
        if self.plot:
            self.init_plot()
        if self.save_steps:
            self.init_savefile()
        #self.reset()

        self.t1 = self.t2 = self.t3 = time.time() # temp
    
    def init_plot(self):
        #print("init plot")
        fig, ax_sim = plt.subplots(1, 1) # , figsize=(10, 5)
        self.empty_sim_img = self.init_sim_img()
        self.plot_img_sim = ax_sim.imshow(self.empty_sim_img)
        plt.ion()
        plt.show()
    
    def init_savefile(self):
        self.csv_filename = f"steps_replay_5fps_{int(time.time())}"
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
    
    def init_sim_img(self):
        img = np.rot90(cv2.imread("maze1.png")) #cv2.cvtColor()
        return img

    def update_plot(self):
        self.plot_img_sim.set_data(self.get_sim_image())
        plt.draw()
        plt.pause(0.00001) # this is needed, otherwise pyplot will not show it :/
    
    def get_sim_image(self):
        img = self.empty_sim_img.copy()
        if self.position is None:
            #print("cant generate sim image, because position is None")
            return img
        x,y = self.position
        imsz = len(self.empty_sim_img)
        x_mid, y_mid = int(x*imsz), int(y*imsz)
        x0 = max(0,x_mid-5)
        y0 = max(0,y_mid-5)
        x1 = min(imsz,x_mid+5)
        y1 = min(imsz,y_mid+5)
        img[imsz-y1:imsz-y0, x0:x1] = (255,0,0)
        return img

    def get_transformation(self): # coordinate transformation from camera to [0,1]^2
        # corners measured from camera:
        pts_src = np.array([
            [0.9103, 0.92708],  # bottom left
            [0.9389, 0.10522],  # bottom right
            [0.10044, 0.085284],  # top right
            [0.083152, 0.91596]   # top left
        ], dtype="float32")
        # corners in sim
        r_ball = 3 / 100
        pts_dst = np.array([
            [1-r_ball, r_ball],      # point a'
            [1-r_ball, 1-r_ball], # TODO: check if BR & TL switched
            [r_ball, 1-r_ball],      # point c'
            [r_ball, r_ball]       # point d'
        ], dtype="float32")
        self.perspective_transform_matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)

    def end_reward(self):
        return -3

    def box_reward(self):
        x,y = self.position
        #t = lambda x: round((x/self.GRIDSIZE - 2.5)/4)
        tx, ty = int(x*10), int(y*10)
        tx, ty = int(min(9,max(0,tx))), int(min(9,max(0,ty)))
        new_box_reward = self.BOX_REWARD_ARRAY[tx,ty]
        #print(f"currently in reward-box: {new_box_reward}")
        if new_box_reward >= self.max_box_reward:
            #print(new_box_reward, self.max_box_reward)
            reward = (new_box_reward - self.max_box_reward) # / self.MAX_REWARD
            if reward > 10: # prevents wrong position detections (& also hole skipping)
                return 0
            self.max_box_reward = new_box_reward
            self.last_reward = new_box_reward
            return reward
        else:
            reward = (new_box_reward - self.last_reward) / 20 # negative
            reward = min(0,reward)
            self.last_reward = new_box_reward
            return reward
    
    def xywhn_to_position(self, xywhn):
        if xywhn is None:
            return None
        x,y,w,h = xywhn
        pt = np.array([ [x, y] ], dtype="float32")
        # cv2.perspectiveTransform expects an array of shape (N, 1, 2)
        pt = np.array([pt])
        pt_transformed = cv2.perspectiveTransform(pt, self.perspective_transform_matrix)
        x,y = pt_transformed[0, 0]
        return [x,y]
    
    def rescale_actions_smooth(self, actions_normalized):
        max_step = 0.4
        ax, ay = actions_normalized
        x0, y0 = self.last_angles
        x1 = x0 + ax * max_step
        y1 = y0 + ay * max_step
        x1 = min(1, max(-1, x1))
        y1 = min(1, max(-1, y1))
        return np.array([x1,y1])
    
    def send_actions(self, actions):
        if self.smooth:
            actions_rescaled = self.rescale_actions_smooth(actions)
        else:
            actions_rescaled = actions
        self.last_angles = actions_rescaled
        response = self.pi.set_xy(*actions_rescaled)
    
    def get_position(self, retries=3):
        for i in range(retries):
            xywhn = self.pi.get_position()
            new_pos = self.xywhn_to_position(xywhn)
            if new_pos is not None:
                return new_pos
        return new_pos
    
    def send_actions_get_position(self, actions, retries=3):
        if self.smooth:
            actions_rescaled = self.rescale_actions_smooth(actions)
        else:
            actions_rescaled = actions
        self.last_angles = actions_rescaled
        xywhn = self.pi.set_xy_get_position(*actions_rescaled)
        new_pos = self.xywhn_to_position(xywhn)
        if new_pos is None:
            return self.get_position(retries=retries-1)
        return new_pos


    def step(self, actions):
        assert not np.array_equal(self.position, np.array([0.5, 0.5])), "ERROR: dummy position value encountered in env-STEP (0.5, 0.5)" # temp
        reward = self.STEP_REWARD
        terminated = truncated = False
        self.current_timestep += 1
        #self.t1 = time.time()
        #print(f"ENV TIME: {(self.t1-self.t2)*1000}ms")
        #self.send_actions(actions)
        #self.position = self.get_position()
        self.position = self.send_actions_get_position(actions)
        #self.t2 = time.time()
        #print(f"PI INTERATCTION TIME: {(self.t2-self.t1)*1000}ms")
        if self.position is None:
            terminated = True
            reward = self.end_reward()
        else:
            reward += self.box_reward()
            if self.current_timestep > self.MAX_TIMESTEP:
                truncated = True
            self.total_reward += reward
        
        if self.plot:
            self.update_plot()

        #print(f"step reward: {reward}")
        if self.save_steps:
            self.append_csv(actions, reward)
        
        return self._get_obs(), reward, terminated, truncated, self._get_info()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_timestep = 0
        self.total_reward = 0
        self.max_box_reward = 0
        self.last_reward = 0
        self.last_angles = np.array([0.62, 0.24])
        xywhn = self.pi.reset()
        self.position = self.xywhn_to_position(xywhn)
        if self.plot:
            self.update_plot()
        if self.position is None:
            print("SHOULD NOT HAPPEN, PI RESET WRONG")
        return self._get_obs(), self._get_info()

    def _get_obs(self):
        if self.position is None:
            pos = np.array([0.5, 0.5]) # dummy value, maybe solve differently
        else:
            pos = self.position
        obs = np.array([*pos, *self.last_angles], dtype=np.float32)
        assert len(obs) == 4, "something wrong with observation"
        #print(f"current obs: {obs}")
        return obs
    
    def _get_info(self):
        return {}
    
    def close(self): # not used, try if there are problems with model.save in stable-baselines3
        plt.ioff()       
        plt.close('all')
        self.empty_sim_img = None
        self.plot_img_sim = None
        self.pi = None
        self.perspective_transform_matrix = None
        plt.ioff()
        plt.pause(1)
        plt.close('all')
        plt.pause(1)
        time.sleep(1)


if __name__ == "__main__":
    env = env_4fps(plot=True)
    env.reset()
    #env.box_reward()
    for _ in range(20):
        act = np.random.rand(2)*2-1
        print(f"act: {act}")
        obs, reward, terminated, truncated, info = env.step(act)
        if terminated or truncated:
            env.reset()
    #env.step(np.array([.4,.85]))
    #env.step(np.array([.6,.2]))
    #env.step(np.array([.8,.1]))
    #speed_test()
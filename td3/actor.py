import os
import yaml
import pickle
from os.path import join, dirname, abspath, exists
import sys
sys.path.append(dirname(dirname(abspath(__file__))))
import torch
import gym
import numpy as np
import random
import time
import rospy
import argparse
import logging

from tianshou.exploration import GaussianNoise
from tianshou.data import Batch

from policy import TD3Policy, SACPolicy
from train import initialize_envs, initialize_policy
from envs import registration
from envs.wrappers import ShapingRewardWrapper

BUFFER_PATH = os.getenv('BUFFER_PATH')

def initialize_actor(id):
    rospy.logwarn(">>>>>>>>>>>>>>>>>> actor id: %s <<<<<<<<<<<<<<<<<<" %(str(id)))
    assert os.path.exists(BUFFER_PATH)
    actor_path = join(BUFFER_PATH, 'actor_%s' %(str(id)))

    if not exists(actor_path):
        os.mkdir(actor_path) # path to store all the trajectories

    f = None
    while f is None:
        try:
            f = open(join(BUFFER_PATH, 'config.yaml'), 'r')
        except:
            rospy.logwarn("wait for critor to be initialized")
            time.sleep(2)

    config = yaml.load(f, Loader=yaml.FullLoader)

    return config

def load_model(model):
    model_path = join(BUFFER_PATH, 'policy.pth')
    state_dict = {}
    state_dict_raw = None
    count = 0
    while (state_dict_raw is None) and count < 10:
        try:
            state_dict_raw = torch.load(model_path, map_location=torch.device('cpu'))
        except:
            time.sleep(2)
            pass
        time.sleep(2)
        count += 1

    if state_dict_raw is None:
        raise FileNotFoundError("critic not initialized at %s" %(BUFFER_PATH))

    model.load_state_dict(state_dict_raw)
    model = model.float()
    # exploration noise std
    with open(join(BUFFER_PATH, 'eps.txt'), 'r') as f:
        eps = None
        count = 0
        while (eps is None) and count < 10:
            try:
                eps = float(f.readlines()[0])
            except IndexError:
                pass
            time.sleep(2)
            count += 1

    if eps is None:
        raise FileNotFoundError("critic not initialized at %s" % BUFFER_PATH)

    return model, eps 

def write_buffer(traj, ep, id):
    with open(join(BUFFER_PATH, 'actor_%s' %(str(id)), 'traj_%d.pickle' %(ep)), 'wb') as f:
        pickle.dump(traj, f)

def get_world_name(config, id):
    if len(config["condor_config"]["worlds"]) < config["condor_config"]["num_actor"]:
        duplicate_time = config["condor_config"]["num_actor"] // len(config["condor_config"]["worlds"]) + 1
        worlds = config["condor_config"]["worlds"] * duplicate_time
    else:
        worlds = config["condor_config"]["worlds"].copy()
        random.shuffle(worlds)
        worlds = worlds[:config["condor_config"]["num_actor"]]
    world_name = worlds[id]
    if isinstance(world_name, int):
        world_name = "BARN/world_%d.world" %(world_name)
    return world_name

def _debug_print_robot_status(env, count, rew):
    Y = env.move_base.robot_config.Y
    X = env.move_base.robot_config.X
    p = env.gazebo_sim.get_model_state().pose.position
    print('current step: %d, X position: %f(world_frame), %f(odem_frame), Y position: %f(world_frame), %f(odom_frame), rew: %f' %(count, p.x, X, p.y, Y , rew))

def main(id):
    config = initialize_actor(id)
    env_config = config['env_config']
    world_name = get_world_name(config, id)
    env_config["kwargs"]["world_name"] = world_name
    env = gym.make(env_config["env_id"], **env_config["kwargs"])
    if env_config["shaping_reward"]:
        env = ShapingRewardWrapper(env)

    policy, _ = initialize_policy(config, env)

    print(">>>>>>>>>>>>>> Running on %s <<<<<<<<<<<<<<<<" %(world_name))
    ep = 0
    while True:
        obs = env.reset()
        obs_batch = Batch(obs=[obs], info={})
        ep += 1
        traj = []
        done = False
        policy, eps = load_model(policy)
        try:
            policy.set_exp_noise(GaussianNoise(sigma=eps))
        except:
            pass
        while not done:
            p = random.random()
            obs = torch.tensor([obs]).float()
            if isinstance(policy._noise, GaussianNoise) or p > eps:
                actions = policy(obs_batch).act.cpu().detach().numpy().reshape(-1)
            else:
                actions = get_random_action()
                actions = np.array(actions)
            obs_new, rew, done, info = env.step(actions)
            info["world"] = world_name
            traj.append([obs, actions, rew, done, info])
            obs_batch = Batch(obs=[obs_new], info={})
            obs = obs_new

            # _debug_print_robot_status(env, len(traj), rew)

        write_buffer(traj, ep, id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'start an actor')
    parser.add_argument('--id', dest='actor_id', type = int, default = 1)
    id = parser.parse_args().actor_id
    main(id)

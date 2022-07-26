import random

import plotly.io as pio
import yaml

from BoxEventEnv import BoxEventEnv
from utils.utils import parse_file

pio.renderers.default = "browser"

if __name__ == '__main__':

    with open("/home/S3G-LABS/u1226/dev/openchests/config/config.yaml", "r") as f:
        conf = yaml.safe_load(f)

    all_event_types = conf["EVENT_TYPES"]
    all_event_attributes = conf["EVENT_ATTRIBUTES"]

    all_instructions = []
    for file in conf["INSTRUCTIONS"]:
        instr = parse_file("config/patterns/" + file)
        all_instructions.append(instr)
        print(instr)

    env = BoxEventEnv(instructions=all_instructions,
                      all_event_types=all_event_types,
                      all_event_attributes=all_event_attributes,
                      verbose=False)

    verbose_env = BoxEventEnv(instructions=all_instructions,
                              all_event_types=all_event_types,
                              all_event_attributes=all_event_attributes,
                              verbose=True)

    from stable_baselines3 import A2C
    from stable_baselines3.common.env_util import make_vec_env

    # Instantiate the env
    # wrap it
    env = make_vec_env(lambda: env, n_envs=1)
    verbose_env = make_vec_env(lambda: verbose_env, n_envs=1)

    # Train the agent
    print("Learning")
    model = A2C('MultiInputPolicy', env, verbose=1).learn(5000)
    #model = A2C('MultiInputPolicy', env, verbose=1)

    # Test the trained agent
    obs = verbose_env.reset()
    verbose_env.render()
    n_steps = 100
    print("------------------------ START -------------------------")
    for step in range(n_steps):
        action, _ = model.predict(obs, deterministic=True)
        sure_action = [[1, 1]]
        empty_action = [[0, 0]]
        random_action = [[random.randint(0, 1) for i in range(2)]]
        print("Step {}".format(step + 1))
        print("Action: ", action)
        obs, reward, done, info = verbose_env.step(action)
        verbose_env.render()
        print('obs =', obs, 'reward=', reward, 'done=', done)
        # env.render(mode='console')
        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break

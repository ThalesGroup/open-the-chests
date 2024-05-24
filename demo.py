from openthechests.src.OpenTheChestsGym import OpenTheChestsGym

if __name__ == '__main__':
    conf = "./docs/examples/create_env/example_config/multiple_per_box.yaml"
    env = OpenTheChestsGym.from_config_file(env_config_file=conf,
                                            verbose=False)
    discrete_env = OpenTheChestsGym.from_config_file(env_config_file=conf,
                                                     verbose=False,
                                                     discrete=True)
    verbose_env = OpenTheChestsGym.from_config_file(env_config_file=conf,
                                                    verbose=True)

    n_steps = 200
    print("------------------------ START -------------------------")
    print("Type \"quit\" to exit the game.")
    obs = env.reset()

    format_obs = lambda d: (
        f"\n"
        f"  Boxes:\n"
        f"      Active: {d['active']}\n"
        f"      Open: {d['open']}\n"
        f"  Event:\n"
        f"      Type: {d['e_type']}\n"
        f"      Background: {d['bg']}\n"
        f"      Foreground: {d['fg']}\n"
        f"      Start: {d['start']}\n"
        f"      End: {d['end']}\n"
        f"      Duration: {d['duration']}"
    )

    print(f"First observation {format_obs(obs)}.")

    user_input = ""
    num_boxes = env.env.get_num_boxes()
    while True:
        print(f"Select an action under the form of a binary vector of length {num_boxes}.")
        print(f"For example {verbose_env.action_space.sample()}")
        user_input = input()
        if user_input == "quit":
            break
        action = list(map(int, user_input.strip("[]").split()))

        if not (len(action) == 3 and all(isinstance(a, int) for a in action)):
            print(f"Input is incorrect. Gor {action}, expected list of {num_boxes} ints.")
            action = verbose_env.action_space.sample()
            print(f"Executing {action} instead.")

        obs, reward, done, info = env.step(action)
        print(f"Observation {format_obs(obs)}.")
        print(f"Reward {reward}.")

        if done:
            # Note that the VecEnv resets automatically
            # when a done signal is encountered
            print("Goal reached!", "reward=", reward)
            break

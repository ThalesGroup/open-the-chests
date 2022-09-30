# Open The Chests Project

Open the Chests is a game that mimics the problem of situation recognition in a concurrent event based environment.
The player is confronted with a number of boxes, each one associated to a button. Pressing on a button sometimes leads 
to a box opening, sometimes leads to nothing. The player also observes events being displayed on a screen.
The goal of the player is to deduce a set of interpretable event based rules that allow to determine with confidence 
at which moment the chests can be opened.

## Quick Start

To install all libraries needed to execute the environment simply run:
`pip install -r requirements.txt`

The environment is then ready to execute by simply running the `main.py` file.
The execution of the main file generates an environment using a `YAML` configuration 
file and then trains one of four algorithms: A2C, DQN, PPO, TRPO.
The output of the main file can be configured by a set of parameters.

  - `env_config` The name of configuration file that defines an environment configuration.
    `Default value: one_per_box.yaml`
  
  - `discrete` Use discrete action input instead of a vector of binary values.
    `Default value: False`
  
  - `model` Model used to train on the environment. Current options : A2C, DQN, PPO, TRPO
    `Default value: PPO`
  
  - `verbose_train` Use verbose mode when training model to get feedback.
    `Default value: False`
  
  - `train_steps` Number of steps to train model.
    `Default value: 100000`
  
  - `plot_training` Plot reward per step after training.
    `Default value: True`
  
  - `num_episodes_eval` Number of episodes over which to evaluate environment.
    `Default value: 100`
  
  - `show_one_episode` Render one episode play trough using the trained model.
    `Default value: False`
  
  - `results_file` Render one episode play trough using the trained model.
    `Default value: test_results`

## Folder description
In the `openthechests` module there are several folders and files of
interest.

The `BoxEventEnv.py` contains the `gym` wrapper of the environment, however the environment code
is actually in the `openthechests.source.env` module. In this repository we have the following folders:

- **config**: is a folder with example configurations for multiple environments.

We have a `YAML` file for each environment, along with a folder with the same name containing other files, 
describing the situations to be played in the corresponding environment.

- **excog_experiments**: contains the scripts related to `excog` experiments. 
 
We have the `Script.py` file that allows to run the experiments, the `Process.py` that allows
to define the code of each process to be run by `excog`, **data** - a folder giving the data to be used for experiments.
The data folder allows to simply give the name of the configuration files to use for each environment. And finally,
we have `final_config.yaml` that allows to define the configuration to use for `excog`.

- **openthechests**: is the main code for the environment.

It contains the folder **examples** that shows how to use the classes used to build the environment.
It also has a folder **models** where the models used for the main file are stored, if it's needed to any specific model parameters, 
this would be the place to add them. A folder **scripts** allows visualising any of the obtained results and finally
the **src** folder that contains most of the environment code that we will detail now. There are also a couple of python scripts, 
including the `main.py` file and other similar files used for testing and demo purposes.

### The `src` folder

- An **env** folder with the main environment elements separated in classes.
- An **outdated** folder that contains old unused code that might be interesting to keep.
- An **utils** folder that defines useful functions used by the other modules.





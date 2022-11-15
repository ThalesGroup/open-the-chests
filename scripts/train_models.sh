python main.py --env_config one_per_box.yaml --model PPO --results_file delay_variation3
python main.py --env_config one_per_box.yaml --model TRPO --results_file delay_variation3
python main.py --env_config one_per_box.yaml --model A2C --results_file delay_variation3
python main.py --env_config one_per_box.yaml --model  DQN --discrete True --results_file delay_variation3

python main.py --env_config one_distinct_per_box.yaml --model PPO --results_file delay_variation3
python main.py --env_config one_distinct_per_box.yaml --model TRPO --results_file delay_variation3
python main.py --env_config one_distinct_per_box.yaml --model A2C --results_file delay_variation3
python main.py --env_config one_distinct_per_box.yaml --model  DQN --discrete True --results_file delay_variation3

python main.py --env_config multiple_per_box.yaml --model PPO --results_file delay_variation3
python main.py --env_config multiple_per_box.yaml --model TRPO --results_file delay_variation3
python main.py --env_config multiple_per_box.yaml --model A2C --results_file delay_variation3
python main.py --env_config multiple_per_box.yaml --model  DQN --discrete True --results_file delay_variation3

python main.py --env_config noise_two_per_box.yaml --model PPO --results_file delay_variation3
python main.py --env_config noise_two_per_box.yaml --model TRPO --results_file delay_variation3
python main.py --env_config noise_two_per_box.yaml --model A2C --results_file delay_variation3
python main.py --env_config noise_two_per_box.yaml --model  DQN --discrete True --results_file delay_variation3
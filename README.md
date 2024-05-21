# Open The Chests Project

Open the Chests is a game that mimics the problem of situation recognition in a concurrent event-based environment.
The player is confronted with a number of boxes, each one associated with a button. Pressing a button sometimes leads 
to a box opening, sometimes leads to nothing. The player also observes events being displayed on a screen.
The goal of the player is to deduce a set of interpretable event-based rules that allow them to determine with confidence 
at which moment the chests can be opened.

## Quick Start

To install all libraries needed to execute the environment simply run:
```shell
pip install -r requirements.txt
```
The environment is then ready to execute by simply running the `demo.py` file.

## Running the Demo
The execution of the demo file generates an environment using a `YAML` configuration
file and allows you to interact with the environment manually.
To run the demo, use the following command:
```shell
python demo.py
```
This will initialize the environment and start the interactive session where you can input actions to interact with the boxes.



## Folder Structure
The `openthechests` module contains several folders and files of interest:
```plaintext
openthechests/
│
├── docs/
│   └── examples/
│
├── openthechests/
│   └── src/
│       ├── elements/
│       ├── utils/
│       ├── OpenTheChests.py
│       └── OpenTheChestsGym.py
│
├── tests/
├── demo.py
├── README.md
└── requirements.txt

```

## Descriptions of Key Files and Folders

- **docs/**: Contains documentation related to the project.
  - **examples/**: Example configurations and usage of the environment.
    - `__init__.py`: Initializes the examples module.

- **openthechests/**: The main code for the environment.
  - **src/**: Contains the main environment elements.
    - **elements/**: Contains classes that define the environment elements.
    - **utils/**: Contains useful functions used by other modules.
    - `OpenTheChests.py`: Defines the core environment logic.
    - `OpenTheChestsGym.py`: Provides the Gym interface for the environment.

- `demo.py`: Demonstration script for the environment.

- `requirements.txt`: Lists the dependencies required to run the project.





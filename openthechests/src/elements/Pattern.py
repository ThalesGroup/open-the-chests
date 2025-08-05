import random
from typing import List, Dict

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patheffects as path_effects

from openthechests.openthechests.src.utils.allen import allen_relations


def validate_pattern_instructions(instructions: List[Dict]) -> None:
    """
    Validates that a list of pattern instructions follows the correct structure and references.

    Checks include:
    - Proper use of 'delay' and 'noise' (only once, numeric parameters).
    - Each 'instantiate' has correct parameters and a unique variable_name.
    - Allen relation commands refer to defined variables.
    - Allen relation commands are among supported types.
    - Optional fields like 'gap_dist' are structurally valid.
    - Every event variable participates in at least one Allen relation.

    Parameters
    ----------
    instructions : List[Dict]
        The instruction list to validate.

    Raises
    ------
    ValueError
        If any instruction is malformed, has missing keys, refers to undefined variables,
        or an event does not participate in at least one Allen relation.
    """
    defined_vars = set()
    participated_vars = set()
    delay_seen = False
    noise_seen = False

    for i, instr in enumerate(instructions):
        cmd = instr.get("command")
        if cmd is None:
            raise ValueError(f"Instruction {i} is missing 'command' field.")

        # Check delay
        if cmd == "delay":
            if delay_seen:
                raise ValueError("Multiple 'delay' commands found.")
            if not isinstance(instr.get("parameters"), (int, float)):
                raise ValueError("'delay' must have a numeric parameter.")
            delay_seen = True

        # Check noise
        elif cmd == "noise":
            if noise_seen:
                raise ValueError("Multiple 'noise' commands found.")
            if not isinstance(instr.get("parameters"), (int, float)):
                raise ValueError("'noise' must have a numeric parameter.")
            noise_seen = True

        # Check instantiate
        elif cmd == "instantiate":
            if "variable_name" not in instr:
                raise ValueError(f"'instantiate' at index {i} is missing 'variable_name'.")
            if instr["variable_name"] in defined_vars:
                raise ValueError(f"Duplicate variable_name '{instr['variable_name']}' found.")
            params = instr.get("parameters")
            if not (isinstance(params, tuple) and len(params) == 3):
                raise ValueError(f"'instantiate' parameters must be (type, attrs, dist) tuple at index {i}.")
            _, attrs, dist = params
            if not isinstance(attrs, dict):
                raise ValueError(f"'instantiate' attrs must be dict at index {i}.")
            if not isinstance(dist, dict) or not all(k in dist for k in ("mu", "sigma")):
                raise ValueError(f"'instantiate' dist must be dict with 'mu' and 'sigma' at index {i}.")
            defined_vars.add(instr["variable_name"])

        # Allen-style temporal relation
        elif cmd in allen_relations:
            params = instr.get("parameters")
            if not (isinstance(params, list) and len(params) == 2):
                raise ValueError(f"'{cmd}' must specify two variables in 'parameters' list at index {i}.")
            src, tgt = params
            if src not in defined_vars or tgt not in defined_vars:
                raise ValueError(f"'{cmd}' refers to undefined variable(s): {src}, {tgt} at index {i}.")

            # Track participation
            participated_vars.add(src)
            participated_vars.add(tgt)

            # Enforce required 'other' fields for specific relations
            if cmd == "after":
                if "other" not in instr or "gap_dist" not in instr["other"]:
                    raise ValueError(f"'after' instruction at index {i} must include 'gap_dist' in 'other'.")
                gap = instr["other"]["gap_dist"]
                if not isinstance(gap, dict) or not all(k in gap for k in ("mu", "sigma")):
                    raise ValueError(f"'gap_dist' must be a dict with 'mu' and 'sigma' in 'after' at index {i}.")
            else:
                # For other relations, 'other' must not include unsupported fields
                if "other" in instr and instr["other"] not in (None, {}):
                    raise ValueError(f"Unexpected 'other' field in '{cmd}' at index {i}; only 'after' supports it.")

        else:
            raise ValueError(f"Unknown command '{cmd}' at index {i}.")

    # Final check: every defined variable must participate in at least one relation
    for var in defined_vars:
        if var not in participated_vars:
            raise ValueError(f"Event variable '{var}' does not participate in any Allen relation.")


class Pattern:
    """
    Represents a pattern associated with an interactive box.

    A pattern consists of an instruction list that defines how events for the box
    should be generated and evaluated. Each pattern may also define a delay (`timeout`)
    and a noise level to simulate variability in event timing or content.

    Attributes
    ----------
    id : int
        Unique identifier for the pattern.
    timeout : float
        Time window (in seconds) after which the pattern deactivates if unmet.
        Extracted from any instruction of type "delay".
    noise : float
        Noise level used to introduce uncertainty into event generation.
        Extracted from any instruction of type "noise".
    instruction : List[Dict]
        List of structured instructions (excluding "delay" and "noise")
        that define the event-matching pattern.
    full_pattern : List
        GUI-facing list used for visualizing or displaying the full pattern history.

    Methods
    -------
    sample_timeout() -> float
        Returns a random float sampled uniformly between 0 and `timeout`.
    reset() -> None
        Clears the full_pattern history (typically called during environment resets).
    get_timeout() -> float
        Returns the fixed `timeout` value.
    get_noise() -> float
        Returns the fixed `noise` value.
    """

    def __init__(self, instruction: List[Dict], id: int):
        """
        Initialize a Pattern object using an instruction list and an ID.

        Parameters
        ----------
        instruction : List[Dict]
            A list of structured pattern instructions. May contain special commands:
            - "delay": defines the timeout for the pattern
            - "noise": defines the noise level
            All other commands define event instructions.
        id : int
            The unique identifier for this pattern instance.
        """
        self.id = id

        # Extract 'delay' value if present; default to 0
        self.timeout = ([cmd["parameters"]
                         for cmd in instruction
                         if cmd["command"] == "delay"] or [0]).pop()

        # Extract 'noise' value if present; default to 0
        self.noise = ([cmd["parameters"]
                       for cmd in instruction
                       if cmd["command"] == "noise"] or [0]).pop()

        # Filter out special control commands to keep only event-related ones
        validate_pattern_instructions(instruction)
        self.instruction = [
            cmd for cmd in instruction
            if cmd["command"] not in ["delay", "noise"]
        ]

        # Used for GUI/display to store the full resolved pattern history
        self.full_pattern = []

    def sample_timeout(self) -> float:
        """
        Returns a random float uniformly sampled in [0, timeout].

        Returns
        -------
        float
            A randomly sampled timeout duration.
        """
        return random.uniform(0, self.timeout)

    def reset(self) -> None:
        """
        Reset the pattern state by clearing the `full_pattern` history.
        Typically used when restarting a box or environment.
        """
        self.full_pattern = []

    def get_timeout(self) -> float:
        """
        Return the timeout value.

        Returns
        -------
        float
            The pattern's timeout.
        """
        return self.timeout

    def get_noise(self) -> float:
        """
        Return the noise value.

        Returns
        -------
        float
            The pattern's noise level.
        """
        return self.noise

    def visualize(self) -> None:
        """
        Visualizes the current pattern as a directed graph of events and temporal relations.

        - Each instantiated event becomes a node.
        - Node color is based on the event's `bg` attribute.
        - Node label color is the `fg` attribute.
        - Event duration parameters (`mu`, `sigma`) are shown inside the node.
        - Temporal constraints (e.g., 'after', 'overlaps') are shown as directed edges.

        This visualization helps understand how the event sequence is structured
        and what Allen-style relations apply between them.

        Returns
        -------
        None
        """
        G = nx.DiGraph()
        pos = {}
        node_styles = {}

        # Step 1: Add event nodes
        for i, cmd in enumerate(self.instruction):
            if cmd["command"] == "instantiate":
                var_name = cmd["variable_name"]
                event_type, attrs, dist = cmd["parameters"]
                bg_color = attrs.get("bg", "#FFFFFF")
                fg_color = attrs.get("fg", "#000000")
                mu = dist.get("mu", "?")
                sigma = dist.get("sigma", "?")

                G.add_node(var_name)
                pos[var_name] = (i * 2, 0)  # spacing for layout
                node_styles[var_name] = (event_type, bg_color, fg_color, mu, sigma)

        # Step 2: Add temporal edges
        for cmd in self.instruction:
            if cmd["command"] in allen_relations:
                src, tgt = cmd["parameters"]
                G.add_edge(src, tgt, label=cmd["command"])

        # Step 3: Plot graph
        fig, ax = plt.subplots(figsize=(len(pos) * 2.2, 3))
        ax.set_aspect('equal')

        nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, edge_color='gray', width=2)

        for node in G.nodes():
            event_type, bg, fg, mu, sigma = node_styles[node]
            x, y = pos[node]

            # Draw circle for event
            circle = plt.Circle((x, y), 0.6, color=bg, ec='black', lw=1.5, zorder=2)
            ax.add_patch(circle)

            # Event type label with foreground outline
            txt = ax.text(x, y + 0.05, event_type, fontsize=14, ha='center', va='center',
                          color=fg, weight='bold')
            txt.set_path_effects([
                path_effects.Stroke(linewidth=3, foreground="black"),
                path_effects.Normal()
            ])

            # Mu and sigma annotation
            ax.text(x, y - 0.2, f"μ={mu}, σ={sigma}", fontsize=9, ha='center', va='center',
                    style='italic', color='black')

        # Draw edge labels
        edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                     font_color='black', font_size=8)

        ax.set_xlim(-1, max(p[0] for p in pos.values()) + 1.5)
        ax.set_ylim(-1, 1)
        plt.axis('off')
        plt.title("Pattern Visualization (Events & Temporal Relations)", fontsize=12)
        plt.show()

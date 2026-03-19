import csv
import random
from collections import defaultdict
from typing import List, Dict

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patheffects as path_effects

from openthechests.src.utils.allen import allen_relations

from typing import List, Dict


def validate_pattern_instructions(instructions: List[Dict]) -> None:
    """
    Validates that a list of pattern instructions follows the correct structure and references.

    Checks include:
    - Proper use of 'delay' and 'noise' (only once, numeric parameters).
    - Each 'instantiate' has correct parameters and a unique variable_name.
    - Allen relation commands refer to defined variables and are supported.
    - Allen relation 'parameters' are ordered as [second_event, first_event].
    - 'after' and 'before' must provide other.gap_dist with 'mu' and 'sigma'.
    - For containment relations ('during', 'starts', 'ends'):
        (second.mu + second.sigma) < (first.mu - first.sigma)
    - Every event variable participates in at least one Allen relation (if >1 events).

    Parameters
    ----------
    instructions : List[Dict]
        The instruction list to validate.

    Raises
    ------
    ValueError
        If any instruction is malformed, has missing keys, refers to undefined variables,
        violates ordering/bonus-parameter rules, or violates containment length constraints.
    """
    # Supported Allen relations (extend as you add more)
    allowed_rels = {
        "after", "before", "during", "met_by", "overlapped", "starts", "ends", "equals"
    }
    # Relations that require extra fields in 'other'
    rel_requires_other = {
        "after": {"gap_dist"},
        "before": {"gap_dist"},
    }
    # Relations implying containment (second inside first)
    containment_rels = {"during", "starts", "ends"}

    defined_vars = set()
    participated_vars = set()
    delay_seen = False
    noise_seen = False
    activity_seen = False

    # Collect distributions from 'instantiate' to validate containment later
    dists_by_var: Dict[str, Dict[str, float]] = {}

    for i, instr in enumerate(instructions):
        cmd = instr.get("command")
        if cmd is None:
            raise ValueError(f"Instruction {i} is missing 'command' field.")

        # --- delay ---
        if cmd == "delay":
            if delay_seen:
                raise ValueError("Multiple 'delay' commands found.")
            if not isinstance(instr.get("parameters"), (int, float)):
                raise ValueError("'delay' must have a numeric parameter.")
            delay_seen = True

        # --- noise ---
        elif cmd == "noise":
            if noise_seen:
                raise ValueError("Multiple 'noise' commands found.")
            if not isinstance(instr.get("parameters"), (int, float)):
                raise ValueError("'noise' must have a numeric parameter.")
            noise_seen = True

        # --- activity ---
        elif cmd == "activity":
            if activity_seen:
                raise ValueError("Multiple 'activity' commands found.")
            if not isinstance(instr.get("parameters"), str):
                raise ValueError("'activity' must have a string parameter.")
            activity_seen = True

        # --- instantiate ---
        elif cmd == "instantiate":
            if "variable_name" not in instr:
                raise ValueError(f"'instantiate' at index {i} is missing 'variable_name'.")
            var = instr["variable_name"]
            if var in defined_vars:
                raise ValueError(f"Duplicate variable_name '{var}' found.")
            params = instr.get("parameters")
            if not (isinstance(params, tuple) and len(params) == 3):
                raise ValueError(f"'instantiate' parameters must be (type, attrs, dist) tuple at index {i}.")
            _, attrs, dist = params
            if not isinstance(attrs, dict):
                raise ValueError(f"'instantiate' attrs must be dict at index {i}.")
            if not (isinstance(dist, dict) and all(k in dist for k in ("mu", "sigma"))):
                raise ValueError(f"'instantiate' dist must be dict with 'mu' and 'sigma' at index {i}.")

            # Record definition and its distribution
            defined_vars.add(var)
            dists_by_var[var] = dist

        # --- Allen relations ---
        elif cmd in allowed_rels:
            params = instr.get("parameters")
            if not (isinstance(params, list) and len(params) == 2):
                raise ValueError(f"'{cmd}' must specify two variables in 'parameters' list at index {i}.")

            # Enforce parameter order: [second_event, first_event]
            second_var, first_var = params[0], params[1]

            if second_var not in defined_vars or first_var not in defined_vars:
                raise ValueError(f"'{cmd}' refers to undefined variable(s): {second_var}, {first_var} at index {i}.")

            # If variable_name is present, enforce it tags the 'first' side for consistency
            if "variable_name" in instr and instr["variable_name"] != second_var:
                raise ValueError(
                    f"'{cmd}' at index {i}: 'variable_name' should reference the FIRST event "
                    f"(the second element in parameters). Expected '{first_var}', got '{instr['variable_name']}'."
                )

            participated_vars.update({second_var, first_var})

            # Validate required 'other' for specific relations (e.g., after/before)
            if cmd in rel_requires_other:
                other = instr.get("other")
                if not isinstance(other, dict):
                    raise ValueError(f"'{cmd}' at index {i} must include 'other' dict.")
                missing = [k for k in rel_requires_other[cmd] if k not in other]
                if missing:
                    raise ValueError(f"'{cmd}' at index {i} missing required keys in 'other': {missing}")
                # Validate gap_dist structure
                if "gap_dist" in other:
                    gd = other["gap_dist"]
                    if not (isinstance(gd, dict) and all(k in gd for k in ("mu", "sigma"))):
                        raise ValueError(
                            f"'gap_dist' in '{cmd}' at index {i} must be a dict with 'mu' and 'sigma'."
                        )
            else:
                # No unsupported 'other' payloads for relations that don't use it
                if "other" in instr and instr["other"] not in (None, {}):
                    raise ValueError(
                        f"Unexpected 'other' field in '{cmd}' at index {i}; only "
                        f"{sorted(rel_requires_other.keys())} support it."
                    )

            # Containment relation duration constraint
            if cmd in containment_rels:
                sec = dists_by_var.get(second_var)
                fst = dists_by_var.get(first_var)
                if sec is None or fst is None:
                    raise ValueError(
                        f"Missing duration distribution for '{second_var}' or '{first_var}' to validate '{cmd}' at index {i}."
                    )
                sec_sum = float(sec["mu"]) + float(sec["sigma"])
                fst_margin = float(fst["mu"]) - float(fst["sigma"])
                if not (sec_sum <= fst_margin):
                    raise ValueError(
                        f"Containment violation for '{cmd}' at index {i}: "
                        f"{second_var}.mu+sigma={sec_sum:.3f} is not < {first_var}.mu-sigma={fst_margin:.3f}."
                    )

        else:
            raise ValueError(f"Unknown command '{cmd}' at index {i}.")

    # Final participation check
    if len(defined_vars) > 1:
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
            A list of structured pattern instructions. Both modes share this
            list-of-dicts format. The mode is determined by the presence of a
            special ``"dataset"`` command:

            **Config mode** (no ``"dataset"`` command):
            - ``"delay"``: defines the timeout for the pattern
            - ``"noise"``: defines the noise level
            - ``"instantiate"``, Allen-relation commands: define event generation

            **Dataset mode** (contains ``{"command": "dataset", "parameters": "<path>"}``):
            - ``"dataset"``: path to CSV file with pre-recorded traces
            - ``"activity"``: optional human-readable activity name (default ``None``)
            - ``"delay"``: optional timeout (default 0)
            - ``"noise"``: optional noise ratio (default 0)
            No event-instantiation commands are needed in this mode.

            Both modes accept an optional ``"activity"`` command for readability.
        id : int
            The unique identifier for this pattern instance.
        """
        self.id = id

        # Used for GUI/display to store the full resolved pattern history
        self.full_pattern = []

        # --- Activity name (both modes) ---
        self.activity_name = next(
            (cmd["parameters"] for cmd in instruction if cmd["command"] == "activity"),
            None,
        )

        if any(cmd["command"] == "dataset" for cmd in instruction):
            # --- Dataset mode ---
            self.instruction_type = "dataset"

            data_file = next(cmd["parameters"]
                             for cmd in instruction
                             if cmd["command"] == "dataset")

            # Extract delay/noise as usual; default to 0
            self.timeout = ([cmd["parameters"]
                             for cmd in instruction
                             if cmd["command"] == "delay"] or [0]).pop()
            self.noise = ([cmd["parameters"]
                           for cmd in instruction
                           if cmd["command"] == "noise"] or [0]).pop()

            self.instruction = []
            self.traces = self._load_traces(data_file)

        else:
            # --- Config mode ---
            self.instruction_type = "config"

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
                if cmd["command"] not in ["delay", "noise", "activity"]
            ]

    @staticmethod
    def _load_traces(data_file: str):
        """
        Load all event traces from a per-activity CSV file for dataset mode.

        The CSV is expected to have the same format produced by the data generation
        pipeline: one row per sensor event, grouped into traces via the
        ``unique_activity_key`` column.  Times are stored as ``HH:MM:SS.ffffff``
        strings and are converted to seconds, then normalized so every trace starts
        at time 0.

        Expected columns: ``unique_activity_key``, ``device_id``,
        ``start_time``, ``end_time``.

        Parameters
        ----------
        data_file : str
            Path to the per-activity CSV file.

        Returns
        -------
        list[list[Event]]
            A list of traces, where each trace is a list of :class:`Event` objects
            sorted by end time.
        """
        import pandas as pd
        from openthechests.src.elements.Event import Event

        def _time_to_seconds(t_str):
            h, m, s = map(float, str(t_str).split(":"))
            return h * 3600 + m * 60 + s

        df = pd.read_csv(data_file)

        traces = []
        for _, group in df.groupby("unique_activity_key"):
            group = group.sort_values("end_time")

            start_secs = group["start_time"].apply(_time_to_seconds)
            end_secs = group["end_time"].apply(_time_to_seconds)

            trace_start = start_secs.min()

            events = [
                Event(
                    e_type=row["device_id"],
                    e_attributes={},
                    t_start=t_start - trace_start,
                    t_end=t_end - trace_start,
                )
                for (_, row), t_start, t_end in zip(
                    group.iterrows(), start_secs, end_secs
                )
            ]
            traces.append(sorted(events))

        return traces

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

        Not available for dataset-mode patterns (no instruction graph to display).

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
        if self.instruction_type == "dataset":
            name = f" ({self.activity_name})" if self.activity_name else ""
            print(f"Pattern {self.id}{name} is a dataset pattern — no instruction graph to visualize.")
            return

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
        title = "Pattern Visualization (Events & Temporal Relations)"
        if self.activity_name:
            title = f"{self.activity_name} — {title}"
        plt.title(title, fontsize=12)
        plt.show()

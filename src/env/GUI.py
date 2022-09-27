import math
import PySimpleGUI as sg
import pandas as pd
import plotly.express as px

# TODO (priority 4) rework whole class to be more logically organised and with less parameters
from matplotlib import colors


class BoxEventGUI:

    def __init__(self, num_patterns, attr_to_color):
        """
        Define GUI that allows to display an environment.

        :param num_patterns: Number of patterns to be displayed.
        :param attr_to_color: Dictionary that allows to convert an attribute to a color for display.
        """
        self.attr_to_color = attr_to_color
        # list of variables used for communication between environment and GUI
        self.variables = dict()
        # history of past observed events to be displayed
        self.history = []

        # left part of display showing history, observations and actions
        timeline_viewer_column = [
            [sg.Image(key="-history-")],
            [sg.Text(size=(100, 1), key="-action-")],
            [sg.Text(size=(100, 1), key="-context-")],
            [sg.Push(), sg.Button("Next")]
        ]

        # right part of display showing advancement of each pattern
        patterns_column = []
        for i in range(num_patterns):
            patterns_column.append([sg.Image(key="-pattern-" + str(i))])
            patterns_column.append([sg.Text(size=(100, 1), key="-box-" + str(i))])

        self.layout = [
            [
                sg.Column(timeline_viewer_column,
                          scrollable=True,
                          vertical_scroll_only=False,
                          size=(800, 600),
                          key='Column0'),

                sg.VSeperator(),

                sg.Column(patterns_column,
                          scrollable=True,
                          vertical_scroll_only=False,
                          size=(800, 600),
                          key='Column1')
            ]
        ]
        self.window = sg.Window("Symbolic Event Environment", self.layout)

    def add_event_to_history(self, event):
        """
        Add an event to the history variable that saves all past events.
        They are all displayed under the form of a timeline history in the right "history" window of the GUI.

        :param event: The event ot add to the history
        """
        self.history.append(event)

    def update_variable(self, name, value):
        """
        Add a variable to the dictionary used for displaying information.
        This is used to avoid passing multiple unclear parameters during step process.
        If needed the variables can be updated and then the step process needs only the variable dictionary.

        :param name: The name of the parameter to update
        :param value: The value to update the parameter to
        """
        self.variables[name] = value

    def get_variable(self, name):
        """
        Get the value of a saved parameter.

        :param name: The name of the parameter to get.
        :return: The value of the parameter
        """
        return self.variables[name] if (name in self.variables) else None

    def step(self):
        """
        Visualise new environment using updated variable values.
        """
        # TODO (priority 4) fix this to add option with smooth transitions with no button
        event, values = self.window.read()

        self.print_history_to_window()

        boxes = self.get_variable("boxes")
        patterns = []
        patterns_closed = []
        box_states = []
        for box in boxes:
            patterns.append(box.pattern.full_pattern)
            if not box.is_open():
                patterns_closed.append(box.pattern.full_pattern)
            box_states.append(box.get_state())

        # get min max ranges of all patterns so that all windows are the same
        patterns_range = [
            # fallback ot 0 if list is empty
            min([p[0].start for p in patterns_closed] or [0]),
            max([p[-1].end for p in patterns_closed] or [0])
        ]

        # print each pattern in a window and update its state
        for i in range(len(patterns)):
            if boxes[i].is_open():
                bg_color = "green"
            elif not boxes[i].is_active():
                bg_color = "red"
            else:
                bg_color = "white"

            pattern_img = self.print_event_list(patterns[i],
                                                current_time=self.get_variable("time"),
                                                patterns_range=patterns_range,
                                                bg_color=bg_color)
            self.window["-pattern-" + str(i)].update(data=pattern_img)
            self.window["-box-" + str(i)].update(f"box state : {box_states[i]}")

        self.update_window()

    def update_window(self):
        """
         Update windows to get new values shown.
        """

        # refresh the update to take into account image changes
        self.window.refresh()
        # update for scroll area of Column element
        self.window['Column0'].contents_changed()
        self.window['Column1'].contents_changed()
        self.window['Column0'].Widget.canvas.xview_moveto(1.0)

    def print_history_to_window(self):
        """
        Print saved event history to image and update window view with the printed image
        as well as current context and action information.
        """
        past_events_img = self.print_event_list(self.history)
        self.window["-history-"].update(data=past_events_img)
        self.window["-context-"].update(self.get_variable("context"))
        self.window["-action-"].update("action : " + str(self.get_variable("last_action")))

    # TODO (priority 2) make this part of the code prettier
    def print_event_list(self,
                         event_list,
                         show=False,
                         current_time=None,
                         patterns_range=None,
                         bg_color=None):
        """
        Allows to print a list of events under the form of a timeline.
        The list of events is transformed into a pandas dataframe which is then used to generate a barchart timeline.
        The colors of the bar charts are synchronised with event backgrounds.
        Annotations are added to indicate the type of each event, where there colors are also synchronised
        with the foreground color attribute.
        Gives the possibility to add a line showing the current time.

        :param event_list: The list of events to print.
        :param show: Show timeline as a window or print it to an image.
        :param current_time: Current time used to make a line on timeline.
        :param patterns_range: Beginning and end of timeline range.
        :param bg_color: Background color of the timeline.
        :return:
        """
        list_df = []
        annots = []
        line_end_times = []
        for event in event_list:
            line_index = self.first_free_line_index(event, line_end_times)

            list_df.append(dict(BG=str(event.symbol["attr"]["bg"]),
                                Start=event.start,
                                Finish=event.end,
                                Task=str(line_index),
                                Label="Event type " + str(event.symbol["e_type"])
                                ))

            fg_color = self.attr_to_color["fg"][event.get_attribute_val("fg")]
            annots.append(dict(
                x=event.start + (event.end - event.start) / 2,
                y=line_index,
                text=str(event.symbol["e_type"]),
                showarrow=False,
                bordercolor="#c7c7c7",
                borderwidth=2,
                borderpad=4,
                bgcolor=fg_color,
                align="center",
                opacity=0.8,
                font=dict(
                    family="Courier New, monospace",
                    size=1 + 25 * (1 - math.exp(-event.end + event.start)),  # scale size wih event length
                    color="#ffffff"
                ),
            ))

        df = pd.DataFrame(list_df)

        if not patterns_range:
            patterns_range = [event_list[0].start, event_list[-1].end]
        color_map = dict((str(i), colors.cnames[col]) for i, col in enumerate(self.attr_to_color["bg"]))
        fig = px.timeline(df,
                          height=90 * len(line_end_times) + 100,
                          width=(patterns_range[1] - patterns_range[0]) * 45 + 100,
                          x_start="Start",
                          x_end="Finish",
                          y="Task",
                          color="BG",
                          color_discrete_map=color_map,
                          category_orders={"Task": [str(i) for i in range(len(line_end_times) - 1, -1, -1)]})

        # otherwise blocks are not printed
        df['delta'] = df['Finish'] - df['Start']
        for d in fig.data:
            filt = df['BG'] == d.name
            d.x = df[filt]['delta'].tolist()

        # to have xaxis with continuous values
        fig.layout.xaxis.type = 'linear'
        fig['layout']['annotations'] = annots

        # change background color
        if bg_color:
            fig.update_layout({
                "paper_bgcolor": bg_color,
            })

        # add line showing current time in environment
        if current_time:
            line = dict(
                type='line',
                yref='paper', y0=0, y1=1,
                xref='x', x0=current_time, x1=current_time
            )
            fig.update_layout(shapes=[line])
            fig.update_xaxes(type="date", range=patterns_range)
            fig.layout.xaxis.type = 'linear'

        if show:
            fig.show()
        else:
            return fig.to_image()

    def first_free_line_index(self, event, line_end_times):
        """
        Place a selected event on a column of other events so that no events overlap.
        The event is placed in the first empty spot.
        If there is no available spot the returned index is larger that the columns size.

        :param event: the event to place
        :param line_end_times: a list indicating the ends of all events placed on the column
        :return: the index showing the first free space
        """
        line_index = 0
        while line_index < len(line_end_times) and line_end_times[line_index] >= event.start:
            line_index += 1
        if line_index < len(line_end_times):
            line_end_times[line_index] = event.end
        else:
            line_end_times.append(event.end)
        return line_index

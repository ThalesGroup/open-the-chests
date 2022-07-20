import math

import PySimpleGUI as sg
import pandas as pd
from joblib.testing import timeout
from plotly import figure_factory as ff
import plotly.express as px


# TODO change background color depending on box state
# TODO rework whole class to be more logically organised and with less parameters

class BoxEventGUI:

    def __init__(self, num_patterns, attr_to_color):

        self.attr_to_color = attr_to_color
        self.pattern_list = None

        timeline_viewer_column = [
            [sg.Image(key="-IMAGE-")],
            [sg.Text(size=(100, 1), key="-action-")],
            [sg.Text(size=(100, 1), key="-TOUT-")],
            [sg.Push(), sg.Button("Next")]
        ]

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

    def step(self,
             past_events,
             context,
             current_time,
             patterns,
             box_states,
             action=None):
        event, values = self.window.read()
        past_events_img = self.print_event_list(past_events)
        self.window["-IMAGE-"].update(data=past_events_img)
        self.window["-TOUT-"].update(context)
        self.window["-action-"].update(f"action : {action}")
        # Refresh the update
        self.window.refresh()
        # Update for scroll area of Column element
        self.window['Column0'].contents_changed()
        self.window['Column1'].contents_changed()
        self.window['Column0'].Widget.canvas.xview_moveto(1.0)

        patterns_range = [patterns[0][0].start, patterns[0][-1].end]
        for pattern in patterns[1:]:
            if pattern[0].start < patterns_range[0]:
                patterns_range[0] = pattern[0].start
            if pattern[0].end > patterns_range[1]:
                patterns_range[1] = pattern[0].end

        for i in range(len(patterns)):
            pattern_img = self.print_event_list(patterns[i],
                                                current_time=current_time,
                                                patterns_range=patterns_range)
            self.window["-pattern-" + str(i)].update(data=pattern_img)
            self.window["-box-" + str(i)].update(f"box state : {box_states[i]}")

    def print_event_list(self, event_list, show=False, current_time=None, patterns_range=None):
        list_df = []
        annots = []
        line_end_times = [-1]
        for event in event_list:
            line_index = 0
            while line_index + 1 <= len(line_end_times) and line_end_times[line_index] >= event.start:
                line_index += 1
            if line_index + 1 <= len(line_end_times):
                line_end_times[line_index] = event.end
            else:
                line_end_times.append(event.end)

            list_df.append(dict(BG=str(event.symbol["attr"]["bg"]),
                                FG=str(event.symbol["attr"]["fg"]),
                                Start=event.start,
                                Finish=event.end,
                                Task=str(line_index),
                                Label="Event type " + str(event.symbol["e_type"])
                                ))

            fg_color = self.attr_to_color["fg"][str(event.symbol["attr"]["fg"])]
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
                    size=25 * (1 - math.exp(-event.end + event.start)),
                    color="#ffffff"
                ),
            ))

        df = pd.DataFrame(list_df)
        df['delta'] = df['Finish'] - df['Start']

        if not patterns_range:
            patterns_range = [event_list[0].start, event_list[-1].end]

        fig = px.timeline(df,
                          height=90 * len(line_end_times) + 100,
                          width=(patterns_range[1] - patterns_range[0]) * 45 + 100,
                          x_start="Start",
                          x_end="Finish",
                          y="Task",
                          color="BG",
                          # TODO
                          color_discrete_map={'0': 'red', '1': 'blue', '2': 'green'})

        for d in fig.data:
            filt = df['BG'] == d.name
            d.x = df[filt]['delta'].tolist()

        fig.update_yaxes(autorange="reversed")  # otherwise, tasks are listed from the bottom up
        fig.layout.xaxis.type = 'linear'
        fig['layout']['annotations'] = annots

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

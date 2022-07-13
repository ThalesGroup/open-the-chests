import PySimpleGUI as sg
from joblib.testing import timeout

from utils.utils import print_event_list


class BoxEventGUI:

    def __init__(self, num_patterns):

        self.pattern_list = None

        timeline_viewer_column = [
            [sg.Image(key="-IMAGE-")],
            [sg.Text(size=(100, 1), key="-action-")],
            [sg.Text(size=(100, 1), key="-TOUT-")],
            [sg.Button("Next")]
        ]

        patterns_column = []
        for i in range(num_patterns):
            patterns_column.append([sg.Image(key="-pattern-" + str(i))])
            patterns_column.append([sg.Text(size=(100, 1), key="-box-" + str(i))])

        self.layout = [
            [
                sg.Column(timeline_viewer_column),

                sg.VSeperator(),

                sg.Column(patterns_column)
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
        past_events_img = print_event_list(past_events, title="Past Timeline of Events")
        self.window["-IMAGE-"].update(data=past_events_img)
        self.window["-TOUT-"].update(context)
        self.window["-action-"].update(f"action : {action}")

        line = dict(
            type='line',
            yref='paper', y0=0, y1=1,
            xref='x', x0=current_time, x1=current_time
        )

        for i in range(len(patterns)):
            pattern_img = print_event_list(patterns[i],
                                           title=f"Pattern {i}",
                                           line=line)
            self.window["-pattern-" + str(i)].update(data=pattern_img)
            self.window["-box-" + str(i)].update(f"box state : {box_states[i]}")

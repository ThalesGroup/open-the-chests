import PySimpleGUI as sg
from joblib.testing import timeout


class BoxEventGUI:

    def __init__(self):
        timeline_viewer_column = [
            [sg.Text("Bellow we observe the active timeline:")],
            [sg.Image(key="-IMAGE-")],
        ]
        self.layout = [
            [
                sg.Image(key="-IMAGE-"),
                [sg.Text(size=(100, 1), key="-TOUT-")],
                sg.Button("Next")
            ]
        ]
        self.window = sg.Window("Symbolic Event Environment", self.layout)

    def step(self, img_binary, context):
        event, values = self.window.read()
        self.window["-IMAGE-"].update(data=img_binary)
        self.window["-TOUT-"].update(context)

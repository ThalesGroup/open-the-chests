from src.env.elements.Event import Event

e = Event("A", {"attr1": "blue", "attr2": "green"}, 5, 10)
shifted_e = e.shift(10)
shifted_e = e.shift(-5)

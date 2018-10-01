


class TestPredictor:
    def __init__(self, path_list):
        self.path_list = path_list

    def predict(self, callback):
        for img in self.path_list:
            callback(target=img[-4:])
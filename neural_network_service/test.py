from utils.client_api import NeuralNetworkTask
import time

a = NeuralNetworkTask()
b = NeuralNetworkTask()

a.start(name='test', pathes=[], extra={})
b.start(name='test', pathes=[], extra={})


for i in range(15):
    time.sleep(1)
    if i == 12:
        print('here')
        a.stop()


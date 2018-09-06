from utils.client_api import NeuralNetworkTask
import time

a = NeuralNetworkTask()
b = NeuralNetworkTask()
c = NeuralNetworkTask()
d = NeuralNetworkTask()
e = NeuralNetworkTask()
f = NeuralNetworkTask()

a.start(name='test1', path_list=[x for x in range(300)], extra={})
b.start(name='test2', path_list=[x for x in range(300)], extra={})
c.start(name='test3', path_list=[x for x in range(300)], extra={})
d.start(name='test4', path_list=[x for x in range(300)], extra={})
e.start(name='test3', path_list=[x for x in range(300)], extra={})
f.start(name='test4', path_list=[x for x in range(300)], extra={})

for i in range(260):
    time.sleep(1)
    if i == 100:
        a.stop()
    elif i == 115:
        b.stop()
    elif i == 120:
        c.stop()
    elif i == 250:
        a.continue_stopped()




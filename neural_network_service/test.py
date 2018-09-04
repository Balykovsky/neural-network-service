from utils.client_api import NeuralNetworkTask
import time

a = NeuralNetworkTask()
b = NeuralNetworkTask()
c = NeuralNetworkTask()
d = NeuralNetworkTask()
e = NeuralNetworkTask()
f = NeuralNetworkTask()

a.start(name='test1', path_list=[x for x in range(50)], extra={})
b.start(name='test2', path_list=[x for x in range(50)], extra={})
c.start(name='test3', path_list=[x for x in range(50)], extra={})
d.start(name='test4', path_list=[x for x in range(50)], extra={})
e.start(name='test3', path_list=[x for x in range(50)], extra={})
f.start(name='test4', path_list=[x for x in range(50)], extra={})

for i in range(5):
    time.sleep(1)
    if i == 4:
        a.stop()




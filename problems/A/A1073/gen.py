from random import *
from cyaron import *

CASES = 20

for _t in range(1, CASES + 1):
    io = IO(f"{_t}.in")
    # ==============================
    if(_t == 1):
        io.input_writeln("1\n3 9\n3 2 7")
    elif _t == 2:
        io.input_writeln("1\n4 100\n9 99 0 999")
    elif _t == 3:
        io.input_writeln("1\n5 100\n1 1 1 1 1")
    elif _t <= 6:
        t = randint(3,10)
        io.input_writeln(t)
        io.input_writeln("10 100")
        list1 = [1 for i in range(1, 11)]
        io.input_writeln(list1)
        io.input_writeln("5 100\n1 1 1 0 9999")
        for test in range(t - 2):
            n = randint(1, 10)
            k = randint(n, 100)
            list1 = [randint(k, 1000) for i in range(1, n + 1)]
            io.input_writeln(n, k)
            io.input_writeln(list1)
    elif _t <= 16:
        t = randint(40,50)
        io.input_writeln(t)
        io.input_writeln("100 10000")
        list1 = [1 for i in range(1, 101)]
        io.input_writeln(list1)
        io.input_writeln("5 10000\n1 1 1 0 9999")
        for test in range(t - 2):
            n = randint(1, 100)
            k = randint(n, 10000)
            list1 = [randint(k, 10000) for i in range(1, n + 1)]
            io.input_writeln(n, k)
            io.input_writeln(list1)
    elif _t <= 19:
        t = randint(3,100)
        io.input_writeln(t)
        io.input_writeln("200000 1000000000")
        list1 = [1 for i in range(1, 200001)]
        io.input_writeln(list1)
        io.input_writeln("5 1000000000\n1 1 1 0 9999")
        for test in range(t - 2):
            n = randint(1, min(int(2e5), (int)(1e6 / t)))
            k = randint(1, 1000000000)
            list1 = [randint(k, 1000000000) for i in range(1, n + 1)]
            io.input_writeln(n, k)
            io.input_writeln(list1)
    else:
        io.input_writeln("100")
        for test in range(100):
            io.input_writeln("1 1000000000\n1000000000")
    # ==============================
    io.close()

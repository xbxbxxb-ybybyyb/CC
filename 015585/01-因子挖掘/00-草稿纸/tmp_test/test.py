class test_class:
    def __init__(self, x):
        self.x=x

list1 = ['a','b']
res = []
for i in list1:
    def test_func(x):
        m = i
        print(x,m)
        return
    a = test_class(5)
    a.func = test_func
    res.append(a)
    res[0].func(5)


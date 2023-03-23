import operator
def test(operator, x, y):
    return operator(x, y)

def test2():
    print(test(operator.lt, 3, 4))
test2()

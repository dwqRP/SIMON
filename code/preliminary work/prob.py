import math


a = 8 / 23 * (2 ** 63)
b = 8 / 23 * (2 ** 63.81)
c = 2 ** 62.81

print(math.log2(a + b + c))
import math



n = 16
mx = 1 << n
find = []

def cyclshift(t, a):
    return ((t << a) & (mx - 1)) | (t >> (n - a))

def F(t):
    return (cyclshift(t, 8) & cyclshift(t, 1)) ^ cyclshift(t, 2)

for i in range(mx):
    find.append([])

for i in range(mx):
    tmp = F(i)
    # print(bin(i)[2:].zfill(n), bin(tmp)[2:].zfill(n))
    find[tmp].append(i)
    
# cnt = 0
# for i in range(mx):
#     if len(find[i]) == 0:
#         cnt += 1

# print("Count =", cnt)

num = 0
maxx = 0
fixpos = 15
k = (1 << fixpos)
for i in range(mx):
    if i & k == 0:
        num += len(find[i])
        maxx = max(maxx, len(find[i]))
        
print(num, maxx)


beta = 0b0100000000010001
print(bin(F(beta))[2:].zfill(n))

print(bin(cyclshift(beta, 1) | cyclshift(beta, 8))[2:].zfill(n))
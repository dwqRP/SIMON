
def listOnes(x):
    bx = bin(x)[2:]
    ans = ""
    print(bx)
    le = len(bx)
    for i in range(le - 1, -1, -1):
        if bx[i] == '1':
            if ans == "":
                ans += "(1 << " + str(le - i - 1) + ")"
            else:
                ans += " ^ (1 << " + str(le - i - 1) + ")"
    print(ans)

l, r = 0x000040, 0x000011

listOnes(l)
listOnes(r)
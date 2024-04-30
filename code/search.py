import time

n = 24
R = 17
minw = 96
mx = 1 << (n << 1)
win = 0
lin = 0
rin = 0

# B = [0, 0, 2, 4, 6, 8, 12, 14, 18, 20, 25, 30, 34, 36, 38]
# C = [0, 32, 496, 4960, 35960, 201376]

B = [0, 0, 2, 4, 6, 8, 12, 14, 18, 20, 26, 30, 35, 38, 44, 46, 50, 52]
C = [0, 48, 1128, 17296, 194580, 1712304, 12271512, 73629072]


def ctz(x):
    count = 0
    while x & 1 == 0 and x != 0:
        count += 1
        x >>= 1
    return count


def wt(x):
    return bin(x).count("1")


def b(x, pos):
    if x & (1 << pos) == 0:
        return 0
    return 1


def next_perm(x):
    v = x | (x - 1)
    return (v + 1) | (((~v & -~v) - 1) >> (ctz(x) + 1))


def next(x):
    global mx
    if ((x - 1) | x) >= mx - 1:
        return (1 << (wt(x) + 1)) - 1
    return next_perm(x)


def lshift(x, pos):
    global n
    return (x >> (n - pos)) | (x << pos) % (1 << n)


def dfs(l, r, round, p):
    print(l, r, round, p)
    if round > R:
        wout = wt(l) + wt(r)
        global win, lin, rin, minw
        if win + wout <= minw:
            minw = win + wout
            print("------------------------")
            print("Delta in: ( %x , %x )" % (lin, rin))
            print("Delta out: ( %x , %x )" % (l, r))
            print("p = 2^{-%d} wt = %d" % (p, win + wout))
            print("------------------------")
        return
    alpha = l
    # print('alpha=%x' %(alpha))
    cnt = 0
    vec = []
    for i in range(n):
        vec.append(-1)
    for i in range(n):
        br1 = b(alpha, (i - 1 + n) % n)
        br8 = b(alpha, (i - 8 + n) % n)
        bl6 = b(alpha, (i + 6) % n)
        if br1 | br8 == 1:
            if vec[i] == -1:
                vec[i] = i
            cnt += 1
            if br1 == 0 and bl6 == 1 and br8 == 1:
                vec[(i + 7) % n] = vec[i]
                cnt -= 1
    if p + cnt + B[R - round] > B[R]:
        return
    w = 1 << cnt
    beta = (lshift(alpha, 1) & lshift(alpha, 8)) ^ lshift(alpha, 2)
    for i in range(w):
        res = beta
        tmp = 0
        for j in range(n):
            if vec[j] == j:
                res ^= b(i, tmp) << j
                tmp += 1
        for j in range(n):
            if vec[j] != -1 and vec[j] != j:
                if b(res, j) ^ b(res, vec[j]):
                    res ^= 1 << j
        dfs(r ^ res, l, round + 1, p + cnt)
    return


if __name__ == "__main__":
    start_time = time.time()
    tmpw = 0
    total = 0
    pr = 0
    js = 0
    i = 1
    while i < mx:
        js += 1
        l = i >> n
        r = i % (1 << n)
        # print(bin(l), bin(r))
        if b(l, 0) | b(r, 0) == 0:
            i = next(i)
            continue
        win = wt(i)
        if win > tmpw:
            print("Start search delta in with hamming weight %d" % (win))
            tmpw = win
            total = C[win]
            js = 1
            pr = 0
        if win >= minw:
            print("Stop at ( %x , %x )" % (l, r))
            break
        rate = 100 * js // total
        if rate and rate % 5 == 0 and rate > pr:
            pr = rate
            print(
                "Processed: {}%    Time: {}s".format(
                    rate, round(time.time() - start_time, 2)
                )
            )
        lin = l
        rin = r
        dfs(l, r, 1, 0)
        i = next(i)

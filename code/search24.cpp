#include <bits/stdc++.h>
#define simon24 unsigned int
#define simon48 unsigned long long
using namespace std;
int n = 24, R = 17;
int minw = 96, win, wout;
simon24 lin, rin;
simon48 mx;
int B[30] = {0, 0, 2, 4, 6, 8, 12, 14, 18, 20, 26, 30, 35, 38, 44, 46, 50, 52};
int C[10] = {0, 48, 1128, 17296, 194580, 1712304, 12271512, 73629072};

int ctz(simon48 x)
{
    simon24 xx = x;
    int ans = __builtin_ctz(xx);
    return ans == 32 ? 32 + __builtin_ctz(x >> 32) : ans;
}

int wt(simon48 x)
{
    simon24 xx = x;
    return __builtin_popcount(xx) + __builtin_popcount(x >> 32);
}

simon48 next_perm(simon48 v)
{
    simon48 t = v | (v - 1);
    return (t + 1) | (((~t & -~t) - 1) >> (ctz(v) + 1));
}

simon48 next(simon48 cur)
{
    return ((cur - 1) | cur) >= mx ? (1ULL << (wt(cur) + 1)) - 1 : next_perm(cur);
}

inline bool bit(simon24 x, int pos) { return (x & (1 << pos)) == 0 ? 0 : 1; }

inline simon24 lshift(simon24 x, int pos) { return (x << pos) | (x >> (n - pos)); }

void dfs(simon24 l, simon24 r, int round, int p)
{
    // printf("l=%x r=%x round=%d p=2^{-%d}\n", l, r, round, p);
    if (round > R)
    {
        wout = wt(l) + wt(r);
        if (win + wout <= minw)
        {
            minw = win + wout;
            puts("------------------------");
            printf("Delta in: ( %x , %x )\n", lin, rin);
            printf("Delta out: ( %x , %x )\n", l, r);
            printf("p=2^{-%d} wt=%d\n", p, win + wout);
            puts("------------------------");
        }
        return;
    }
    simon24 alpha = l;
    // printf("alpha=%u\n", alpha);
    int cnt = 0, vec[24];
    for (int i = 0; i < n; i++)
        vec[i] = -1;
    for (int i = 0; i < n; i++)
    {
        bool s1 = bit(alpha, (i - 1 + n) % n);
        bool s8 = bit(alpha, (i - 8 + n) % n);
        bool s6 = bit(alpha, (i + 6) % n);
        // cout << s1 << " " << s6 << " " << s8 << endl;
        if (s1 | s8 == 1)
        {
            if (vec[i] == -1)
                vec[i] = i;
            cnt++;
            if (s1 == 0 && s6 == 1 && s8 == 1)
            {
                vec[(i + 7) % n] = vec[i];
                cnt--;
            }
        }
    }
    if (p + cnt + B[R - round] > B[R])
        return;
    simon24 w = (1 << cnt);
    simon24 beta = (lshift(alpha, 1) & lshift(alpha, 8)) ^ lshift(alpha, 2);
    for (int i = 0; i < w; i++)
    {
        simon24 res = beta;
        for (int j = 0, tmp = 0; j < n; j++)
        {
            if (vec[j] == j)
            {
                res ^= (bit(i, tmp) << j);
                tmp++;
            }
        }
        for (int j = 0; j < n; j++)
        {
            if (vec[j] != -1 && vec[j] != j)
            {
                if (bit(res, j) ^ bit(res, vec[j]))
                {
                    res ^= (1 << j);
                }
            }
        }
        dfs(r ^ res, l, round + 1, p + cnt);
    }
    // printf("%d\n", cnt);
    // for (int i = 0; i < n; i++)
    // {
    //     printf("%d ", vec[i]);
    // }
    // puts("");
    return;
}

int main()
{
    // freopen("24.log", "w", stdout);
    clock_t start, end;
    start = clock();
    for (int i = 0; i < 48; i++)
        mx |= (1ULL << i);
    // printf("%llx\n", mxv);
    int tmpw = 0, total = 0, pr = 0;
    for (simon48 i = 1, js = 0; i <= mx; i = next(i))
    {
        js++;
        simon24 l = i >> n, r = i % (1 << n);
        if (bit(l, 0) | bit(r, 0) == 0)
            continue;
        win = wt(i);
        if (win > tmpw)
        {
            printf("Start search delta in with hamming weight %d\n", win);
            tmpw = win;
            total = C[win];
            js = 1;
            pr = 0;
        }
        if (win >= minw)
        {
            printf("Stop at ( %x , %x )\n", l, r);
            break;
        }
        int rate = 100 * js / total;
        if (rate >= pr + 5)
        {
            pr = rate;
            end = clock();
            printf("Processed: %d%    Time: %.2fs\n", rate, (double)(end - start) / CLOCKS_PER_SEC);
        }
        lin = l;
        rin = r;
        dfs(l, r, 1, 0);
    }
    return 0;
}
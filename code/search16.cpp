#include <bits/stdc++.h>
#define simon16 unsigned short
#define simon32 unsigned int
#define ctz __builtin_ctz
#define wt __builtin_popcount
using namespace std;
int n = 16, R = 14;
int minw = 64, win, wout;
simon16 lin, rin;
simon32 mx;
int B[20] = {0, 0, 2, 4, 6, 8, 12, 14, 18, 20, 25, 30, 34, 36, 38};
int C[10] = {0, 32, 496, 4960, 35960, 201376};

simon32 next_perm(simon32 v)
{
    simon32 t = v | (v - 1);
    return (t + 1) | (((~t & -~t) - 1) >> (ctz(v) + 1));
}

simon32 next(simon32 cur)
{
    return ((cur - 1) | cur) >= mx ? (1ULL << (wt(cur) + 1)) - 1 : next_perm(cur);
}

inline bool bit(simon16 x, int pos) { return (x & (1 << pos)) == 0 ? 0 : 1; }

inline simon16 lshift(simon16 x, int pos) { return (x << pos) | (x >> (n - pos)); }

void dfs(simon16 l, simon16 r, int round, int p)
{
    // printf("l=%x r=%x round=%d p=2^{-%d}\n", l, r, round, p);
    if (round > R)
    {
        wout = wt(l) + wt(r);
        if (win + wout <= minw)
        {
            minw = win + wout;
        }
        puts("------------------------");
        printf("Delta in: ( %x , %x )\n", lin, rin);
        printf("Delta out: ( %x , %x )\n", l, r);
        printf("p=2^{-%d} wt=%d\n", p, win + wout);
        puts("------------------------");
        return;
    }
    simon16 alpha = l;
    // printf("alpha=%u\n", alpha);
    int cnt = 0, vec[16];
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
        else
        {
            vec[i] = -1;
        }
    }
    if (p + cnt + B[R - round] > B[R])
        return;
    simon16 w = (1 << cnt);
    simon16 beta = (lshift(alpha, 1) & lshift(alpha, 8)) ^ lshift(alpha, 2);
    for (int i = 0; i < w; i++)
    {
        simon16 res = beta;
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
    // freopen("16.log", "w", stdout);
    clock_t start, end;
    start = clock();
    for (int i = 0; i < 32; i++)
        mx |= (1ULL << i);
    // printf("%llx\n", mxv);
    int tmpw = 0, total = 0, pr = 0;
    for (simon32 i = 1, js = 0; i <= mx; i = next(i))
    {
        js++;
        simon16 l = i >> n, r = i % (1 << n);
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
        if (rate && rate % 5 == 0 && rate > pr)
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
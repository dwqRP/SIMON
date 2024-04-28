#include <bits/stdc++.h>
#define simon16 unsigned short
#define simon32 unsigned int
#define wt __builtin_popcount
using namespace std;
int n = 16, R = 14;
int minw = 64, win, wout;
simon16 lin, rin;
int B[20] = {0, 0, 2, 4, 6, 8, 12, 14, 18, 20, 25, 30, 34, 36, 38};

simon32 next_perm(simon32 v)
{
    simon32 t = v | (v - 1);
    return (t + 1) | (((~t & -~t) - 1) >> (__builtin_ctz(v) + 1));
}

simon32 next(simon32 cur, simon32 mx)
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
            printf("Delta in: ( %x , %x )\n", lin, rin);
            printf("Delta out: ( %x , %x )\n", l, r);
            printf("p=2^{-%d} wt=%d\n", p, win + wout);
            puts("------------");
        }
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
    simon32 mxv = UINT32_MAX;
    printf("%llx\n", mxv);
    int tmpw = 0;
    for (simon32 i = 1; i <= mxv; i = next(i, mxv))
    {
        simon16 l = i >> n, r = i % (1 << n);
        lin = l;
        rin = r;
        win = wt(l) + wt(r);
        if (win > tmpw)
        {
            printf("Start search delta in with hamming weight %d\n", win);
            tmpw = win;
        }
        else if (win < tmpw)
        {
            puts("ERROR!");
        }
        if (win >= minw)
        {
            printf("Stop at ( %x , %x )\n", l, r);
            break;
        }
        dfs(l, r, 1, 0);
    }
    return 0;
}
#include <bits/stdc++.h>
using namespace std;
#define simon16 unsigned short
#define simon32 unsigned int
int n = 16, R = 14, midR = 7;
int threshold = 7;
// int minp = 600, maxp = 0;
simon16 lin = 0x0000;
simon16 rin = 0x0001;
simon16 lout = 0x0400;
simon16 rout = 0x0100;
double prob = 0;
bool flag = 0;
struct state
{
    simon16 x, y;
    bool operator<(const state &other) const
    {
        if (x != other.x)
            return x < other.x;
        return y < other.y;
    }
};
map<state, double> mp;
map<state, double>::iterator iter;
// int num[700];

inline bool bit(simon16 x, int pos) { return (x & (1 << pos)) == 0 ? 0 : 1; }

inline simon16 lshift(simon16 x, int pos) { return (x << pos) | (x >> (n - pos)); }

inline double add_prob(double x, double y) { return -log2(pow(2, -x) + pow(2, -y)); }

void dfs(simon16 l, simon16 r, int round, int p, bool rev)
{
    // printf("l=%x r=%x round=%d p=2^{-%d}\n", l, r, round, p);
    if (rev == 0 && round > midR)
    {
        // add this internal state to hash table
        // printf("l=%x r=%x round=%d p=2^{-%d}\n", l, r, round, p);
        state st = (state){l, r};
        iter = mp.find(st);
        if (iter != mp.end())
            mp[(state){l, r}] = add_prob(iter->second, p);
        else
            mp[(state){l, r}] = p;
        return;
    }
    if (rev && round <= midR)
    {
        // check for matches and calc prob
        state st = (state){l, r};
        iter = mp.find(st);
        if (iter != mp.end())
        {
            if (flag == 0)
            {
                prob = p + iter->second;
                flag = 1;
            }
            else
            {
                prob = add_prob(prob, p + iter->second);
                // printf("%f\n", prob);
            }
        }
        return;
    }
    simon16 alpha = rev ? r : l;
    int cnt = 0, vec[16];
    for (int i = 0; i < n; i++)
        vec[i] = -1;
    for (int i = 0; i < n; i++)
    {
        bool s1 = bit(alpha, (i - 1 + n) % n);
        bool s8 = bit(alpha, (i - 8 + n) % n);
        bool s6 = bit(alpha, (i + 6) % n);
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
    if (cnt > threshold)
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
        if (rev)
            dfs(r, l ^ res, round - 1, p + cnt, 1);
        else
            dfs(r ^ res, l, round + 1, p + cnt, 0);
    }
    return;
}
int main()
{
    dfs(lin, rin, 1, 0, 0);
    dfs(lout, rout, R, 0, 1);
    printf("%f\n", prob);
    return 0;
}
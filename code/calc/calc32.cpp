#include <bits/stdc++.h>
using namespace std;
#define simon32 unsigned int
const int gap = 1e6;
int n = 32, R = 23, midR = 11;
int single_threshold = 8;
int forward_threshold = 45;
int backward_threshold = 59;
simon32 lin = 0x00000004;
simon32 rin = 0x00000011;
simon32 lout = 0x00000111;
simon32 rout = 0x00000040;
double prob = 0;
bool flag = 0;
clock_t start, ed;
struct state
{
    simon32 x, y;
    bool operator<(const state &other) const
    {
        if (x != other.x)
            return x < other.x;
        return y < other.y;
    }
};
map<state, double> mp;
map<state, double>::iterator iter;
int num = 0;

inline bool bit(simon32 x, int pos) { return (x & (1 << pos)) == 0 ? 0 : 1; }

inline simon32 lshift(simon32 x, int shift) { return (x << shift) | (x >> (n - shift)); }

inline double add_prob(double x, double y) { return -log2(pow(2, -x) + pow(2, -y)); }

void dfs(simon32 l, simon32 r, int round, int p, bool rev)
{
    // printf("l=%x r=%x round=%d p=2^{-%d}\n", l, r, round, p);
    if (rev == 0 && round > midR)
    {
        // add this internal state to hash table
        num++;
        if (num == gap)
        {
            ed = clock();
            printf("Upper Part: add 10^6 forward trails    Time: %.2fs\n", (double)(ed - start) / CLOCKS_PER_SEC);
            num = 0;
        }
        state st = (state){l, r};
        iter = mp.find(st);
        if (iter != mp.end())
            mp[st] = add_prob(iter->second, p);
        else
            mp[st] = p;
        return;
    }
    if (rev && round <= midR)
    {
        // check for matches and calc prob
        num++;
        if (num == gap)
        {
            ed = clock();
            printf("Lower Part: add 10^6 backward trails    Time: %.2fs    Prob: %.10f\n", (double)(ed - start) / CLOCKS_PER_SEC, prob);
            num = 0;
        }
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
    if (rev == 0 && p > forward_threshold)
        return;
    if (rev && p > backward_threshold)
        return;
    simon32 alpha = rev ? r : l;
    int cnt = 0, vec[32];
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
    if (cnt > single_threshold)
        return;
    simon32 w = (1 << cnt);
    simon32 beta = (lshift(alpha, 1) & lshift(alpha, 8)) ^ lshift(alpha, 2);
    for (int i = 0; i < w; i++)
    {
        simon32 res = beta;
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
    start = clock();
    dfs(lin, rin, 1, 0, 0);
    num = 0;
    dfs(lout, rout, R, 0, 1);
    printf("%f\n", prob);
    return 0;
}
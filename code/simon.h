#ifndef __SIMON__
#define __SIMON__

#include <bits/stdc++.h>
#define simon(x) bitset<x>
typedef unsigned char uc;

extern uc N;

template <class T>
class full_state
{
private:
    T s;

public:
    inline void nxt()
    {
        uc num = s.count();
        bool check = 1;
        for (uc i = N - num; i < N; i++)
            check &= s[i];
        if (check)
        {
            s = 0;
            for (uc i = 0; i <= num; i++)
                s[i] = 1;
        }
        else
        {
            uc ctz = 0;
            for (uc i = 0; i < N - 1; i++)
            {
                if (!s[i])
                    ctz++;
                if (s[i] == 1 && s[i + 1] == 0)
                {
                    s[i] = 0, s[i + 1] = 1;
                    for (uc j = 0; j < i; j++)
                        s[i] = (j < (i - ctz));
                }
                break;
            }
        }
        return;
    }
};

#endif
#ifndef __SIMON__
#define __SIMON__

#include <bitset>
#include <cstdio>
#define simon(x) bitset<x>
// typedef unsigned char uc;

extern const char N;

template <class T>
class full_state
{
private:
    T s;

public:
    full_state(char pos = -1)
    {
        s = 0;
        if (pos >= 0)
            s[pos] = 1;
    }
    inline void print()
    {
        for (char i = N - 1; i >= 0; i--)
            putchar(s[i] ? '1' : '0');
        puts("");
        return;
    }
    inline bool valid()
    {
        return s.count() < N;
    }
    inline void nxt()
    {
        char num = s.count();
        bool check = 1;
        for (char i = N - num; i < N; i++)
            check &= s[i];
        if (check)
        {
            s = 0;
            for (char i = 0; i <= num; i++)
                s[i] = 1;
        }
        else
        {
            char ctz = 0;
            for (char i = 0; i < N - 1; i++)
            {
                if (!s[i])
                    ctz++;
                if (s[i] == 1 && s[i + 1] == 0)
                {
                    s[i] = 0, s[i + 1] = 1;
                    for (char j = 0; j < i; j++)
                        s[j] = (j < (i - ctz));
                    break;
                }
            }
        }
        return;
    }
};

#endif
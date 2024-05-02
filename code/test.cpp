#include "simon.h"
#include <bits/stdc++.h>
using namespace std;
const char N = 24;
clock_t st, ed;
int main()
{
    st = clock();
    for (full_state<simon(N)> i(0); i.valid(); i.nxt())
    {
        // i.print();
    }
    ed = clock();
    printf("Time: %.2fs\n", (double)(ed - st) / CLOCKS_PER_SEC);
    return 0;
}
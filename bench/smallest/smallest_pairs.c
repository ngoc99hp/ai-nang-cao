#include <stdio.h>

void read4(int *a, int *b, int *c, int *d)
{
    scanf("%d %d %d %d", a, b, c, d);
}

void min_of(int x, int y, int *m)
{
    if (x < y)
        *m = x;
    else
        *m = y;
}

int main()
{
    int a, b, c, d, m1, m2, m;
    printf("Please enter 4 numbers separated by spaces > ");
    read4(&a, &b, &c, &d);
    min_of(a, b, &m1);
    min_of(c, d, &m2);
    min_of(m1, m2, &m);
    printf("%d is the smallest\n", m);
    return 0;
}

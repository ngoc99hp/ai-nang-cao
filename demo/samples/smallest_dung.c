#include <stdio.h>

int main()
{
    int a, b, c, d, m;
    printf("Please enter 4 numbers separated by spaces > ");
    scanf("%d %d %d %d", &a, &b, &c, &d);
    m = a;
    if (b < m) m = b;
    if (c < m) m = c;
    if (d < m) m = d;
    printf("%d is the smallest\n", m);
    return 0;
}

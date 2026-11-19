#include <stdio.h>

void update_min(int *m, int x)
{
    if (x < *m)
        *m = x;
}

int main()
{
    int a[4], i, min;
    printf("Please enter 4 numbers separated by spaces > ");
    for (i = 0; i < 4; i++)
        scanf("%d", &a[i]);
    min = a[0];
    for (i = 1; i < 4; i++)
        update_min(&min, a[i]);
    printf("%d is the smallest\n", min);
    return 0;
}

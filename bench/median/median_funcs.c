#include <stdio.h>

void minmax(int a[], int n, int *lo, int *hi)
{
    int i;
    *lo = a[0];
    *hi = a[0];
    for (i = 1; i < n; i++) {
        if (a[i] < *lo)
            *lo = a[i];
        if (a[i] > *hi)
            *hi = a[i];
    }
}

int main()
{
    int a[3], i, lo, hi, total = 0;
    printf("Please enter 3 numbers separated by spaces > ");
    for (i = 0; i < 3; i++) {
        scanf("%d", &a[i]);
        total += a[i];
    }
    minmax(a, 3, &lo, &hi);
    printf("%d is the median\n", total - lo - hi);
    return 0;
}

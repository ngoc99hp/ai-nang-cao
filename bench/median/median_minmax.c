#include <stdio.h>

int main()
{
    int a[3], i, sum = 0, mx, mn;
    printf("Please enter 3 numbers separated by spaces > ");
    for (i = 0; i < 3; i++)
        scanf("%d", &a[i]);
    mx = a[0];
    mn = a[0];
    for (i = 0; i < 3; i++) {
        sum += a[i];
        if (a[i] > mx)
            mx = a[i];
        if (a[i] < mn)
            mn = a[i];
    }
    printf("%d is the median\n", sum - mx - mn);
    return 0;
}

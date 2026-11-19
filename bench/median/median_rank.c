#include <stdio.h>

int main()
{
    int a[3], i, j, lo, hi, med = 0;
    printf("Please enter 3 numbers separated by spaces > ");
    for (i = 0; i < 3; i++)
        scanf("%d", &a[i]);
    for (i = 0; i < 3; i++) {
        lo = 0;
        hi = 0;
        for (j = 0; j < 3; j++) {
            if (a[j] < a[i])
                lo++;
            else if (a[j] > a[i])
                hi++;
        }
        if (lo <= 1 && hi <= 1) {
            med = a[i];
            break;
        }
    }
    printf("%d is the median\n", med);
    return 0;
}

#include <stdio.h>

void swap(int *x, int *y)
{
    int t = *x;
    *x = *y;
    *y = t;
}

int main()
{
    int a[3], i, j;
    printf("Please enter 3 numbers separated by spaces > ");
    for (i = 0; i < 3; i++)
        scanf("%d", &a[i]);
    for (i = 1; i < 3; i++) {
        j = i;
        while (j > 0 && a[j - 1] > a[j]) {
            swap(&a[j - 1], &a[j]);
            j--;
        }
    }
    printf("%d is the median\n", a[1]);
    return 0;
}

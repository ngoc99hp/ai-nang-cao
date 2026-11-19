#include <stdio.h>

void swap(int *p, int *q)
{
    int t = *p;
    *p = *q;
    *q = t;
}

int main()
{
    int a[4], i, j;
    printf("Please enter 4 numbers separated by spaces > ");
    for (i = 0; i < 4; i++)
        scanf("%d", &a[i]);
    for (i = 0; i < 3; i++) {
        for (j = 0; j < 3 - i; j++) {
            if (a[j] > a[j + 1])
                swap(&a[j], &a[j + 1]);
        }
    }
    printf("%d is the smallest\n", a[0]);
    return 0;
}

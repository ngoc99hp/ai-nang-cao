#include <stdio.h>

void swap(int *a, int *b)
{
    int t = *a;
    *a = *b;
    *b = t;
}

int main()
{
    int a[3], i, j;
    printf("Please enter 3 numbers separated by spaces > ");
    for (i = 0; i < 3; i++)
        scanf("%d", &a[i]);
    for (i = 0; i < 2; i++) {
        for (j = 0; j < 2 - i; j++) {
            if (a[j] > a[j + 1])
                swap(&a[j], &a[j + 1]);
        }
    }
    printf("%d is the median\n", a[1]);
    return 0;
}

#include <stdio.h>

int find_min(int a[], int n)
{
    int i, min;
    min = a[0];
    for (i = 1; i < n; i++) {
        if (a[i] < min)
            min = a[i];
    }
    return min;
}

int main()
{
    int a[4], i;
    printf("Please enter 4 numbers separated by spaces > ");
    for (i = 0; i < 4; i++)
        scanf("%d", &a[i]);
    printf("%d is the smallest\n", find_min(a, 4));
    return 0;
}

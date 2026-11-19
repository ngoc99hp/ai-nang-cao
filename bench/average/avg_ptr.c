#include <stdio.h>

void stats(int a[], int n, int *sum, double *avg)
{
    int i;
    *sum = 0;
    for (i = 0; i < n; i++)
        *sum += a[i];
    *avg = *sum / (double)n;
}

int main()
{
    int n, i, a[100], sum;
    double avg;
    printf("Enter count > ");
    scanf("%d", &n);
    printf("Enter %d integers > ", n);
    for (i = 0; i < n; i++)
        scanf("%d", &a[i]);
    stats(a, n, &sum, &avg);
    printf("Average is %.2f\n", avg);
    return 0;
}

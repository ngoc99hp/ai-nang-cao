#include <stdio.h>

int main()
{
    int n, i, x, sum = 0;
    double avg;
    printf("Enter count > ");
    scanf("%d", &n);
    printf("Enter %d integers > ", n);
    for (i = 0; i < n; i++) {
        scanf("%d", &x);
        sum += x;
    }
    avg = (double)sum / n;
    printf("Average is %.2f\n", avg);
    return 0;
}

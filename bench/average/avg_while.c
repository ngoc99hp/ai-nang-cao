#include <stdio.h>

int main()
{
    int n, k = 0, x, total = 0;
    printf("Enter count > ");
    scanf("%d", &n);
    printf("Enter %d integers > ", n);
    while (k < n) {
        scanf("%d", &x);
        total += x;
        k++;
    }
    printf("Average is %.2f\n", total / (float)n);
    return 0;
}

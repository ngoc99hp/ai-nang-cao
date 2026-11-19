#include <stdio.h>
#include <stdlib.h>

void split(int n, int digits[], int *count)
{
    int i = 0;
    if (n == 0) {
        digits[i] = 0;
        i++;
    }
    while (n != 0) {
        digits[i] = n % 10;
        n = n / 10;
        i++;
    }
    *count = i;
}

int main()
{
    int n, k, i, a[20];
    printf("\nEnter an integer > ");
    scanf("%d", &n);
    printf("\n");
    split(abs(n), a, &k);
    if (n < 0)
        a[k - 1] = -a[k - 1];
    for (i = 0; i < k; i++) {
        printf("%d\n", a[i]);
    }
    printf("That's all, have a nice day!\n");
    return 0;
}

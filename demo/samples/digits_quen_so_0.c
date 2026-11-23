#include <stdio.h>
#include <stdlib.h>

int main()
{
    int n, neg;
    printf("\nEnter an integer > ");
    scanf("%d", &n);
    printf("\n");
    neg = n < 0;
    n = abs(n);
    while (n > 0) {
        if (n < 10 && neg)
            printf("%d\n", -n);
        else
            printf("%d\n", n % 10);
        n = n / 10;
    }
    printf("That's all, have a nice day!\n");
    return 0;
}

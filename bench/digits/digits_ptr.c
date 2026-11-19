#include <stdio.h>

/* Tách chữ số cuối của *n và bỏ nó khỏi *n */
int pop_digit(int *n)
{
    int d = *n % 10;
    *n = *n / 10;
    return d;
}

int main()
{
    int n, neg = 0, d;
    printf("\nEnter an integer > ");
    scanf("%d", &n);
    printf("\n");
    if (n < 0) {
        neg = 1;
        n = -n;
    }
    do {
        d = pop_digit(&n);
        if (n == 0 && neg == 1)
            printf("%d\n", -d);
        else
            printf("%d\n", d);
    } while (n > 0);
    printf("That's all, have a nice day!\n");
    return 0;
}

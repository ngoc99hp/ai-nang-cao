#include <stdio.h>

/* Đảm bảo *x <= *y */
void order(int *x, int *y)
{
    int t;
    if (*x > *y) {
        t = *x;
        *x = *y;
        *y = t;
    }
}

int main()
{
    int a, b, c;
    printf("Please enter 3 numbers separated by spaces > ");
    scanf("%d %d %d", &a, &b, &c);
    order(&a, &b);
    order(&b, &c);
    order(&a, &b);
    printf("%d is the median\n", b);
    return 0;
}

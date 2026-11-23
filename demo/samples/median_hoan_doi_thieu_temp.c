#include <stdio.h>

int main()
{
    int a, b, c;
    printf("Please enter 3 numbers separated by spaces > ");
    scanf("%d %d %d", &a, &b, &c);
    if (a > b) { a = b; b = a; }
    if (b > c) { b = c; c = b; }
    if (a > b) { a = b; b = a; }
    printf("%d is the median\n", b);
    return 0;
}

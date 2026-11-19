#include <stdio.h>

int main()
{
    int x, i, smallest;
    printf("Please enter 4 numbers separated by spaces > ");
    scanf("%d", &x);
    smallest = x;
    for (i = 1; i < 4; i++) {
        scanf("%d", &x);
        if (x < smallest)
            smallest = x;
    }
    printf("%d is the smallest\n", smallest);
    return 0;
}

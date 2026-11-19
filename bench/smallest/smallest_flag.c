#include <stdio.h>

int main()
{
    int x, k = 0, least = 0, first = 1;
    printf("Please enter 4 numbers separated by spaces > ");
    while (k < 4) {
        scanf("%d", &x);
        if (first == 1 || x < least) {
            least = x;
            first = 0;
        }
        k++;
    }
    printf("%d is the smallest\n", least);
    return 0;
}

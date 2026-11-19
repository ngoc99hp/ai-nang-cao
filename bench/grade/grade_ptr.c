#include <stdio.h>

void classify(float score, float a, float b, float c, float d, char *g)
{
    if (score >= a)
        *g = 'A';
    else if (score >= b)
        *g = 'B';
    else if (score >= c)
        *g = 'C';
    else if (score >= d)
        *g = 'D';
    else
        *g = 'F';
}

int main()
{
    float a, b, c, d, score;
    char g;
    printf("Enter thresholds for A, B, C, D\nin that order, decreasing percentages > ");
    scanf("%f %f %f %f", &a, &b, &c, &d);
    printf("Thank you. Now enter student score (percent) >");
    scanf("%f", &score);
    classify(score, a, b, c, d, &g);
    if (g == 'F')
        printf("Student has failed the course\n");
    else
        printf("Student has an %c grade\n", g);
    return 0;
}

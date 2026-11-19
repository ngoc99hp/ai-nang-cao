#include <stdio.h>

void read_score(float *s)
{
    scanf("%f", s);
}

char letter_for(float score, float t[], int n)
{
    char letters[] = "ABCD";
    int i;
    for (i = 0; i < n; i++) {
        if (score >= t[i])
            return letters[i];
    }
    return 'F';
}

int main()
{
    float t[4], score;
    int i;
    char g;
    printf("Enter thresholds for A, B, C, D\nin that order, decreasing percentages > ");
    for (i = 0; i < 4; i++)
        scanf("%f", &t[i]);
    printf("Thank you. Now enter student score (percent) >");
    read_score(&score);
    g = letter_for(score, t, 4);
    if (g == 'F')
        printf("Student has failed the course\n");
    else
        printf("Student has an %c grade\n", g);
    return 0;
}

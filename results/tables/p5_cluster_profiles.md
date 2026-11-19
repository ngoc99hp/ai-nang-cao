# Hồ sơ cụm — dữ liệu thật IntroClass (K-modes, trọng số DP3, k theo DP4)

Đặc trưng: cặp thuộc tính = giá trị có tần suất trong cụm ≥ 50% và cao hơn toàn bài rõ nhất (cụm% / toàn bài%). Bỏ qua giá trị F / none / n/a / 0.

## digits — 108 bài, 54 SV, k = 5

### digits / Cụm 0 — 60 bài, 35 SV

**Đặc trưng:** `D:diff.missing_output=T` (85%/61%); `O:tests.fail_frac=low` (93%/84%); `O:tests_zero.fail=all` (72%/64%); `O:output.missing_answer=T` (75%/68%); `O:tests_single_digit.fail=some` (78%/73%); `A:condition.if_cmp=strict` (53%/49%)

**Luật ILA (coverage cao nhất):**

- `R1: NẾU [D:diff.neg_extra = F] VÀ [D:diff.var_changed = F] THÌ Cụm 0 [coverage 47/60, accuracy 1.00]`
- `R2: NẾU [O:tests_inner_zero.fail = none] VÀ [A:negation.uses_abs = F] VÀ [D:diff.missing_output = T] THÌ Cụm 0 [coverage 33/60, accuracy 1.00]`
- `R3: NẾU [A:negation.uses_abs = T] VÀ [D:diff.neg_extra = F] THÌ Cụm 0 [coverage 20/60, accuracy 1.00]`

**Bài đại diện** `ic_digits_1b31fa5c50f7_000` vs bản đúng `ic_digits_1b31fa5c50f7_004` (own_fix, sim 0.89) — `-` bản đúng, `+` bài sai:

```diff
-	printf("\nEnter an integer > ");
+	printf("Enter an integer > ");
-	if(n == 0)
-	{
-	printf("%d\n", n);
-	printf("That's all, have a nice day!\n");
-
-        return 0;
-	}
```

### digits / Cụm 1 — 4 bài, 3 SV

**Đặc trưng:** `D:diff.cmp_loop=T` (100%/5%); `D:diff.neg_extra=T` (100%/31%); `D:diff.cmp_kind=reversed` (75%/6%); `D:diff.literal_other=T` (75%/30%); `A:loop.cmp_op=<` (50%/5%); `A:negation.uses_abs=T` (75%/44%)

**Luật ILA (coverage cao nhất):**

- `R15: NẾU [O:output.missing_answer = F] VÀ [D:diff.cmp_loop = T] THÌ Cụm 1 [coverage 3/4, accuracy 1.00]`
- `R16: NẾU [A:loop.cmp_op = <,<=,>] THÌ Cụm 1 [coverage 1/4, accuracy 1.00]`
- `R17: NẾU [D:diff.cmp_kind = mixed] THÌ Cụm 1 [coverage 1/4, accuracy 1.00]`

**Bài đại diện** `ic_digits_90a14c1ac8f5_004` vs bản đúng `ic_digits_90a14c1ac8f5_005` (own_fix, sim 0.90) — `-` bản đúng, `+` bài sai:

```diff
-		value=abs(value);
-		while (value>10){
-			digit=value%10;
+		while (value<-10) {
+			digit=abs(value%10);
-		digit=value%10;
-		printf("-%d\n", digit);
-		digit=value;
+		digit=0;
```

### digits / Cụm 2 — 19 bài, 12 SV

**Đặc trưng:** `D:diff.literal_other=T` (100%/30%); `D:diff.stmt_extra=T` (68%/17%); `D:diff.var_changed=T` (100%/53%); `D:diff.init_value=T` (79%/44%); `O:tests_inner_zero.fail=some` (53%/19%); `O:tests_zero.fail=all` (84%/64%)

**Luật ILA (coverage cao nhất):**

- `R18: NẾU [D:diff.literal_other = T] VÀ [D:diff.stmt_extra = T] THÌ Cụm 2 [coverage 13/19, accuracy 1.00]`
- `R19: NẾU [O:tests.fail_frac = mid] VÀ [D:diff.literal_other = T] THÌ Cụm 2 [coverage 8/19, accuracy 1.00]`
- `R20: NẾU [A:accumulator.init = expr] THÌ Cụm 2 [coverage 2/19, accuracy 1.00]`

**Bài đại diện** `ic_digits_387be36eafae_000` vs bản đúng `ic_digits_90a14c1ac8f5_005` (nearest, sim 0.55) — `-` bản đúng, `+` bài sai:

```diff
-#include <stdio.h>
-#include <stdlib.h>
+#include<stdio.h>
+#include<math.h>
-int main(void)
-{
-	int value, digit;
-	printf("\nEnter an integer > ");
-	scanf("%d", &value);
-	printf("\n");
-	if (value>0){
-		while (value!=0) {
-			digit=value%10;
-			value=value/10;
… (57 dòng nữa)
```

### digits / Cụm 3 — 15 bài, 11 SV

**Đặc trưng:** `D:diff.neg_extra=T` (87%/31%); `D:diff.extra_output=T` (67%/12%); `O:tests_inner_zero.fail=some` (67%/19%); `D:diff.neg_missing=T` (93%/50%); `D:diff.init_value=T` (87%/44%); `D:diff.var_changed=T` (93%/53%)

**Luật ILA (coverage cao nhất):**

- `R24: NẾU [O:tests_inner_zero.fail = some] VÀ [D:diff.extra_output = T] THÌ Cụm 3 [coverage 7/15, accuracy 1.00]`
- `R25: NẾU [A:negation.uses_abs = T] VÀ [D:diff.extra_output = T] THÌ Cụm 3 [coverage 6/15, accuracy 1.00]`
- `R26: NẾU [O:tests_zero.fail = none] VÀ [A:loop.return_in_loop = T] THÌ Cụm 3 [coverage 4/15, accuracy 1.00]`

**Bài đại diện** `ic_digits_ca94e3756cbf_002` vs bản đúng `ic_digits_d43d32076778_001` (nearest, sim 0.50) — `-` bản đúng, `+` bài sai:

```diff
-#include <math.h>
+#include <stdlib.h>
+int main () {
-int
-main(void)
-{
-    int input, digits;
+	int n;
+	int x, y;
+	int temp;
-    //**/
-    printf("Enter an integer > ");
-    scanf("%d", &input);
+	printf("\nEnter an integer > ");
… (56 dòng nữa)
```

### digits / Cụm 4 — 10 bài, 7 SV

**Đặc trưng:** `D:diff.extra_break=T` (60%/7%); `D:diff.neg_missing=T` (100%/50%); `A:loop.break_in_loop=T` (60%/11%); `D:diff.var_changed=T` (100%/53%); `O:run.nondet_dataset=T` (60%/17%); `D:diff.neg_extra=T` (70%/31%)

**Luật ILA (coverage cao nhất):**

- `R32: NẾU [A:condition.if_cmp = strict] VÀ [D:diff.extra_break = T] THÌ Cụm 4 [coverage 4/10, accuracy 1.00]`
- `R33: NẾU [O:tests_inner_zero.fail = none] VÀ [A:loop.cmp_op = none] VÀ [D:diff.stmt_missing = T] THÌ Cụm 4 [coverage 3/10, accuracy 1.00]`
- `R34: NẾU [O:output.missing_answer = T] VÀ [O:tests_single_digit.fail = all] THÌ Cụm 4 [coverage 2/10, accuracy 1.00]`

**Bài đại diện** `ic_digits_f2997e14a460_002` vs bản đúng `ic_digits_d120480a6e4b_003` (nearest, sim 0.68) — `-` bản đúng, `+` bài sai:

```diff
-#include <stdlib.h>
+#include <math.h>
-int main (void) {
+int main () {
-  int n, digit;
+  int digit, input;
-  scanf ("%d", &n);
-  printf ("\n");
-
-  //**/
+  scanf("%d", &input);
-  if (n==0) {
-    printf ("0\n");
-  }
… (31 dòng nữa)
```

## grade — 38 bài, 22 SV, k = 4

### grade / Cụm 0 — 15 bài, 12 SV

**Đặc trưng:** `D:diff.size=6-20` (73%/34%); `A:condition.if_cmp=nonstrict` (67%/29%); `O:tests_failing.fail=all` (87%/55%); `D:diff.missing_output=T` (73%/50%); `O:output.missing_answer=T` (60%/45%); `O:tests.fail_frac=low` (80%/68%)

**Luật ILA (coverage cao nhất):**

- `R1: NẾU [O:tests_top.fail = none] VÀ [D:diff.size = 6-20] THÌ Cụm 0 [coverage 10/15, accuracy 1.00]`
- `R2: NẾU [A:condition.if_cmp = nonstrict] VÀ [D:diff.missing_output = T] THÌ Cụm 0 [coverage 7/15, accuracy 1.00]`
- `R3: NẾU [O:tests.fail_frac = all] THÌ Cụm 0 [coverage 1/15, accuracy 1.00]`

**Bài đại diện** `ic_grade_48b82975576f_000` vs bản đúng `ic_grade_48b82975576f_001` (own_fix, sim 0.97) — `-` bản đúng, `+` bài sai:

```diff
-else printf("Student has failed the course\n");
+
```

### grade / Cụm 1 — 7 bài, 5 SV

**Đặc trưng:** `D:diff.var_changed=T` (86%/29%); `D:diff.size=21+` (100%/45%); `O:run.nondet_dataset=T` (57%/34%); `A:condition.if_cmp=mixed` (71%/53%); `O:output.grade_too_high=T` (57%/42%); `O:tests_boundary.fail=some` (71%/58%)

**Luật ILA (coverage cao nhất):**

- `R7: NẾU [O:tests_top.fail = none] VÀ [D:diff.var_changed = T] THÌ Cụm 1 [coverage 6/7, accuracy 1.00]`
- `R8: NẾU [D:diff.missing_output = F] VÀ [D:diff.size = 21+] THÌ Cụm 1 [coverage 6/7, accuracy 1.00]`
- `R9: NẾU [D:diff.stmt_extra = T] THÌ Cụm 1 [coverage 1/7, accuracy 1.00]`

**Bài đại diện** `ic_grade_b1924d63a2e2_001` vs bản đúng `ic_grade_b1924d63a2e2_004` (own_fix, sim 0.67) — `-` bản đúng, `+` bài sai:

```diff
-#include <stdio.h>
-#include <math.h>
+#include<stdio.h>
-float A, B, C, D, Grade;
+	float a,b,c,d,score;
-printf("Enter thresholds for A, B, C, D\nin that order, decreasing percentages > ");
-scanf("%f" "%f" "%f" "%f", &A, &B, &C, &D);
-printf("Thank you. Now enter student score (percent) >");
-scanf("%f", &Grade);
+	printf("Enter thresholds for A, B, C, D \nin that order, decreasing percentages > ");
+	scanf("%f %f %f %f",&a,&b,&c,&d);
-if(Grade >= D){
-	if(Grade >= C){
-		if(Grade >= B){
… (30 dòng nữa)
```

### grade / Cụm 2 — 4 bài, 1 SV

**Đặc trưng:** `O:tests.fail_frac=high` (100%/11%); `D:diff.ptr_missing=T` (100%/11%); `D:diff.init_value=T` (100%/11%); `A:division.int_div_float_ctx=T` (100%/11%); `D:diff.cmp_kind=reversed` (100%/13%); `O:tests_top.fail=all` (100%/16%)

**Luật ILA (coverage cao nhất):**

- `R10: NẾU [O:tests.fail_frac = high] THÌ Cụm 2 [coverage 4/4, accuracy 1.00]`

**Bài đại diện** `ic_grade_af81ffd4bc47_000` vs bản đúng `ic_grade_af81ffd4bc47_011` (own_fix, sim 0.71) — `-` bản đúng, `+` bài sai:

```diff
-float a, b, c, d, score;
+double a, b, c, d;
+double per;
-scanf("%f""%f""%f""%f", &a, &b, &c, &d);
-printf("Thank you. Now enter student score (percent) >");
-scanf("%f", &score);
+scanf("%lf""%lf""%lf""%lf", &a, &b, &c, &d);
-if(score>=a)
-printf("Student has an A grade\n");
+per = (a+b+c+d)/4;
-else if (score>=b)
-printf("Student has an B grade\n");
+if(per<60)
+printf("Thank you. Now enter student score (percent) >Student has an B grade\n");
… (12 dòng nữa)
```

### grade / Cụm 3 — 12 bài, 7 SV

**Đặc trưng:** `D:diff.cmp_kind=strictness` (92%/29%); `O:tests_top.fail=some` (83%/26%); `D:diff.cmp_if=T` (92%/42%); `D:diff.size=2-5` (50%/16%); `O:output.grade_too_low=T` (58%/32%); `O:tests_boundary.fail=some` (83%/58%)

**Luật ILA (coverage cao nhất):**

- `R11: NẾU [D:diff.cmp_kind = strictness] THÌ Cụm 3 [coverage 11/12, accuracy 1.00]`
- `R12: NẾU [O:tests_top.fail = some] THÌ Cụm 3 [coverage 10/12, accuracy 1.00]`

**Bài đại diện** `ic_grade_e23b96b6bab2_001` vs bản đúng `ic_grade_e23b96b6bab2_003` (own_fix, sim 0.97) — `-` bản đúng, `+` bài sai:

```diff
-	if (percent >= a)
+	if (percent > a)
-	else if (percent < a && percent >= b)
+	else if (percent <= a && percent >= b)
-	else if (percent < b && percent >= c)
+	else if (percent <= b && percent >= c)
-	else if (percent < c && percent >= d)
+	else if (percent <= c && percent >= d)
```

## median — 69 bài, 44 SV, k = 5

### median / Cụm 0 — 27 bài, 19 SV

**Đặc trưng:** `D:diff.cmp_if=T` (93%/45%); `D:diff.cmp_kind=strictness` (52%/22%); `O:output.missing_answer=T` (67%/45%); `O:tests_tie.fail=all` (52%/35%); `A:condition.if_cmp=strict` (81%/67%); `O:tests_zero.fail=some` (85%/71%)

**Luật ILA (coverage cao nhất):**

- `R1: NẾU [D:diff.cmp_if = T] VÀ [D:diff.stmt_missing = F] THÌ Cụm 0 [coverage 21/27, accuracy 1.00]`
- `R2: NẾU [O:output.off_by_one = F] VÀ [D:diff.cmp_if = T] THÌ Cụm 0 [coverage 19/27, accuracy 1.00]`
- `R3: NẾU [D:diff.size = 2-5] THÌ Cụm 0 [coverage 3/27, accuracy 1.00]`

**Bài đại diện** `ic_median_1b31fa5c50f7_000` vs bản đúng `ic_median_1b31fa5c50f7_003` (own_fix, sim 0.86) — `-` bản đúng, `+` bài sai:

```diff
-	if((((num1 >= num2) && (num1 <= num3))) || ((num1 >= num3) && (num1 <= num2)))
+	if((((num1 > num2) && (num1 < num3))) || ((num1 > num3) && (num1 < num2)))
-	else if((((num2 >= num1) && (num2 <= num3))) || ((num2 >= num3) && (num2 <= num1)))
+	else if((((num2 > num1) && (num2 < num3))) || ((num2 > num3) && (num2 < num1)))
-	else
+	else if((((num3 > num2) && (num3 < num1))) || ((num3 > num1) && (num3 < num2)))
+
```

### median / Cụm 1 — 19 bài, 13 SV

**Đặc trưng:** `D:diff.var_changed=T` (74%/43%); `D:diff.stmt_missing=T` (58%/30%); `O:output.wrong_input_elem=T` (63%/42%); `O:tests.fail_frac=low` (84%/87%); `D:diff.size=21+` (63%/71%); `O:tests_zero.fail=some` (58%/71%)

**Luật ILA (coverage cao nhất):**

- `R6: NẾU [D:diff.cmp_if = F] VÀ [D:diff.missing_output = F] VÀ [D:diff.var_changed = T] THÌ Cụm 1 [coverage 12/19, accuracy 1.00]`
- `R7: NẾU [O:output.off_by_one = T] VÀ [A:condition.if_cmp = nonstrict] VÀ [D:diff.var_changed = T] THÌ Cụm 1 [coverage 5/19, accuracy 1.00]`
- `R8: NẾU [D:diff.stmt_missing = T] VÀ [D:diff.size = 6-20] THÌ Cụm 1 [coverage 4/19, accuracy 1.00]`

**Bài đại diện** `ic_median_0cdfa335eea3_002` vs bản đúng `ic_median_0cdfa335eea3_010` (own_fix, sim 0.63) — `-` bản đúng, `+` bài sai:

```diff
-  int a, b, c, temp;
+  int a, b, c, median;
-  if(a > b)
-  {
-    temp = b;
-    b = a;
-    a = temp;
-//
-  }
-  if(b > c)
-  {
-    temp = c;
-    c = b;
-    b = temp;
… (17 dòng nữa)
```

### median / Cụm 2 — 3 bài, 2 SV

**Đặc trưng:** `D:diff.init_value=T` (100%/10%); `O:tests_zero.fail=all` (67%/3%); `O:tests_sorted.fail=all` (67%/3%); `O:tests.fail_frac=all` (67%/3%); `O:output.crash=T` (67%/3%); `A:loop.cmp_op=<=` (67%/3%)

**Luật ILA (coverage cao nhất):**

- `R15: NẾU [O:tests_sorted.fail = all] THÌ Cụm 2 [coverage 2/3, accuracy 1.00]`
- `R16: NẾU [O:output.not_input_elem = T] VÀ [O:tests_sorted.fail = none] THÌ Cụm 2 [coverage 1/3, accuracy 1.00]`

**Bài đại diện** `ic_median_d6364e6e98a5_005` vs bản đúng `ic_median_b6fd408d589f_002` (nearest, sim 0.47) — `-` bản đúng, `+` bài sai:

```diff
+//
+
-#include <math.h>
-int main()
-
-{
-	int n1, n2, n3, temp;
-	printf("Please enter 3 numbers separated by spaces > ");
-	scanf("%d%d%d", &n1, &n2, &n3);
-	if(n2<n1)
-	{
-		temp=n2;
-		n2=n1;
-		n1=temp;
… (28 dòng nữa)
```

### median / Cụm 3 — 16 bài, 12 SV

**Đặc trưng:** `D:diff.missing_output=T` (69%/19%); `O:output.missing_answer=T` (56%/45%); `D:diff.size=21+` (81%/71%); `A:condition.if_cmp=strict` (75%/67%); `O:tests_sorted.fail=some` (69%/61%); `O:tests.fail_frac=low` (94%/87%)

**Luật ILA (coverage cao nhất):**

- `R17: NẾU [D:diff.var_changed = F] VÀ [D:diff.stmt_missing = F] VÀ [D:diff.cmp_kind = none] THÌ Cụm 3 [coverage 14/16, accuracy 1.00]`
- `R18: NẾU [D:diff.missing_output = T] VÀ [D:diff.var_changed = F] THÌ Cụm 3 [coverage 9/16, accuracy 1.00]`
- `R19: NẾU [A:extremum.init = expr] THÌ Cụm 3 [coverage 2/16, accuracy 1.00]`

**Bài đại diện** `ic_median_c716ee619761_000` vs bản đúng `ic_median_c716ee619761_007` (own_fix, sim 0.80) — `-` bản đúng, `+` bài sai:

```diff
-	printf("Please enter 3 numbers separated by spaces > ");
+	printf("Pleaes enter 3 numbers seperated by spaces > ");
-	if (A == B && A ==C)
+
+	if ( A > B && A < C)
-	else if ( A > B && A < C)
+	if ( A > C && A < B)
-	else if ( A > C && A < B)
-		printf("%d is the median\n", A);
-	else if ( B > C && B < A)
+	if ( B > C && B < A)
-	else if ( B > A && B < C)
+	if ( B > A && B < C)
-	else if ( C > A && C < B)
… (10 dòng nữa)
```

### median / Cụm 4 — 4 bài, 3 SV

**Đặc trưng:** `D:diff.init_value=T` (100%/10%); `D:diff.stmt_missing=T` (100%/30%); `O:output.off_by_one=T` (100%/32%); `O:tests_tie.fail=some` (100%/35%); `D:diff.cmp_kind=mixed` (75%/13%); `O:output.wrong_input_elem=T` (100%/42%)

**Luật ILA (coverage cao nhất):**

- `R25: NẾU [O:tests_sorted.fail = some] VÀ [D:diff.init_value = T] THÌ Cụm 4 [coverage 4/4, accuracy 1.00]`

**Bài đại diện** `ic_median_1bf73a9ca02e_000` vs bản đúng `ic_median_070455301c2e_010` (nearest, sim 0.59) — `-` bản đúng, `+` bài sai:

```diff
-#include <math.h>
-	int a, b, c, median;
-
-	a = 0;
-	b = 0;
-	c = 0;
-	median = 0;
-	printf("Please enter 3 numbers separated by spaces > ");
-	scanf("%d %d %d", &a, &b, &c);
+	int first, second, third, ans;
-	if ((a<=b && a>=c) || (a>=b && a<=c))
-		median = a;
-	else if ((b<=a && b>=c) || (b>=a && b<=c))
-		median = b;
… (16 dòng nữa)
```

## smallest — 64 bài, 42 SV, k = 4

### smallest / Cụm 0 — 48 bài, 36 SV

**Đặc trưng:** `D:diff.cmp_if=T` (100%/75%); `D:diff.cmp_kind=strictness` (83%/62%); `A:condition.if_cmp=strict` (100%/88%); `O:output.missing_answer=T` (50%/39%); `O:tests_sorted.fail=some` (92%/84%); `D:diff.size=21+` (92%/84%)

**Luật ILA (coverage cao nhất):**

- `R1: NẾU [D:diff.cmp_if = T] THÌ Cụm 0 [coverage 48/48, accuracy 1.00]`

**Bài đại diện** `ic_smallest_90a14c1ac8f5_001` vs bản đúng `ic_smallest_5a5683598d8e_004` (nearest, sim 0.70) — `-` bản đúng, `+` bài sai:

```diff
-//
-//
-//
-
+/**/
-int main() {
-int a, b, c, d; //
+int main()
+{
-
-//
-printf("Please enter 4 numbers separated by spaces > ");
-scanf("%d%d%d%d", &a, &b, &c, &d);
-
… (38 dòng nữa)
```

### smallest / Cụm 1 — 2 bài, 2 SV

**Đặc trưng:** `D:diff.size=1` (100%/3%); `O:run.nondet_dataset=T` (100%/16%); `O:tests_negative.fail=some` (100%/17%); `O:tests.fail_frac=mid` (100%/36%); `A:loop.cmp_op=<,<=,>` (50%/2%); `D:diff.literal_other=T` (50%/3%)

**Luật ILA (coverage cao nhất):**

- `R2: NẾU [D:diff.size = 1] THÌ Cụm 1 [coverage 2/2, accuracy 1.00]`

**Bài đại diện** `ic_smallest_c868b30a4ade_000` vs bản đúng `ic_smallest_c868b30a4ade_003` (own_fix, sim 0.99) — `-` bản đúng, `+` bài sai:

```diff
-  for(i = 0; i < 4; i++)
+  for(i = 0; i < 3; i++)
+
```

### smallest / Cụm 2 — 7 bài, 4 SV

**Đặc trưng:** `A:condition.if_cmp=nonstrict` (71%/12%); `O:tests_negative.fail=some` (71%/17%); `O:output.wrong_input_elem=T` (100%/47%); `O:tests.fail_frac=low` (100%/58%); `D:diff.stmt_extra=T` (57%/16%); `D:diff.var_changed=T` (100%/61%)

**Luật ILA (coverage cao nhất):**

- `R3: NẾU [A:condition.if_cmp = nonstrict] VÀ [D:diff.size = 21+] THÌ Cụm 2 [coverage 5/7, accuracy 1.00]`
- `R4: NẾU [D:diff.cmp_if = F] VÀ [D:diff.stmt_extra = T] THÌ Cụm 2 [coverage 4/7, accuracy 1.00]`

**Bài đại diện** `ic_smallest_88394fc00b70_006` vs bản đúng `ic_smallest_769cd811312c_011` (nearest, sim 0.79) — `-` bản đúng, `+` bài sai:

```diff
-#include <stdio.h>
+# include <stdio.h>
-int main(){
-int a, b, c, d, x;
-printf("Please enter 4 numbers separated by spaces > ");
-scanf("%d %d %d %d", &a, &b, &c, &d);
-if (a>=b)
-x = b;
-else
-x = a;
-if (x>=c)
-x = c;
-if (x>=d)
-x = d;
… (29 dòng nữa)
```

### smallest / Cụm 3 — 7 bài, 5 SV

**Đặc trưng:** `D:diff.size=2-5` (57%/8%); `O:tests.fail_frac=low` (100%/58%); `D:diff.var_changed=T` (100%/61%); `O:output.off_by_one=T` (100%/64%); `O:output.wrong_input_elem=T` (71%/47%); `O:output.output_zero=T` (57%/33%)

**Luật ILA (coverage cao nhất):**

- `R5: NẾU [O:tests_zero.fail = none] VÀ [D:diff.cmp_if = F] THÌ Cụm 3 [coverage 4/7, accuracy 1.00]`
- `R6: NẾU [O:tests_negative.fail = none] VÀ [O:tests_sorted.fail = some] VÀ [D:diff.cmp_if = F] THÌ Cụm 3 [coverage 3/7, accuracy 1.00]`
- `R7: NẾU [O:tests_tie.fail = none] THÌ Cụm 3 [coverage 2/7, accuracy 1.00]`

**Bài đại diện** `ic_smallest_6aaeaf2ffb62_000` vs bản đúng `ic_smallest_6aaeaf2ffb62_002` (own_fix, sim 0.97) — `-` bản đúng, `+` bài sai:

```diff
-	printf("Please enter 4 numbers separated by spaces > ");
+	printf("Please enter 4 numbers separated by space > ");
-	if (tmp > int2)
+	if (int1 > int2)
-	if (tmp > int3)
+	else if (tmp > int3)
-	if (tmp > int4)
+	else if (tmp > int4)
```

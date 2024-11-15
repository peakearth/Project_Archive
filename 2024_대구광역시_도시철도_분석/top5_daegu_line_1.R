# 필요한 패키지 로드
library(tidyverse)

# 데이터 로드
data <- read.csv(text = "
년,분기,팔거,칠곡운암,북구청,서문시장,범물
2017,1,380018,368272,290562,604195,367625
2017,2,403603,395418,321670,766166,393855
2017,3,390955,376482,299061,735527,381813
2017,4,390748,374947,310646,730286,373617
2018,1,374893,352846,293605,637169,350804
2018,2,407284,388535,345675,742896,391138
2018,3,386581,367611,311815,710654,377006
2018,4,392939,377262,326725,723955,382725
2019,1,388211,364640,314641,678338,368233
2019,2,415279,400823,365107,698988,405592
2019,3,410155,384615,334608,663767,390268
2019,4,412453,389652,348687,648875,394512
2020,1,372956,340559,300919,519133,344737
2020,2,206607,209429,184992,344545,210671
2020,3,309386,300854,266158,502826,300642
2020,4,315747,310439,277080,496220,303932
2021,1,278875,268777,246523,414563,267203
2021,2,333348,322051,294922,514494,322661
2021,3,313942,301401,277174,465756,303407
2021,4,332615,321554,289100,498555,316585
2022,1,316902,297180,269760,428161,287658
2022,2,357091,335707,310198,511293,321478
2022,3,362984,333702,304277,537548,332495
2022,4,372324,346025,323358,535839,340155
2023,1,359699,329310,306022,502546,321994
2023,2,391514,360074,344981,588932,358258
2023,3,376219,330667,310909,546449,338276
2023,4,389400,340828,326648,561688,341155", header = TRUE, stringsAsFactors = FALSE)

# 데이터에서 합계 행 제거
data <- data[-nrow(data), ]

# 년과 분기를 결합하여 새로운 열 생성
data$년도_분기 <- paste(data$년, data$분기, sep = "_")

# 데이터를 long format으로 변환
data_long <- data %>%
  pivot_longer(cols = 팔거:범물, names_to = "역", values_to = "이용자수") %>%
  mutate(분기 = factor(분기, levels = c(1, 2, 3, 4), labels = c("Q1", "Q2", "Q3", "Q4")))

# ANOVA 분석 수행
anova_results <- aov(이용자수 ~ 분기 + 역, data = data_long)
summary(anova_results)

# =========================
# F - 분포
# =========================

# F-분포 시각화
library(ggplot2)

# F-값 및 자유도 추출
f_value <- summary(anova_result)[[1]][["F value"]][1]
df1 <- summary(anova_result)[[1]][["Df"]][1]
df2 <- summary(anova_result)[[1]][["Df"]][2]

# F-분포 시각화
x <- seq(0, 10, length = 100)
y <- df(x, df1, df2)

plot_df <- data.frame(x = x, y = y)

ggplot(plot_df, aes(x, y)) +
  geom_line(color = "blue") +
  geom_vline(xintercept = f_value, color = "red", linetype = "dashed") +
  labs(title = "F-distribution",
       x = "F-Value",
       y = "Density") +
  theme_minimal()

# =========================
# F - 검정
# =========================
# F-검정을 수행하는 함수 정의
perform_f_test <- function(data, quarter1, quarter2) {
  return(var.test(data[data$분기 == quarter1, "이용자수"], data[data$분기 == quarter2, "이용자수"]))
}

# 모든 분기 조합에 대해 F-검정 수행
quarters <- c("Q1", "Q2", "Q3", "Q4")
results <- list()

for (i in 1:(length(quarters) - 1)) {
  for (j in (i + 1):length(quarters)) {
    quarter1 <- quarters[i]
    quarter2 <- quarters[j]
    results[[paste(quarter1, "vs", quarter2)]] <- perform_f_test(data, quarter1, quarter2)
  }
}

# 결과 출력
results

# =========================
# t-검정
# =========================

# 각 역별로 t-검정 수행
t_test_results <- list()

for (역 in unique(data_long$역)) {
  data_sub <- subset(data_long, 역 == 역)
  t_test_results[[역]] <- list(
    Q1_vs_Q2 = t.test(data_sub[data_sub$분기 == "Q1", "이용자수"], data_sub[data_sub$분기 == "Q2", "이용자수"]),
    Q1_vs_Q3 = t.test(data_sub[data_sub$분기 == "Q1", "이용자수"], data_sub[data_sub$분기 == "Q3", "이용자수"]),
    Q1_vs_Q4 = t.test(data_sub[data_sub$분기 == "Q1", "이용자수"], data_sub[data_sub$분기 == "Q4", "이용자수"]),
    Q2_vs_Q3 = t.test(data_sub[data_sub$분기 == "Q2", "이용자수"], data_sub[data_sub$분기 == "Q3", "이용자수"]),
    Q2_vs_Q4 = t.test(data_sub[data_sub$분기 == "Q2", "이용자수"], data_sub[data_sub$분기 == "Q4", "이용자수"]),
    Q3_vs_Q4 = t.test(data_sub[data_sub$분기 == "Q3", "이용자수"], data_sub[data_sub$분기 == "Q4", "이용자수"])
  )
}

# ANOVA 결과 출력
print(summary(anova_results))

# 각 역별 t-검정 결과 출력
t_test_results

# T-test 중 그나마 가장 영향력이 높은 계절(분기) 출력하기
# 데이터 프레임 생성
data <- data.frame(
  분기 = rep(c("Q1", "Q2", "Q3", "Q4"), times = 5), # 예시 데이터로 분기 추가
  역 = rep(c("상인", "서부정류장", "중앙로", "대구역", "동대구역"), each = 4),
  이용자수 = c(1115484, 1069302, 1075571, 1090106,  # 상인 역의 이용자수
           1115484, 1069302, 1075571, 1090106,  # 서부정류장 역의 이용자수
           1115484, 1069302, 1075571, 1090106,  # 중앙로 역의 이용자수
           1115484, 1069302, 1075571, 1090106,  # 대구역의 이용자수
           1115484, 1069302, 1075571, 1090106)  # 동대구역의 이용자수
)

# 분기별 평균 이용자수 계산
avg_usage_by_quarter <- aggregate(이용자수 ~ 분기, data, mean)
print(avg_usage_by_quarter)

# 분기별 평균 이용자수 차이 계산
Q1_vs_Q2 <- abs(avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q1", "이용자수"] - avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q2", "이용자수"])
Q1_vs_Q3 <- abs(avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q1", "이용자수"] - avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q3", "이용자수"])
Q1_vs_Q4 <- abs(avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q1", "이용자수"] - avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q4", "이용자수"])
Q2_vs_Q3 <- abs(avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q2", "이용자수"] - avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q3", "이용자수"])
Q2_vs_Q4 <- abs(avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q2", "이용자수"] - avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q4", "이용자수"])
Q3_vs_Q4 <- abs(avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q3", "이용자수"] - avg_usage_by_quarter[avg_usage_by_quarter$분기 == "Q4", "이용자수"])

# 결과 출력
print(paste("Q1 vs Q2: ", Q1_vs_Q2))
print(paste("Q1 vs Q3: ", Q1_vs_Q3))
print(paste("Q1 vs Q4: ", Q1_vs_Q4))
print(paste("Q2 vs Q3: ", Q2_vs_Q3))
print(paste("Q2 vs Q4: ", Q2_vs_Q4))
print(paste("Q3 vs Q4: ", Q3_vs_Q4))

# 가장 큰 차이를 보이는 분기 확인
max_diff <- max(Q1_vs_Q2, Q1_vs_Q3, Q1_vs_Q4, Q2_vs_Q3, Q2_vs_Q4, Q3_vs_Q4)
if (max_diff == Q1_vs_Q2) {
  print("가장 큰 차이는 Q1 vs Q2")
} else if (max_diff == Q1_vs_Q3) {
  print("가장 큰 차이는 Q1 vs Q3")
} else if (max_diff == Q1_vs_Q4) {
  print("가장 큰 차이는 Q1 vs Q4")
} else if (max_diff == Q2_vs_Q3) {
  print("가장 큰 차이는 Q2 vs Q3")
} else if (max_diff == Q2_vs_Q4) {
  print("가장 큰 차이는 Q2 vs Q4")
} else if (max_diff == Q3_vs_Q4) {
  print("가장 큰 차이는 Q3 vs Q4")
}


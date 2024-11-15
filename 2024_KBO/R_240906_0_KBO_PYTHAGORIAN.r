# 필요한 패키지 로드
library(dplyr)
library(readr)

# CSV 파일 경로 설정
cat('\n피타고리안 승률기반 기대승리 산출을 시행합니다.\n')
cat('팀명의 입력은 영어로만 지원됩니다. (KIA, SAMSUNG, LG, DOOSAN, KT, SSG, HANHWA, LOTTE, NC, KIWOOM)\n')
team_name <- readline(prompt = '계산하고자 하는 팀명을 입력해 주세요 : ')

file_path <- '/Users/song/Desktop/03_개인 Projects/개인적 프로젝트/2024 KBO 팀별분석'
csv_file_path <- paste0(file_path, '/', team_name, '.csv')

# 기대확률 계산
played_game <- as.integer(readline(prompt = '지금까지 시행 한 게임 수를 입력하세요 : '))
janyeo_game <- 144 - played_game
cat(' \n')

# 팀명 한글 처리
team_name_kor <- switch(tolower(team_name),
                        'kia' = '기아 타이거즈',
                        'samsung' = '삼성 라이온즈',
                        'lg' = 'LG 트윈즈',
                        'doosan' = '두산 베어스',
                        'kt' = 'KT 위즈',
                        'ssg' = 'SSG 랜더스',
                        'hanhwa' = '한화 이글즈',
                        'lotte' = '롯데 자이언츠',
                        'nc' = 'NC 다이노스',
                        'kiwoom' = '키움 히어로즈')

# CSV 파일에서 데이터 읽기
tryCatch({
  data <- read_csv(csv_file_path)
  
  # 팀별 경기 데이터 가져오기
  vs_team_data <- data %>%
    group_by(VS_TEAM) %>%
    summarise(WIN = sum(WIN, na.rm = TRUE),
              L = sum(L, na.rm = TRUE)) %>%
    mutate(TOTAL_GAMES = WIN + L,
           WIN_RATE = WIN / TOTAL_GAMES)
  
  # 홈/원정 경기 데이터 가져오기
  home_away_data <- data %>%
    group_by(HOME_AWAY) %>%
    summarise(WIN = sum(WIN, na.rm = TRUE),
              L = sum(L, na.rm = TRUE)) %>%
    mutate(TOTAL_GAMES = WIN + L,
           WIN_RATE = WIN / TOTAL_GAMES)
  
  # 기초 게임 정보
  checksum_w <- sum(data$W, na.rm = TRUE)
  checksum_l <- sum(data$L, na.rm = TRUE)
  checksum_win <- sum(data$WIN, na.rm = TRUE)
  checksum_draw <- sum(data$DRAW, na.rm = TRUE)
  
  cat(sprintf('1. %s의 잔여 경기는 %d 경기입니다.\n', team_name_kor, janyeo_game))
  cat(sprintf('2. %s의 승리 경기수는 %d 게임입니다.\n', team_name_kor, checksum_win))
  cat(sprintf('3. %s의 총 득점은 %d점, 총 실점은 %d점입니다.\n', team_name_kor, checksum_w, checksum_l))
  
  # 피타고리안 승률 계산
  pythagorean_exp <- (checksum_w^1.83) / ((checksum_w^1.83) + (checksum_l^1.83))
  
  cat('\n피타고리안 승률에 대한 계산을 실시합니다.\n')
  cat(sprintf('4. %s의 피타고리안 승률은 %.4f 입니다.\n', team_name_kor, pythagorean_exp))
  
  exp_win <- janyeo_game * pythagorean_exp
  exp_draw_rate <- checksum_draw / played_game
  exp_draw <- janyeo_game * exp_draw_rate
  exp_loss <- janyeo_game - exp_win - exp_draw
  
  cat(sprintf('5. 잔여게임에 대한 기대승리 게임은 %.4f 경기입니다.\n', exp_win))
  cat(sprintf('6. 잔여게임에 대한 기대무승부 게임은 %.4f 경기입니다.\n', exp_draw))
  cat(sprintf('7. 잔여게임에 대한 기대패배 게임은 %.4f 경기입니다.\n', exp_loss))
  
  cat('\n상대팀별 승률:\n')
  print(vs_team_data)
  
  cat('\n홈/원정 경기 승률:\n')
  print(home_away_data)
  
}, error = function(e) {
  cat('오류가 발생했습니다: ', conditionMessage(e), '\n')
})
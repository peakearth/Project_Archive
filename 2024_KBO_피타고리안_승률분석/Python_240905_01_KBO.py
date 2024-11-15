import pandas as pd

# CSV 파일 경로 설정
print()
print('피타고리안 승률기반 기대승리 산출을 시행합니다.')
print('팀명의 입력은 영어로만 지원됩니다. (KIA, SAMSUNG, LG, DOOSAN, KT, SSG, HANHWA, LOTTE, NC, KIWOOM)')
team_name = input('계산하고자 하는 팀명을 입력해 주세요 : ')

file_path = '/Users/song/Desktop/03_개인 Projects/개인적 프로젝트/2024 KBO 팀별분석'
csv_file_path = f'{file_path}/{team_name}.csv'

# 기대확률 계산
played_game = int(input('지금까지 시행 한 게임 수를 입력하세요 : '))
janyeo_game = 144 - played_game
print(' ')

# 팀명 한글 처리
if team_name.lower() in ['kia' , '기아']:
    team_name_kor = '기아 타이거즈'
elif team_name.lower() in ['samsung' , '삼성']:
    team_name_kor = '삼성 라이온즈'
elif team_name.lower() == 'lg':
    team_name_kor = 'LG 트윈즈'
elif team_name.lower() in ['doosan' , '두산']:
    team_name_kor = '두산 베어스'
elif team_name.lower() == 'kt':
    team_name_kor = 'KT 위즈'
elif team_name.lower() == 'ssg':
    team_name_kor = 'SSG 랜더스'
elif team_name.lower() in ['hanhwa' , '한화']:
    team_name_kor = '한화 이글즈'
elif team_name.lower() == 'lotte':
    team_name_kor = '롯데 자이언츠'
elif team_name.lower() == 'nc':
    team_name_kor = 'NC 다이노스'
elif team_name.lower() == 'kiwoom':
    team_name_kor = '키움 히어로즈'

# CSV 파일에서 데이터 읽기
try:
    data = pd.read_csv(csv_file_path)

    # 팀별 경기 데이터 가져오기
    vs_team_data = data.groupby('VS_TEAM').agg({'WIN': 'sum' , 'L': 'sum'}).reset_index()
    print(vs_team_data)

    # 팀별 승률 계산
    vs_team_data['TOTAL_GAMES'] = vs_team_data['WIN'] + vs_team_data['L']
    vs_team_data['WIN_RATE'] = vs_team_data['WIN'] / vs_team_data['TOTAL_GAMES']

    # 홈/원정 경기 데이터 가져오기
    home_away_data = data.groupby('HOME_AWAY').agg({'WIN': 'sum' , 'L': 'sum'}).reset_index()

    # 홈/원정 경기 승률 계산
    home_away_data['TOTAL_GAMES'] = home_away_data['WIN'] + home_away_data['L']
    home_away_data['WIN_RATE'] = home_away_data['WIN'] / home_away_data['TOTAL_GAMES']

    # 기초게임 정보
    list_w = data['W'].tolist()
    list_l = data['L'].tolist()
    list_win = data['WIN'].tolist()
    list_draw = data['DRAW'].tolist()

    checksum_w = sum(list_w)
    checksum_l = sum(list_l)
    checksum_win = sum(list_win)
    checksum_draw = sum(list_draw)

    print(f'1. {team_name_kor}의 잔여 경기는 {janyeo_game} 경기입니다.')
    print(f'2. {team_name_kor}의 승리 경기수는 {checksum_win} 게임입니다.')
    print(f'3. {team_name_kor}의 총 득점은 {checksum_w}점, 총 실점은 {checksum_l}점입니다.')

    # 피타고리안 승률 계산
    pythagorean_exp = (checksum_w ** 1.83) / ((checksum_w ** 1.83) + (checksum_l ** 1.83))

    print()
    print('피타고리안 승률에 대한 계산을 실시합니다.')
    print(f'4. {team_name_kor}의 피타고리안 승률은 {pythagorean_exp:.4f} 입니다.')

    exp_win = janyeo_game * pythagorean_exp
    exp_draw_rate = checksum_draw / played_game
    exp_draw = janyeo_game * exp_draw_rate
    exp_loss = janyeo_game - exp_win - exp_draw

    print(f'5. 잔여게임에 대한 기대승리 게임은 {exp_win:.4f} 경기입니다.')
    print(f'6. 잔여게임에 대한 기대무승부 게임은 {exp_draw:.4f} 경기입니다.')
    print(f'7. 잔여게임에 대한 기대패배 게임은 {exp_loss:.4f} 경기입니다.')

    print('\n상대팀별 승률:')
    print(vs_team_data[['VS_TEAM' , 'WIN_RATE']])

    print('\n홈/원정 경기 승률:')
    print(home_away_data[['HOME_AWAY' , 'WIN_RATE']])

except FileNotFoundError:
    print('CSV 파일을 찾을 수 없습니다. 경로를 확인해주세요.')
except pd.errors.EmptyDataError:
    print('CSV 파일이 비어 있습니다.')
except KeyError as e:
    print(f'CSV 파일에 필요한 열이 없습니다: {e}')
except Exception as e:
    print(f'오류가 발생했습니다: {e}')
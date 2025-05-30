import pandas as pd

# CSV 파일 경로 설정
# 안내문
print('피타고리안 승률기반 기대승리 산출을 시행합니다.')
print('팀명의 입력은 영어로만 지원됩니다. (KIA, SAMSUNG, LG, DOOSAN, KT, SSG, HANHWA, LOTTE, NC, KIWOOM)')
team_name = input('계산하고자 하는 팀명을 영어로 입력해 주세요 : ')
# team_name_kor = team_name
file_path = '/Users/song/Desktop/03_개인 Projects/개인적 프로젝트/2024 KBO 팀별분석'
csv_file_path = f'{file_path}/{team_name}.csv'
# print(csv_file_path)

# 기대확률 계산
played_game = int(input('지금까지 시행 한 게임 수를 입력하세요 : '))
janyeo_game = 144 - played_game
print()

# win_input = int(input('지금까지의 승  리 게임 수를 입력하세요 >> '))
# lose_input = int(input('지금까지의 패  배 게임 수를 입력하세요 >> '))
# draw_input = int(input('지금까지의 무승부 게임 수를 입력하세요 >> '))
# print('=' * 40)
# print('=' * 40)
if team_name == 'kia' or team_name == 'KIA':
    team_name_kor = '기아 타이거즈'
    
elif team_name == 'samsung' or team_name == 'SAMSUNG':
    team_name_kor = '삼성 라이온즈'
    
elif team_name == 'lg' or team_name == 'LG':
    team_name_kor = 'LG 트윈즈'
    
elif team_name == 'doosan' or team_name == 'DOOSAN':
    team_name_kor = '두산 베어스'
    
elif team_name == 'KT' or team_name == 'kt':
    team_name_kor = 'KT 위즈'
    
elif team_name == 'SSG' or team_name == 'ssg':
    team_name_kor = 'SSG 렌더스'
    
elif team_name == 'HANHWA' or team_name == 'hanhwa':
    team_name_kor = '한화 이글즈'
    
elif team_name == 'LOTTE' or team_name == 'lotte':
    team_name_kor = '롯데 자이언츠'
    
elif team_name == 'NC' or team_name == 'nc':
    team_name_kor = 'NC 다이노스'
    
elif team_name == 'KIWOOM' or team_name == 'kiwoom':
    team_name_kor = '키움 히어로스'

# CSV 파일에서 득점과 실점 데이터를 불러오기
try:
    data = pd.read_csv(csv_file_path)
    list_w = data['W'].tolist()
    list_l = data['L'].tolist()
    list_win = data['WIN'].tolist()

    # 총 득점과 총 실점 계산
    checksum_w = sum(list_w)
    checksum_l = sum(list_l)
    checksum_win = sum(list_win)

    # 결과 출력 - 기초게임 정보
    print(f'1. {team_name_kor}의 잔여 경기는 {janyeo_game} 경기입니다.')
    print()
    print(f'2. {team_name_kor}의 승리 경기수는 {checksum_win} 게임입니다.')
    print()
    print(f'3. {team_name_kor}의 총 득점은 {checksum_w}점, 총 실점은 {checksum_l}점입니다.')
    print('----------------------------------------------------------------------------')
    
    # 피타고리안 승률 계산
    pythagorean_exp = (checksum_w ** 1.83) / ((checksum_w ** 1.83) + (checksum_l ** 1.83))
    print(f'4. {team_name_kor}의 피타고리안 승률은 {pythagorean_exp:.4f} 입니다.')
    print()
    # 잔여 기대승 확인
    print(f'5. 잔여게임에 대한 기대승리 게임은 {checksum_win + (janyeo_game * pythagorean_exp):.4f} 입니다.')
    print()  

except FileNotFoundError:
    print('CSV 파일을 찾을 수 없습니다. 경로를 확인해주세요.')
except pd.errors.EmptyDataError:
    print('CSV 파일이 비어 있습니다.')
except KeyError:
    print('CSV 파일에 필요한 열이 없습니다. 득점항목의 열은 "W"로, 실점항목의 열은 "L" 열로 작성되어 있는지 확인하세요.')
except Exception as e:
    print(f'오류가 발생했습니다: {e}')
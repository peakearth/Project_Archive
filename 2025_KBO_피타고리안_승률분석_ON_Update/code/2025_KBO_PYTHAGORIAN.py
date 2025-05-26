import pandas as pd

# CSV 파일 경로 설정
print('----------------------------------------------------------')
print('피타고리안 승률기반 기대승리 산출을 시행합니다.')

print('팀 이름을 입력받습니다.')
print('팀명은 아래 리스트 중 하나로 입력해 주세요.')
print('KIA, SAMSUNG, LG, DOOSAN, KT, SSG, HANHWA, LOTTE, NC, KIWOOM')
print('----------------------------------------------------------')

team_name = input('계산하고자 하는 팀명을 입력해 주세요 : ')


file_path = ''

if team_name.lower() in ['kia', '기아']:
    team_name_kor = '기아 타이거즈'
elif team_name.lower() in ['samsung', '삼성']:
    team_name_kor = '삼성 라이온즈'
elif team_name.lower() == ['lg', '엘지']:
    team_name_kor = 'LG 트윈즈'
elif team_name.lower() in ['doosan', '두산']:
    team_name_kor = '두산 베어스'
elif team_name.lower() == ['kt', '케이티']:
    team_name_kor = 'KT 위즈'
elif team_name.lower() in ['ssg', '에스에스지']:
    team_name_kor = 'SSG 랜더스'
elif team_name.lower() in ['hanhwa', '한화']:
    team_name_kor = '한화 이글즈'
elif team_name.lower() == ['lotte', '롯데']:
    team_name_kor = '롯데 자이언츠'
elif team_name.lower() == ['nc', '엔씨']:
    team_name_kor = 'NC 다이노스'
elif team_name.lower() == ['kiwoom', '키움']:
    team_name_kor = '키움 히어로즈'
else:
    print('입력한 팀명이 잘못되었습니다. 다시 입력해 주세요.')

file_path = 'Project_Archive/2025_KBO_피타고리안_승률분석_ON_Update/Data'
csv_path = f'{file_path}/{team_name}.csv'

try:
    data = pd.read_csv(csv_path)
    
    # 팀별 경기 데이터 가져오기
    vs_team_data = data.groupby('VS_TEAM').agg({'WIN': 'sum', 'L': 'sum'}).reset_index()
    print(vs_team_data)
    
    # 팀별 승률 계산
    vs_team_data['TOTAL_GAMES'] = vs_team_data['WIN'] + vs_team_data['L']
    vs_team_data['WIN_RATE'] = vs_team_data['WIN'] / vs_team_data['TOTAL_GAMES']
    
    # 홈/원정 경기 데이터 가져오기
    home_away_data = data.groupby('HOME_AWAY').agg({'WIN': 'sum', 'L': 'sum'}).reset_index()
    
    # 홈/원정 경기 승률 계산
    home_away_data['TOTAL_GAMES'] = home_away_data['WIN'] + home_away_data['L']
    home_away_data['WIN_RATE'] = home_away_data['WIN'] / home_away_data['TOTAL_GAMES']
    
    # 기초게임 정보
    list_w = data['W'].tolist()
    list_l = data['L'].tolist()
    list_win = sum(list_w)
    list_lose = sum(list_l)
    
    list_total = list_win + list_lose

# 에러 정의
except FileNotFoundError:
    print(f'파일을 찾을 수 없습니다. 경로를 확인해 주세요: {csv_path}')
    exit() 
except pd.errors.EmptyDataError:
    print('CSV 파일이 비어 있습니다. 데이터를 확인해 주세요.')
    exit()
except pd.errors.ParserError:
    print('CSV 파일을 읽는 중 오류가 발생했습니다. 파일 형식을 확인해 주세요.')
    exit()
except Exception as e:
    print(f'알 수 없는 오류가 발생했습니다: {e}')
    exit()
except KeyError as e:
    print(f'CSV 파일에 필요한 열이 없습니다: {e}')
    exit()
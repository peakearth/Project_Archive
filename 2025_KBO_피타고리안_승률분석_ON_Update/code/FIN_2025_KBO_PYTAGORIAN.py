import pandas as pd
import os

class PythagoreanAnalyzer:
    def __init__(self):
        self.team_mapping = {
            'kia': ('기아 타이거즈', 'KIA'),
            '기아': ('기아 타이거즈', 'KIA'),
            'samsung': ('삼성 라이온즈', 'SAMSUNG'),
            '삼성': ('삼성 라이온즈', 'SAMSUNG'),
            'lg': ('LG 트윈즈', 'LG'),
            '엘지': ('LG 트윈즈', 'LG'),
            'doosan': ('두산 베어스', 'DOOSAN'),
            '두산': ('두산 베어스', 'DOOSAN'),
            'kt': ('KT 위즈', 'KT'),
            '케이티': ('KT 위즈', 'KT'),
            'ssg': ('SSG 랜더스', 'SSG'),
            '에스에스지': ('SSG 랜더스', 'SSG'),
            'hanhwa': ('한화 이글즈', 'HANHWA'),
            '한화': ('한화 이글즈', 'HANHWA'),
            'lotte': ('롯데 자이언츠', 'LOTTE'),
            '롯데': ('롯데 자이언츠', 'LOTTE'),
            'nc': ('NC 다이노스', 'NC'),
            '엔씨': ('NC 다이노스', 'NC'),
            'kiwoom': ('키움 히어로즈', 'KIWOOM'),
            '키움': ('키움 히어로즈', 'KIWOOM')
        }
        
        self.file_path = 'Project_Archive/2025_KBO_피타고리안_승률분석_ON_Update/Data'
        self.excel_path = os.path.join(self.file_path, 'KBO_2025_Data.xlsx')
        
    def calculate_pythagorean_stats(self, data, team_name_kor):
        """피타고리안 승률 통계 계산"""
        try:
            # 득점과 실점 데이터 가져오기 (컬럼명은 실제 엑셀 파일에 맞게 조정 필요)
            runs_scored = data['득점'].sum() if '득점' in data.columns else data.get('RS', data.get('R', 0)).sum()
            runs_allowed = data['실점'].sum() if '실점' in data.columns else data.get('RA', 0).sum()
            
            # 실제 승수와 패수
            actual_wins = data['W'].sum()
            actual_losses = data['L'].sum()
            total_games = actual_wins + actual_losses
            
            # 피타고리안 승률 계산 (지수 2 사용)
            if runs_allowed > 0:
                pythagorean_win_pct = (runs_scored ** 2) / (runs_scored ** 2 + runs_allowed ** 2)
                expected_wins = pythagorean_win_pct * total_games
                expected_losses = total_games - expected_wins
                win_difference = actual_wins - expected_wins
            else:
                pythagorean_win_pct = 1.0
                expected_wins = total_games
                expected_losses = 0
                win_difference = 0
            
            actual_win_pct = actual_wins / total_games if total_games > 0 else 0
            
            return {
                '팀명': team_name_kor,
                '경기수': total_games,
                '실제승수': actual_wins,
                '실제패수': actual_losses,
                '실제승률': round(actual_win_pct, 3),
                '득점': runs_scored,
                '실점': runs_allowed,
                '득실차': runs_scored - runs_allowed,
                '피타고리안승률': round(pythagorean_win_pct, 3),
                '예상승수': round(expected_wins, 1),
                '예상패수': round(expected_losses, 1),
                '승차': round(win_difference, 1)
            }
        except Exception as e:
            print(f"{team_name_kor} 데이터 처리 중 오류: {e}")
            return None
    
    def analyze_vs_teams(self, data):
        """상대팀별 분석"""
        try:
            vs_team_data = data.groupby('VS_TEAM').agg({
                'W': 'sum', 
                'L': 'sum'
            }).reset_index()
            
            vs_team_data['총경기'] = vs_team_data['W'] + vs_team_data['L']
            vs_team_data['승률'] = round(vs_team_data['W'] / vs_team_data['총경기'], 3)
            
            return vs_team_data.sort_values('승률', ascending=False)
        except Exception as e:
            print(f"상대팀별 분석 중 오류: {e}")
            return None
    
    def analyze_home_away(self, data):
        """홈/원정 분석"""
        try:
            home_away_data = data.groupby('HOME_AWAY').agg({
                'W': 'sum', 
                'L': 'sum'
            }).reset_index()
            
            home_away_data['총경기'] = home_away_data['W'] + home_away_data['L']
            home_away_data['승률'] = round(home_away_data['W'] / home_away_data['총경기'], 3)
            
            return home_away_data
        except Exception as e:
            print(f"홈/원정 분석 중 오류: {e}")
            return None
    
    def analyze_single_team(self, team_input):
        """단일 팀 분석"""
        team_info = self.team_mapping.get(team_input.lower())
        if not team_info:
            print('입력한 팀명이 잘못되었습니다. 다시 입력해 주세요.')
            return
        
        team_name_kor, sheet_name = team_info
        
        try:
            data = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            print(f'\n{"="*60}')
            print(f'{team_name_kor} 피타고리안 승률 분석 결과')
            print(f'{"="*60}')
            
            # 피타고리안 통계 계산
            stats = self.calculate_pythagorean_stats(data, team_name_kor)
            if stats:
                print('\n[기본 통계]')
                for key, value in stats.items():
                    if key != '팀명':
                        print(f'{key}: {value}')
            
            # 상대팀별 분석
            vs_team_analysis = self.analyze_vs_teams(data)
            if vs_team_analysis is not None:
                print('\n[상대팀별 성적]')
                print(vs_team_analysis.to_string(index=False))
            
            # 홈/원정 분석
            home_away_analysis = self.analyze_home_away(data)
            if home_away_analysis is not None:
                print('\n[홈/원정 성적]')
                print(home_away_analysis.to_string(index=False))
                
        except ValueError as e:
            if 'Worksheet' in str(e):
                print(f'시트를 찾을 수 없습니다: {sheet_name}')
                self._show_available_sheets()
            else:
                print(f'값 오류: {e}')
        except Exception as e:
            print(f'분석 중 오류가 발생했습니다: {e}')
    
    def analyze_all_teams(self):
        """전체 팀 분석"""
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            all_stats = []
            
            print(f'\n{"="*80}')
            print('전체 팀 피타고리안 승률 분석 결과')
            print(f'{"="*80}')
            
            # 각 시트(팀)별로 데이터 분석
            for sheet_name in excel_file.sheet_names:
                # 시트명으로부터 팀 정보 찾기
                team_name_kor = None
                for korean_name, (kor_name, eng_name) in self.team_mapping.items():
                    if eng_name == sheet_name:
                        team_name_kor = kor_name
                        break
                
                if not team_name_kor:
                    continue
                
                try:
                    data = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                    stats = self.calculate_pythagorean_stats(data, team_name_kor)
                    if stats:
                        all_stats.append(stats)
                except Exception as e:
                    print(f'{sheet_name} 시트 처리 중 오류: {e}')
                    continue
            
            if all_stats:
                # DataFrame으로 변환하여 정렬
                df_stats = pd.DataFrame(all_stats)
                df_stats = df_stats.sort_values('피타고리안승률', ascending=False)
                
                print('\n[전체 팀 피타고리안 승률 순위]')
                print(df_stats.to_string(index=False))
                
                # 상위/하위 팀 분석
                print(f'\n[분석 요약]')
                best_team = df_stats.iloc[0]
                worst_team = df_stats.iloc[-1]
                
                print(f'• 피타고리안 승률 1위: {best_team["팀명"]} ({best_team["피타고리안승률"]})')
                print(f'• 피타고리안 승률 최하위: {worst_team["팀명"]} ({worst_team["피타고리안승률"]})')
                
                # 실제 승률과 피타고리안 승률 차이가 큰 팀
                df_stats['승률차이'] = df_stats['실제승률'] - df_stats['피타고리안승률']
                overperformer = df_stats.loc[df_stats['승률차이'].idxmax()]
                underperformer = df_stats.loc[df_stats['승률차이'].idxmin()]
                
                print(f'• 예상보다 잘하는 팀: {overperformer["팀명"]} (차이: +{overperformer["승률차이"]:.3f})')
                print(f'• 예상보다 못하는 팀: {underperformer["팀명"]} (차이: {underperformer["승률차이"]:.3f})')
                
        except Exception as e:
            print(f'전체 팀 분석 중 오류가 발생했습니다: {e}')
    
    def _show_available_sheets(self):
        """사용 가능한 시트 목록 출력"""
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            print(f'사용 가능한 시트: {excel_file.sheet_names}')
        except:
            pass
    
    def run_analysis(self):
        """메인 분석 실행"""
        if not os.path.exists(self.excel_path):
            print(f'파일을 찾을 수 없습니다: {self.excel_path}')
            return
        
        print('----------------------------------------------------------')
        print('피타고리안 승률기반 기대승리 산출을 시행합니다.')
        print('팀 이름을 입력받습니다.')
        print('팀명은 아래 리스트 중 하나로 입력해 주세요.')
        print('KIA, SAMSUNG, LG, DOOSAN, KT, SSG, HANHWA, LOTTE, NC, KIWOOM')
        print('전체 팀 분석을 원하시면 "전체" 또는 "total"을 입력해 주세요.')
        print('----------------------------------------------------------')
        
        team_input = input('계산하고자 하는 팀명을 입력해 주세요 : ').strip()
        
        if team_input.lower() in ['전체', 'total', 'all']:
            self.analyze_all_teams()
        else:
            self.analyze_single_team(team_input)

# 실행
if __name__ == "__main__":
    analyzer = PythagoreanAnalyzer()
    analyzer.run_analysis()
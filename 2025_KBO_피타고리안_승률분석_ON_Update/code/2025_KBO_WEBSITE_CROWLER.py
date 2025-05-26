import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class KBODataScraper:
    def __init__(self):
        self.base_url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
        self.team_mapping = {
            '기아': ('KIA', '기아 타이거즈'),
            'KIA': ('KIA', '기아 타이거즈'),
            '삼성': ('SAMSUNG', '삼성 라이온즈'),
            'LG': ('LG', 'LG 트윈즈'),
            '두산': ('DOOSAN', '두산 베어스'),
            'KT': ('KT', 'KT 위즈'),
            'SSG': ('SSG', 'SSG 랜더스'),
            '한화': ('HANHWA', '한화 이글즈'),
            '롯데': ('LOTTE', '롯데 자이언츠'),
            'NC': ('NC', 'NC 다이노스'),
            '키움': ('KIWOOM', '키움 히어로즈')
        }
        
        self.file_path = 'Project_Archive/2025_KBO_피타고리안_승률분석_ON_Update/Data'
        self.excel_path = os.path.join(self.file_path, 'KBO_2025_Data.xlsx')
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kbo_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 디렉토리 생성
        os.makedirs(self.file_path, exist_ok=True)
    
    def setup_driver(self):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        # 더 안정적인 Chrome 옵션 설정
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # webdriver-manager를 사용하는 경우
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 페이지 로드 타임아웃 설정
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            return driver
            
        except ImportError:
            self.logger.warning("webdriver-manager가 설치되지 않음. 기본 ChromeDriver 사용")
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)
                return driver
            except Exception as e:
                self.logger.error(f"기본 ChromeDriver 설정 실패: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"WebDriver 설정 실패: {e}")
            # requests 방법으로 대체 시도
            self.logger.info("Selenium 실패로 requests 방법으로 대체 시도")
            return None
    
    def get_game_data_selenium(self, year=2025, month=None):
        """Selenium을 사용한 게임 데이터 수집"""
        driver = self.setup_driver()
        if not driver:
            self.logger.warning("Selenium 드라이버 설정 실패. requests 방법으로 대체")
            return self.get_game_data_requests(year)
        
        all_games = []
        
        try:
            # 현재 월부터 12월까지 또는 지정된 월만
            start_month = month if month else 3  # 시즌은 보통 3월부터
            end_month = month + 1 if month else datetime.now().month + 1
            
            for current_month in range(start_month, end_month):
                self.logger.info(f"Selenium으로 {year}년 {current_month}월 데이터 수집 중...")
                
                try:
                    # 해당 월의 일정 페이지로 이동
                    url = f"{self.base_url}?year={year}&month={current_month:02d}"
                    self.logger.info(f"URL 접근: {url}")
                    
                    driver.get(url)
                    
                    # 페이지 로딩 대기 (더 안정적인 대기)
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CLASS_NAME, "tblType01")),
                                EC.presence_of_element_located((By.TAG_NAME, "table"))
                            )
                        )
                    except Exception as wait_error:
                        self.logger.warning(f"페이지 로딩 대기 실패: {wait_error}")
                        time.sleep(5)  # 추가 대기
                    
                    # 경기 테이블 찾기 (여러 방법 시도)
                    tables = driver.find_elements(By.CLASS_NAME, "tblType01")
                    if not tables:
                        tables = driver.find_elements(By.TAG_NAME, "table")
                    
                    self.logger.info(f"찾은 테이블 수: {len(tables)}")
                    
                    for table_idx, table in enumerate(tables):
                        try:
                            rows = table.find_elements(By.TAG_NAME, "tr")
                            self.logger.info(f"테이블 {table_idx + 1}에서 {len(rows)}개 행 발견")
                            
                            for row_idx, row in enumerate(rows[1:], 1):  # 헤더 제외
                                try:
                                    cells = row.find_elements(By.TAG_NAME, "td")
                                    if len(cells) >= 5:
                                        date = cells[0].text.strip()
                                        vs_info = cells[2].text.strip()
                                        result = cells[4].text.strip()
                                        stadium = cells[3].text.strip() if len(cells) > 3 else ''
                                        
                                        # 경기 결과가 있는 경우만 처리
                                        if result and ':' in result and result != '-':
                                            game_data = self.parse_game_info(date, vs_info, result, stadium)
                                            if game_data:
                                                all_games.extend(game_data)
                                                self.logger.info(f"경기 데이터 추가: {date} {vs_info} {result}")
                                
                                except Exception as row_error:
                                    self.logger.warning(f"행 {row_idx} 처리 중 오류: {row_error}")
                                    continue
                        
                        except Exception as table_error:
                            self.logger.warning(f"테이블 {table_idx + 1} 처리 중 오류: {table_error}")
                            continue
                
                except Exception as month_error:
                    self.logger.error(f"{current_month}월 데이터 수집 실패: {month_error}")
                    continue
                
                time.sleep(3)  # 서버 부하 방지
        
        except Exception as e:
            self.logger.error(f"Selenium 데이터 수집 중 전체 오류: {e}")
        
        finally:
            try:
                driver.quit()
            except:
                pass
        
        if not all_games:
            self.logger.warning("Selenium으로 데이터를 수집하지 못함. requests 방법 시도")
            return self.get_game_data_requests(year)
        
        return all_games
    
    def parse_game_info(self, date, vs_info, result, stadium):
        """경기 정보 파싱"""
        try:
            # 팀 정보 추출
            vs_parts = vs_info.split('vs')
            if len(vs_parts) != 2:
                return None
            
            away_team = vs_parts[0].strip()
            home_team = vs_parts[1].strip()
            
            # 결과 파싱 (예: "5:3")
            if ':' not in result:
                return None
            
            score_parts = result.split(':')
            away_score = int(score_parts[0])
            home_score = int(score_parts[1])
            
            # 승부 결정
            away_win = 1 if away_score > home_score else 0
            home_win = 1 if home_score > away_score else 0
            
            games = []
            
            # 원정팀 데이터
            away_data = {
                'DATE': date,
                'HOME_AWAY': 'AWAY',
                'VS_TEAM': home_team,
                'STADIUM': stadium,
                'W': away_win,
                'L': 1 - away_win,
                '득점': away_score,
                '실점': home_score
            }
            
            # 홈팀 데이터  
            home_data = {
                'DATE': date,
                'HOME_AWAY': 'HOME',
                'VS_TEAM': away_team,
                'STADIUM': stadium,
                'W': home_win,
                'L': 1 - home_win,
                '득점': home_score,
                '실점': away_score
            }
            
            return [
                (away_team, away_data),
                (home_team, home_data)
            ]
            
        except Exception as e:
            self.logger.warning(f"경기 정보 파싱 오류: {e}")
            return None
    
    def get_game_data_requests(self, year=2025):
        """requests를 사용한 대안 방법"""
        self.logger.info("requests를 사용하여 데이터 수집 시도")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        all_games = []
        current_month = datetime.now().month
        
        try:
            for month in range(3, current_month + 1):  # 3월부터 현재 월까지
                self.logger.info(f"requests로 {year}년 {month}월 데이터 수집 중...")
                
                url = f"https://www.koreabaseball.com/Schedule/Schedule.aspx?year={year}&month={month:02d}"
                
                session = requests.Session()
                response = session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 경기 일정 테이블 찾기
                tables = soup.find_all('table', class_='tblType01')
                
                for table in tables:
                    rows = table.find_all('tr')[1:]  # 헤더 제외
                    
                    for row in rows:
                        try:
                            cells = row.find_all('td')
                            if len(cells) >= 5:
                                date = cells[0].get_text(strip=True)
                                vs_info = cells[2].get_text(strip=True)
                                result = cells[4].get_text(strip=True)
                                stadium = cells[3].get_text(strip=True) if len(cells) > 3 else ''
                                
                                # 경기 결과가 있는 경우만 처리
                                if result and ':' in result and result != '-':
                                    game_data = self.parse_game_info(date, vs_info, result, stadium)
                                    if game_data:
                                        all_games.extend(game_data)
                        
                        except Exception as e:
                            self.logger.warning(f"행 처리 중 오류: {e}")
                            continue
                
                time.sleep(1)  # 서버 부하 방지
                
        except Exception as e:
            self.logger.error(f"requests 데이터 수집 중 오류: {e}")
            return []
        
        return all_games
    
    def update_excel_file(self, games_data):
        """엑셀 파일 업데이트"""
        try:
            # 팀별 데이터 분류
            team_data = {}
            for team, game_data in games_data:
                if team not in team_data:
                    team_data[team] = []
                team_data[team].append(game_data)
            
            # 기존 엑셀 파일이 있으면 읽기
            existing_data = {}
            if os.path.exists(self.excel_path):
                try:
                    excel_file = pd.ExcelFile(self.excel_path)
                    for sheet_name in excel_file.sheet_names:
                        existing_data[sheet_name] = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                except Exception as e:
                    self.logger.warning(f"기존 엑셀 파일 읽기 오류: {e}")
            
            # ExcelWriter로 여러 시트에 데이터 저장
            with pd.ExcelWriter(self.excel_path, engine='openpyxl', mode='w') as writer:
                for team, games in team_data.items():
                    # 팀명을 시트명으로 변환
                    sheet_name = None
                    for key, (eng_name, kor_name) in self.team_mapping.items():
                        if key == team or kor_name == team:
                            sheet_name = eng_name
                            break
                    
                    if not sheet_name:
                        continue
                    
                    # DataFrame 생성
                    df = pd.DataFrame(games)
                    
                    # 기존 데이터와 병합 (중복 제거)
                    if sheet_name in existing_data:
                        existing_df = existing_data[sheet_name]
                        # 날짜와 상대팀 기준으로 중복 제거
                        combined_df = pd.concat([existing_df, df]).drop_duplicates(
                            subset=['DATE', 'VS_TEAM', 'HOME_AWAY'], keep='last'
                        )
                        df = combined_df.sort_values('DATE')
                    
                    # 엑셀에 저장
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    self.logger.info(f"{sheet_name} 시트 업데이트 완료: {len(df)}경기")
            
            self.logger.info(f"엑셀 파일 업데이트 완료: {self.excel_path}")
            
        except Exception as e:
            self.logger.error(f"엑셀 파일 업데이트 실패: {e}")
    
    def run_full_update(self):
        """전체 시즌 데이터 업데이트"""
        self.logger.info("=== KBO 데이터 전체 업데이트 시작 ===")
        
        try:
            # 먼저 requests 방법 시도 (더 안정적)
            self.logger.info("requests 방법으로 데이터 수집 시도")
            all_games = self.get_game_data_requests()
            
            # requests 방법이 실패하면 Selenium 시도
            if not all_games:
                self.logger.info("requests 실패. Selenium 방법 시도")
                all_games = self.get_game_data_selenium()
            
            if all_games:
                self.logger.info(f"수집된 전체 경기 데이터: {len(all_games)}건")
                self.update_excel_file(all_games)
            else:
                self.logger.warning("모든 방법으로 데이터 수집 실패")
                
        except Exception as e:
            self.logger.error(f"전체 업데이트 실패: {e}")
        
        self.logger.info("=== KBO 데이터 전체 업데이트 완료 ===")
    
    def run_daily_update(self):
        """일일 업데이트 실행"""
        self.logger.info("=== KBO 데이터 일일 업데이트 시작 ===")
        
        try:
            # 먼저 requests 방법 시도
            current_month = datetime.now().month
            self.logger.info("requests 방법으로 당월 데이터 수집 시도")
            
            # requests 방법으로 현재 월 데이터 수집
            games_data = self.get_game_data_requests()
            
            # 실패하면 Selenium 시도
            if not games_data:
                self.logger.info("requests 실패. Selenium 방법 시도")
                games_data = self.get_game_data_selenium(month=current_month)
            
            if games_data:
                self.logger.info(f"수집된 경기 데이터: {len(games_data)}건")
                self.update_excel_file(games_data)
            else:
                self.logger.warning("모든 방법으로 데이터 수집 실패")
                
        except Exception as e:
            self.logger.error(f"일일 업데이트 실패: {e}")
        
        self.logger.info("=== KBO 데이터 일일 업데이트 완료 ===")
    
    def test_connection(self):
        """연결 테스트"""
        self.logger.info("=== KBO 사이트 연결 테스트 ===")
        
        # requests 테스트
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.base_url, headers=headers, timeout=10)
            self.logger.info(f"requests 연결 성공: {response.status_code}")
        except Exception as e:
            self.logger.error(f"requests 연결 실패: {e}")
        
        # Selenium 테스트
        driver = self.setup_driver()
        if driver:
            try:
                driver.get(self.base_url)
                title = driver.title
                self.logger.info(f"Selenium 연결 성공: {title}")
            except Exception as e:
                self.logger.error(f"Selenium 연결 실패: {e}")
            finally:
                driver.quit()
        else:
            self.logger.error("Selenium 드라이버 생성 실패")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        self.logger.info("KBO 데이터 자동 업데이트 스케줄러 시작")
        
        # 매일 23시에 업데이트
        schedule.every().day.at("23:00").do(self.run_daily_update)
        
        # 매주 일요일 자정에 전체 업데이트
        schedule.every().sunday.at("00:00").do(self.run_full_update)
        
        self.logger.info("스케줄 등록 완료:")
        self.logger.info("- 매일 23:00: 일일 업데이트")
        self.logger.info("- 매주 일요일 00:00: 전체 업데이트")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 확인

def main():
    """메인 실행 함수"""
    scraper = KBODataScraper()
    
    print("KBO 데이터 수집기")
    print("1. 즉시 일일 업데이트 실행")
    print("2. 즉시 전체 업데이트 실행") 
    print("3. 자동 스케줄러 시작")
    print("4. 연결 테스트")
    print("5. 종료")
    
    while True:
        choice = input("\n선택하세요 (1-5): ").strip()
        
        if choice == '1':
            scraper.run_daily_update()
        elif choice == '2':
            scraper.run_full_update()
        elif choice == '3':
            print("자동 스케줄러를 시작합니다. (Ctrl+C로 중단)")
            try:
                scraper.start_scheduler()
            except KeyboardInterrupt:
                print("\n스케줄러가 중단되었습니다.")
        elif choice == '4':
            scraper.test_connection()
        elif choice == '5':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 선택해 주세요.")

if __name__ == "__main__":
    main()


scraper = KBODataScraper()
scraper.run_daily_update()  # 오늘 경기 업데이트
scraper.run_full_update()   # 전체 시즌 업데이트
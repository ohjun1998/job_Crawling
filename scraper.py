import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse
# 엑셀 스타일 설정을 위한 라이브러리 패키지
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

PC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

EXCLUDE_KEYWORDS = [
    "요양", "주간보호", "주야간보호", "보호소", "보호센터", "사회복지", "복지사", 
    "요양보호사", "간호", "물리치료", "작업치료", "치료사", "조리사", "영양사", 
    "노인", "어르신", "케어", "재활", "교육환경보호원", "아동보호", "교사", "운전원", "사무원"
]

def should_exclude(title, corp):
    for kw in EXCLUDE_KEYWORDS:
        if kw in title or kw in corp:
            return True
    return False

def scrape_saramin(keyword):
    jobs = []
    url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={keyword}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.item_recruit')
            for item in items:
                try:
                    title_elem = item.select_one('h2.job_tit a')
                    corp_elem = item.select_one('div.area_corp strong a') or item.select_one('div.area_corp a')
                    if title_elem and corp_elem:
                        title, corp = title_elem.get_text(strip=True), corp_elem.get_text(strip=True)
                        if should_exclude(title, corp): continue
                        jobs.append({"사이트": "사람인", "회사명": corp, "제목": title, "링크": "https://www.saramin.co.kr" + title_elem['href']})
                except Exception: continue
            print(f"  └ [사람인] '{keyword}' -> {len(jobs)}건 수집")
    except Exception: print(f"  └ [사람인] 연결 실패 ({keyword})")
    return jobs

def scrape_jobkorea_mobile(keyword):
    jobs = []
    url = f"https://m.jobkorea.co.kr/search?stext={keyword}"
    try:
        res = requests.get(url, headers=MOBILE_HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('ul.lists-item li') or soup.select('li.list-item') or soup.select('.list-default li')
            for item in items:
                try:
                    title_elem = item.select_one('p.title') or item.select_one('a.link') or item.select_one('.tit')
                    corp_elem = item.select_one('p.name') or item.select_one('span.corp-name') or item.select_one('.corp')
                    if title_elem and corp_elem:
                        title, corp = title_elem.get_text(strip=True), corp_elem.get_text(strip=True)
                        if should_exclude(title, corp): continue
                        link_elem = item.select_one('a')
                        link = "https://m.jobkorea.co.kr" + link_elem['href'] if link_elem else url
                        jobs.append({"사이트": "잡코리아", "회사명": corp, "제목": title, "링크": link})
                except Exception: continue
            print(f"  └ [잡코리아] '{keyword}' -> {len(jobs)}건 수집")
    except Exception: print(f"  └ [잡코리아] 방화벽 차단 또는 타임아웃 ({keyword})")
    return jobs

def scrape_incruit(keyword):
    jobs = []
    url = f"https://search.incruit.com/list/search.asp?col=job&kw={keyword}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.cl_md ul.docs_list li') or soup.select('ul.win_list li')
            for item in items:
                try:
                    title_elem = item.select_one('span.txt_tit a') or item.select_one('p.tit a')
                    corp_elem = item.select_one('span.txt_corp a') or item.select_one('p.cpname a')
                    if title_elem and corp_elem:
                        title, corp = title_elem.get_text(strip=True), corp_elem.get_text(strip=True)
                        if should_exclude(title, corp): continue
                        jobs.append({"사이트": "인크루트", "회사명": corp, "제목": title, "링크": title_elem['href']})
                except Exception: continue
            print(f"  └ [인크루트] '{keyword}' -> {len(jobs)}건 수집")
    except Exception: print(f"  └ [인크루트] 연결 실패 ({keyword})")
    return jobs

def scrape_remember(keyword):
    jobs = []
    url = f"https://career.rememberapp.com/job/search?keyword={keyword}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div[class*="JobCard"]') or soup.select('article')
            for item in items:
                try:
                    title_elem = item.select_one('h3') or item.select_one('[class*="Title"]')
                    corp_elem = item.select_one('span[class*="CompanyName"]') or item.select_one('[class*="Company"]')
                    link_elem = item.select_one('a')
                    if title_elem and corp_elem and link_elem:
                        title, corp = title_elem.get_text(strip=True), corp_elem.get_text(strip=True)
                        if should_exclude(title, corp): continue
                        jobs.append({"사이트": "리멤버", "회사명": corp, "제목": title, "링크": "https://career.rememberapp.com" + link_elem['href']})
                except Exception: continue
            print(f"  └ [리멤버] '{keyword}' -> {len(jobs)}건 수집")
    except Exception: print(f"  └ [리멤버] 방화벽 차단 또는 에러 ({keyword})")
    return jobs

def scrape_google(keyword):
    jobs = []
    query = urllib.parse.quote(f"{keyword} 채용공고")
    url = f"https://www.google.com/search?q={query}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.g') or soup.select('div.tF2Cxc')
            for item in items:
                try:
                    title_elem = item.select_one('h3')
                    link_elem = item.select_one('a')
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        if should_exclude(title, ""): continue
                        jobs.append({"사이트": "구글검색", "회사명": "검색결과참조", "제목": title, "링크": link_elem['href']})
                except Exception: continue
            print(f"  └ [구글검색] '{keyword}' -> {len(jobs)}건 수집")
    except Exception: print(f"  └ [구글검색] 연결 제한 또는 타임아웃 ({keyword})")
    return jobs

def main():
    keywords = ["취약점", "모의해킹", "보안", "보호", "security"]
    all_jobs = []
    
    for kw in keywords:
        print(f"--- 통합 검색 진행 중: {kw} ---")
        all_jobs.extend(scrape_saramin(kw))
        all_jobs.extend(scrape_jobkorea_mobile(kw))
        all_jobs.extend(scrape_incruit(kw))
        all_jobs.extend(scrape_remember(kw))
        all_jobs.extend(scrape_google(kw))
        time.sleep(1.5)
    
    print("\n==================================================")
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.drop_duplicates(subset=['링크'], inplace=True)
        
        # --- 엑셀 디자인 서식 지정 시작 ---
        output_filename = "job_results.xlsx"
        
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="보안 채용공고")
            
            workbook = writer.book
            worksheet = writer.sheets["보안 채용공고"]
            
            # 디자인 테마 설정 (신뢰감을 주는 은은한 네이비/블루 스타일)
            header_fill = PatternFill(start_color="365F91", end_color="365F91", fill_type="solid")
            header_font = Font(name="맑은 고딕", size=11, bold=True, color="FFFFFF")
            data_font = Font(name="맑은 고딕", size=10, color="333333")
            
            align_center = Alignment(horizontal="center", vertical="center")
            align_left = Alignment(horizontal="left", vertical="center")
            
            thin_side = Side(style='thin', color='D9D9D9')
            grid_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
            
            # 제목 행(Header) 스타일 배치
            worksheet.row_dimensions[1].height = 26
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = align_center
                cell.border = grid_border
            
            # 데이터 행(Data) 스타일 배치 및 열 너비 자동 산출
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
                worksheet.row_dimensions[row[0].row].height = 20
                for cell in row:
                    cell.font = data_font
                    cell.border = grid_border
                    # '사이트' 열만 가운데 정렬, 나머지는 좌측 정렬
                    cell.alignment = align_center if cell.column_letter == 'A' else align_left
            
            # 열 너비 유연하게 늘리기 (글자 수 계산 기반 자동 정렬, 링크 열은 45 고정)
            for col in worksheet.columns:
                col_letter = col[0].column_letter
                if col_letter == 'D':  # 링크 열
                    worksheet.column_dimensions[col_letter].width = 45
                else:
                    max_len = 0
                    for cell in col:
                        val = str(cell.value or '')
                        # 한글 가중치 계산 (한글은 영문의 약 2배 공간 차지)
                        char_length = sum(2 if ord(char) > 128 else 1 for char in val)
                        if char_length > max_len:
                            max_len = char_length
                    worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
                    
        print(f"🎉 가독성 개선 완료! 정렬된 엑셀 파일이 {output_filename}로 생성되었습니다.")
    else:
        print("😭 조건에 맞는 공고가 없어 엑셀 파일을 만들지 못했습니다.")
    print("==================================================")

if __name__ == "__main__":
    main()

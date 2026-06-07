import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse

# 사이트별 맞춤형 브라우저 헤더 설정
PC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

# 복지·의료·요양·교육 등 무관한 공고를 걸러내기 위한 블랙리스트
EXCLUDE_KEYWORDS = [
    "요양", "주간보호", "주야간보호", "보호소", "보호센터", "사회복지", "복지사", 
    "요양보호사", "간호", "물리치료", "작업치료", "치료사", "조리사", "영양사", 
    "노인", "어르신", "케어", "재활", "교육환경보호원", "아동보호", "교사", "운전원", "사무원"
]

def should_exclude(title, corp):
    """제목이나 회사명에 제외 키워드가 포함되어 있는지 검사"""
    for kw in EXCLUDE_KEYWORDS:
        if kw in title or kw in corp:
            return True
    return False

def scrape_saramin(keyword):
    """1. 사람인 크롤링 (PC 버전)"""
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
    except Exception:
        print(f"  └ [사람인] 연결 실패 ({keyword})")
    return jobs

def scrape_jobkorea_mobile(keyword):
    """2. 잡코리아 크롤링 (모바일 우회 버전)"""
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
    except Exception:
        print(f"  └ [잡코리아] 방화벽 차단 또는 타임아웃 ({keyword})")
    return jobs

def scrape_incruit(keyword):
    """3. 인크루트 크롤링 (PC 버전)"""
    jobs = []
    url = f"https://search.incruit.com/list/search.asp?col=job&kw={keyword}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 인크루트 채용정보 목록 영역 섹션 선택
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
    except Exception:
        print(f"  └ [인크루트] 연결 실패 ({keyword})")
    return jobs

def scrape_remember(keyword):
    """4. 리멤버 채용 크롤링 (PC 버전)"""
    jobs = []
    url = f"https://career.rememberapp.com/job/search?keyword={keyword}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 리멤버 채용공고 카드 셀렉터 분석 기반 반영
            items = soup.select('div[class*="JobCard"]') or soup.select('article')
            for item in items:
                try:
                    title_elem = item.select_one('h3') or item.select_one('[class*="Title"]')
                    corp_elem = item.select_one('span[class*="CompanyName"]') or item.select_one('[class*="Company"]')
                    link_elem = item.select_one('a')
                    if title_elem and corp_elem and link_elem:
                        title, corp = title_elem.get_text(strip=True), corp_elem.get_text(strip=True)
                        if should_exclude(title, corp): continue
                        jobs.append({"사이트": "리멤버", "회사명": corp, "제목": title, "リンク": "https://career.rememberapp.com" + link_elem['href']})
                except Exception: continue
            print(f"  └ [리멤버] '{keyword}' -> {len(jobs)}건 수집")
        else:
            print(f"  └ [리멤버] 차단됨 (Status Code: {res.status_code})")
    except Exception:
        print(f"  └ [리멤버] 방화벽 차단 또는 에러 ({keyword})")
    return jobs

def scrape_google(keyword):
    """5. 구글 검색결과 크롤링 (채용정보 섹션/링크 추적)"""
    jobs = []
    # 단순 키워드 대신 '채용공고'를 결합하여 정확도 상승
    query = urllib.parse.quote(f"{keyword} 채용공고")
    url = f"https://www.google.com/search?q={query}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 구글 검색결과 메인 텍스트 링크 레이아웃 선택자
            items = soup.select('div.g') or soup.select('div.tF2Cxc')
            for item in items:
                try:
                    title_elem = item.select_one('h3')
                    link_elem = item.select_one('a')
                    # 구글 검색은 회사명을 파싱하기 어려우므로 제목에서 분리 시도하거나 대체 텍스트 처리
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem['href']
                        if should_exclude(title, ""): continue
                        jobs.append({"사이트": "구글검색", "회사명": "검색결과참조", "제목": title, "링크": link})
                except Exception: continue
            print(f"  └ [구글검색] '{keyword}' -> {len(jobs)}건 수집")
        else:
            print(f"  └ [구글검색] 로봇으로 감지되어 차단됨 (Status: {res.status_code})")
    except Exception:
        print(f"  └ [구글검색] 연결 제한 또는 타임아웃 ({keyword})")
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
        time.sleep(1.5) # 공격적 접근으로 오인되지 않도록 딜레이 조정
    
    print("\n==================================================")
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        # 모든 채용공고 주소(링크) 기준으로 중복값 제거
        df.drop_duplicates(subset=['링크'], inplace=True)
        df.to_csv("job_results.csv", index=False, encoding="utf-8-sig")
        print(f"🎉 필터링 및 중복제거 완료! 총 {len(df)}개의 알짜 공고가 job_results.csv에 담겼습니다.")
    else:
        print("😭 모든 사이트 검사 및 필터링 결과 남은 공고가 없습니다.")
    print("==================================================")

if __name__ == "__main__":
    main()

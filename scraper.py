import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 1. 사이트별 맞춤형 헤더
PC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

# 2. 강력한 제외 키워드 리스트 (복지, 요양, 의료, 교육보호 등 제거)
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
    """사람인 PC 버전 크롤링"""
    jobs = []
    url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={keyword}"
    try:
        res = requests.get(url, headers=PC_HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.item_recruit')
            for item in items:
                try:
                    title_elem = item.select_one('h2.job_tit a')
                    corp_elem = item.select_one('div.area_corp strong a') or item.select_one('div.area_corp a')
                    if title_elem and corp_elem:
                        title = title_elem.get_text(strip=True)
                        corp = corp_elem.get_text(strip=True)
                        
                        # [필터링 적용] 제외 키워드가 걸리면 패스
                        if should_exclude(title, corp):
                            continue
                            
                        jobs.append({
                            "사이트": "사람인",
                            "회사명": corp,
                            "제목": title,
                            "リンク": "https://www.saramin.co.kr" + title_elem['href']
                        })
                except Exception:
                    continue
            print(f"  └ [사람인] '{keyword}' 결과: 필터링 후 {len(jobs)}건 수집")
    except Exception:
        print(f"  └ [사람인] 연결 실패 또는 에러 발생 ({keyword})")
    return jobs

def scrape_jobkorea_mobile(keyword):
    """잡코리아 모바일 버전 크롤링"""
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
                        title = title_elem.get_text(strip=True)
                        corp = corp_elem.get_text(strip=True)
                        
                        # [필터링 적용] 제외 키워드가 걸리면 패스
                        if should_exclude(title, corp):
                            continue
                            
                        link_elem = item.select_one('a')
                        link = "https://m.jobkorea.co.kr" + link_elem['href'] if link_elem else url
                        jobs.append({
                            "사이트": "잡코리아",
                            "회사명": corp,
                            "제목": title,
                            "링크": link
                        })
                except Exception:
                    continue
            print(f"  └ [잡코리아] '{keyword}' 결과: 필터링 후 {len(jobs)}건 수집")
    except Exception:
        print(f"  └ [잡코리아] 방화벽 차단 또는 타임아웃 ({keyword})")
    return jobs

def main():
    keywords = ["취약점", "모의해킹", "보안", "보호", "security"]
    all_jobs = []
    
    for kw in keywords:
        print(f"--- 키워드 검색 중: {kw} ---")
        all_jobs.extend(scrape_saramin(kw))
        all_jobs.extend(scrape_jobkorea_mobile(kw))
        time.sleep(1.0)
    
    print("\n========================================")
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.drop_duplicates(subset=['링크'], inplace=True)
        df.to_csv("job_results.csv", index=False, encoding="utf-8-sig")
        print(f"🎉 필터링 완료! 총 {len(df)}개의 IT 보안 공고를 수집하여 job_results.csv에 보관합니다.")
    else:
        print("😭 제외 키워드를 거르고 나니 수집된 보안 공고가 없습니다.")
    print("========================================")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 1. 사이트별 맞춤형 헤더 분리
PC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

def scrape_saramin(keyword):
    """사람인 PC 버전 크롤링"""
    jobs = []
    url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={keyword}"
    try:
        # 사람인은 철저하게 PC 헤더로 접근
        res = requests.get(url, headers=PC_HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.item_recruit')
            for item in items:
                try:
                    title_elem = item.select_one('h2.job_tit a')
                    corp_elem = item.select_one('div.area_corp strong a') or item.select_one('div.area_corp a')
                    if title_elem and corp_elem:
                        jobs.append({
                            "사이트": "사람인",
                            "회사명": corp_elem.get_text(strip=True),
                            "제목": title_elem.get_text(strip=True),
                            "링크": "https://www.saramin.co.kr" + title_elem['href']
                        })
                except Exception:
                    continue
            print(f"  └ [사람인] '{keyword}' 결과: {len(jobs)}건 수집 완료")
    except Exception as e:
        print(f"  └ [사람인] 연결 실패 또는 에러 발생 ({keyword})")
    return jobs

def scrape_jobkorea_mobile(keyword):
    """잡코리아 모바일 버전 크롤링"""
    jobs = []
    url = f"https://m.jobkorea.co.kr/search?stext={keyword}"
    try:
        # 잡코리아는 모바일 헤더로 우회 접근
        res = requests.get(url, headers=MOBILE_HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 모바일 검색결과 카드 컴포넌트 선택자 구체화
            items = soup.select('ul.lists-item li') or soup.select('li.list-item') or soup.select('.list-default li')
            for item in items:
                try:
                    title_elem = item.select_one('p.title') or item.select_one('a.link') or item.select_one('.tit')
                    corp_elem = item.select_one('p.name') or item.select_one('span.corp-name') or item.select_one('.corp')
                    if title_elem and corp_elem:
                        link_elem = item.select_one('a')
                        link = "https://m.jobkorea.co.kr" + link_elem['href'] if link_elem else url
                        jobs.append({
                            "사이트": "잡코리아",
                            "회사명": corp_elem.get_text(strip=True),
                            "제목": title_elem.get_text(strip=True),
                            "링크": link
                        })
                except Exception:
                    continue
            print(f"  └ [잡코리아] '{keyword}' 결과: {len(jobs)}건 수집 완료")
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
        time.sleep(1.0) # 안전을 위한 1초 대기
    
    print("\n========================================")
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        # 중복 링크 제거
        df.drop_duplicates(subset=['링크'], inplace=True)
        df.to_csv("job_results.csv", index=False, encoding="utf-8-sig")
        print(f"🎉 최종 성공! 총 {len(df)}개의 고유 공고를 job_results.csv에 저장했습니다.")
    else:
        print("😭 모든 사이트에서 공고를 가져오지 못했습니다. 위 로그를 확인해 주세요.")
    print("========================================")

if __name__ == "__main__":
    main()

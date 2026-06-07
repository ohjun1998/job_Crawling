import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 봇 차단 방지를 위한 브라우저 헤더 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

def scrape_saramin(keyword):
    """사람인 채용공고 크롤링"""
    jobs = []
    url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={keyword}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.item_recruit')
            for item in items:
                try:
                    title_elem = item.select_one('h2.job_tit a')
                    corp_elem = item.select_one('div.area_corp strong a') or item.select_one('div.area_corp a')
                    
                    if title_elem and corp_elem:
                        title = title_elem.get_text(strip=True)
                        link = "https://www.saramin.co.kr" + title_elem['href']
                        corp = corp_elem.get_text(strip=True)
                        jobs.append({"사이트": "사람인", "회사명": corp, "제목": title, "링크": link})
                except Exception:
                    continue
    except Exception as e:
        print(f"사람인 크롤링 실패 ({keyword}): {e}")
    return jobs

def scrape_jobkorea(keyword):
    """잡코리아 채용공고 크롤링"""
    jobs = []
    url = f"https://www.jobkorea.co.kr/Search/?stext={keyword}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('li.list-post')
            for item in items:
                try:
                    title_elem = item.select_one('div.post-list-info a.title')
                    corp_elem = item.select_one('div.post-list-corp a')
                    
                    if title_elem and corp_elem:
                        title = title_elem.get_text(strip=True)
                        link = "https://www.jobkorea.co.kr" + title_elem['href']
                        corp = corp_elem.get_text(strip=True)
                        jobs.append({"사이트": "잡코리아", "회사명": corp, "제목": title, "링크": link})
                except Exception:
                    continue
    except Exception as e:
        print(f"잡코리아 크롤링 실패 ({keyword}): {e}")
    return jobs

def main():
    # 수집할 핵심 키워드 리스트
    keywords = ["취약점", "모의해킹", "보안", "보호", "security"]
    all_jobs = []
    
    for kw in keywords:
        print(f"--- 키워드 검색 중: {kw} ---")
        all_jobs.extend(scrape_saramin(kw))
        all_jobs.extend(scrape_jobkorea(kw))
        # 사이트 과부하 및 차단 방지를 위한 디레이 (0.5초)
        time.sleep(0.5)
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        
        # 중복 수집된 공고는 '링크' 기준으로 깔끔하게 제거
        df.drop_duplicates(subset=['リンク' if 'リンク' in df.columns else '링크'], inplace=True)
        
        # 결과 저장 (엑셀 깨짐 방지용 utf-8-sig 인코딩)
        df.to_csv("job_results.csv", index=False, encoding="utf-8-sig")
        print(f"\n🎉 성공! 총 {len(df)}개의 고유 채용 공고를 수집하여 job_results.csv에 저장했습니다.")
    else:
        print("수집된 공고가 없습니다.")

if __name__ == "__main__":
    main()

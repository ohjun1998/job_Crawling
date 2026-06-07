import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
}

def scrape_saramin(keyword):
    """사람인 채용공고 크롤링"""
    jobs = []
    url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={keyword}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
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
    except Exception as e:
        print(f"[-] 사람인 연결 실패 ({keyword})")
    return jobs

def scrape_jobkorea_mobile(keyword):
    """잡코리아 모바일 웹 채용공고 크롤링 (방화벽 우회 시도)"""
    jobs = []
    # PC 주소 대신 모바일(m.jobkorea.co.kr) 주소 사용
    url = f"https://m.jobkorea.co.kr/search?stext={keyword}"
    try:
        # 방화벽 차단 시 오래 대기하지 않도록 타임아웃을 4초로 단축
        res = requests.get(url, headers=HEADERS, timeout=4)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 모바일 잡코리아의 검색 결과 리스트 태그 선택자
            items = soup.select('ul.lists-item li') or soup.select('li.list-item')
            for item in items:
                try:
                    title_elem = item.select_one('p.title') or item.select_one('a.link')
                    corp_elem = item.select_one('p.name') or item.select_one('span.corp-name')
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
    except requests.exceptions.Timeout:
        print(f"[-] 잡코리아 방화벽 차단 가동 중 (타임아웃 - {keyword})")
    except Exception as e:
        print(f"[-] 잡코리아 기타 오류 ({keyword})")
    return jobs

def main():
    keywords = ["취약점", "모의해킹", "보안", "보호", "security"]
    all_jobs = []
    
    for kw in keywords:
        print(f"--- 키워드 검색 중: {kw} ---")
        all_jobs.extend(scrape_saramin(kw))
        all_jobs.extend(scrape_jobkorea_mobile(kw))
        time.sleep(1.0) # 차단 확률을 낮추기 위해 요청 간격 1초로 연장
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.drop_duplicates(subset=['링크'], inplace=True)
        df.to_csv("job_results.csv", index=False, encoding="utf-8-sig")
        print(f"\n🎉 완료! 총 {len(df)}개의 공고를 수집하여 job_results.csv에 반영했습니다.")
    else:
        print("\n😭 수집된 공고가 전혀 없습니다.")

if __name__ == "__main__":
    main()

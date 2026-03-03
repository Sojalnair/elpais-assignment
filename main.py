import os
import re
import time
import requests
from collections import Counter
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

BS_USERNAME = "sojalnair_JhEvbY"
BS_KEY = "eGZutFseRNGPt2W8btoX"
BS_URL = f"https://{BS_USERNAME}:{BS_KEY}@hub-cloud.browserstack.com/wd/hub"

def create_options(config):
    browser_name = config.get('browserName', '').lower()
    
    if 'device' in config:
        opts = ChromeOptions() if 'chrome' in browser_name else SafariOptions()
        opts.set_capability('bstack:options', {
            'deviceName': config['device'],
            'osVersion': config['osVersion'],
            'realMobile': config.get('realMobile', 'true'),
            'sessionName': config['name']
        })
    else:
        if browser_name == 'chrome':
            opts = ChromeOptions()
        elif browser_name == 'firefox':
            opts = FirefoxOptions()
        else:
            opts = SafariOptions()
        
        opts.set_capability('bstack:options', {
            'os': config['os'],
            'osVersion': config['osVersion'],
            'browserVersion': config.get('browserVersion', 'latest'),
            'sessionName': config['name']
        })
    
    opts.browser_version = config.get('browserVersion', 'latest')
    return opts

BROWSERS = [
    {
        "browserName": "Chrome",
        "browserVersion": "latest",
        "os": "Windows",
        "osVersion": "10",
        "name": "Chrome Windows 10"
    },
    {
        "browserName": "Safari",
        "browserVersion": "latest",
        "os": "OS X",
        "osVersion": "Big Sur",
        "name": "Safari macOS"
    },
    {
        "browserName": "Firefox",
        "browserVersion": "latest",
        "os": "Windows",
        "osVersion": "11",
        "name": "Firefox Windows 11"
    },
    {
        "browserName": "chrome",
        "device": "Samsung Galaxy S22",
        "realMobile": "true",
        "osVersion": "12.0",
        "name": "Samsung Mobile"
    },
    {
        "browserName": "safari",
        "device": "iPhone 13",
        "realMobile": "true",
        "osVersion": "15",
        "name": "iPhone"
    }
]

def run_scraper(browser_id):
    config = BROWSERS[browser_id]
    name = f"Browser_{browser_id + 1}"
    
    print(f"\n{name} started on {config['name']}")
    
    img_folder = f"images/browser_{browser_id + 1}"
    os.makedirs(img_folder, exist_ok=True)
    
    results = open(f"output_{browser_id + 1}.txt", "w", encoding="utf-8")
    
    try:
        driver = webdriver.Remote(command_executor=BS_URL, options=create_options(config))
        wait = WebDriverWait(driver, 20)
        
        results.write(f"Browser: {config['name']}\n{'='*60}\n")
        
        driver.get("https://elpais.com/opinion/")
        print(f"{name}: Loaded opinion page")
        
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
            cookie_btn.click()
            time.sleep(1)
        except:
            pass
        
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h2 a")))
        
        links = driver.find_elements(By.CSS_SELECTOR, "h2 a")
        urls = [links[i].get_attribute("href") for i in range(min(5, len(links))) if links[i].get_attribute("href")]
        
        print(f"{name}: Found {len(urls)} articles")
        
        titles_en = []
        
        for idx, url in enumerate(urls, 1):
            print(f"{name}: Article {idx}")
            
            results.write(f"\n{'='*60}\nArticle {idx}\n{'='*60}\n")
            
            driver.get(url)
            time.sleep(2)
            
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            try:
                h1 = driver.find_element(By.TAG_NAME, "h1").text
                results.write(f"\nTítulo (ES):\n{h1}\n")
                
                try:
                    h1_en = GoogleTranslator(source='es', target='en').translate(h1)
                    titles_en.append(h1_en)
                    results.write(f"\nTitle (EN):\n{h1_en}\n")
                except:
                    results.write("\nTranslation error\n")
            except:
                results.write("\nTitle not found\n")
            
            results.write("\nContent:\n")
            
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
                
                content = driver.execute_script("""
                    let a = document.querySelector("article");
                    return a ? a.innerText : "";
                """)
                
                paras = content.split("\n")
                for p in paras:
                    p = p.strip()
                    if p and len(p) > 50:
                        results.write(p + "\n")
            except:
                results.write("Content extraction failed\n")
            
            try:
                driver.execute_script("window.scrollTo(0, 300);")
                time.sleep(1)
                
                img_url = None
                
                css_list = [
                    "div.c_m_a_m-h img",
                    "article figure img",
                    "article img",
                    "figure img"
                ]
                
                for css in css_list:
                    try:
                        imgs = driver.find_elements(By.CSS_SELECTOR, css)
                        for i in imgs:
                            src = i.get_attribute("src")
                            if src and "http" in src and ("elpais" in src or "cloudfront" in src):
                                img_url = src
                                break
                        if img_url:
                            break
                    except:
                        continue
                
                if img_url:
                    r = requests.get(img_url, timeout=10)
                    if r.status_code == 200:
                        path = f"{img_folder}/article_{idx}.jpg"
                        with open(path, "wb") as f:
                            f.write(r.content)
                        results.write(f"\nImage: {path}\n")
                        print(f"{name}: Article {idx} image saved")
                else:
                    results.write("\nNo image\n")
            except Exception as e:
                results.write(f"\nImage error: {e}\n")
        
        results.write(f"\n{'='*60}\nWord Analysis\n{'='*60}\n")
        
        words = []
        for t in titles_en:
            w = re.findall(r'\b[a-zA-Z]+\b', t.lower())
            words.extend(w)
        
        counts = Counter(words)
        repeated = {w: c for w, c in counts.items() if c > 2}
        
        if repeated:
            results.write("\nRepeated words (>2):\n")
            for w, c in sorted(repeated.items(), key=lambda x: x[1], reverse=True):
                results.write(f"  {w}: {c}\n")
        else:
            results.write("\nNo repeated words\n")
        
        print(f"{name}: Done")
        
        driver.quit()
        results.close()
        
        return {
            "browser": name,
            "status": "OK",
            "config": config['name'],
            "count": len(urls),
            "titles": titles_en
        }
    
    except Exception as e:
        print(f"{name}: Error - {e}")
        results.write(f"\nError: {e}\n")
        results.close()
        
        try:
            driver.quit()
        except:
            pass
        
        return {
            "browser": name,
            "status": "FAILED",
            "config": config.get('name', 'Unknown'),
            "error": str(e)
        }

if __name__ == "__main__":
    print("Starting El Pais scraper on BrowserStack")
    print(f"Running {len(BROWSERS)} browsers in parallel\n")
    
    os.makedirs("images", exist_ok=True)
    
    with ThreadPoolExecutor(max_workers=5) as pool:
        tasks = {pool.submit(run_scraper, i): i for i in range(len(BROWSERS))}
        
        outcomes = []
        for task in as_completed(tasks):
            outcomes.append(task.result())
    
    print("\n" + "="*60)
    print("Results:")
    print("="*60)
    
    ok = sum(1 for o in outcomes if o['status'] == 'OK')
    
    for o in outcomes:
        mark = "✓" if o['status'] == 'OK' else "✗"
        print(f"{mark} {o['browser']} - {o['config']}: {o['status']}")
        if o['status'] == 'FAILED':
            print(f"  Error: {o['error']}")
    
    print(f"\nCompleted: {ok}/{len(BROWSERS)}")
    
    if ok > 0:
        print("\n" + "="*60)
        print("Combined word frequency:")
        print("="*60)
        
        all_t = []
        for o in outcomes:
            if o['status'] == 'OK' and 'titles' in o:
                all_t.extend(o['titles'])
        
        all_w = []
        for t in all_t:
            all_w.extend(re.findall(r'\b[a-zA-Z]+\b', t.lower()))
        
        c = Counter(all_w)
        rep = {w: cnt for w, cnt in c.items() if cnt > 2}
        
        if rep:
            print("\nWords appearing more than twice:")
            for w, cnt in sorted(rep.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {w}: {cnt}")
    
    print("\n" + "="*60)
    print("Files saved:")
    print("  output_*.txt")
    print("  images/browser_*/")
    print("="*60)
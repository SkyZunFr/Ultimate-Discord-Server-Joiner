import tls_client
import threading
import os
import time
import random
import re
import signal
import sys
import queue
import ctypes
import json
from typing import List, Tuple, Optional, Dict, Union
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

                                   
try:
    import colorama
    colorama.init(autoreset=True)
    USE_COLORAMA = True
except ImportError:
    USE_COLORAMA = False

                                           
if USE_COLORAMA:
    from colorama import Fore, Style
    class Colors:
        GREEN = Fore.GREEN
        RED = Fore.RED
        YELLOW = Fore.YELLOW
        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        MAGENTA = Fore.MAGENTA
        WHITE = Fore.WHITE
        RESET = Style.RESET_ALL
        BOLD = Style.BRIGHT
else:
                                    
    class Colors:
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

                      
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
CONFIG_FILE = 'config.json'

                                         
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

                          
def load_config() -> Dict:
    """Charge la configuration depuis config.json ou crée un fichier par défaut."""
    default_config = {
        "max_captcha_before_ban": 3,
        "delay_between_joins_min": 45,
        "delay_between_joins_max": 75,
        "use_proxy": True,
        "proxy_rotation": True,
        "retry_on_failure": True,
        "max_retries": 3,
        "bypass_onboarding": True,
        "bypass_rules": True,
        "bypass_restorecord": False,
        "timeout": 30,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                                                                                   
                if 'delay_between_joins' in config and 'delay_between_joins_min' not in config:
                    delay_value = config['delay_between_joins']
                    config['delay_between_joins_min'] = max(1, delay_value - 15)
                    config['delay_between_joins_max'] = delay_value + 15
                    del config['delay_between_joins']
                                              
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=4)
                
                                                                               
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
                                                                     
            try:
                print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Error loading config.json: {e}. Using default config.")
            except:
                print(f"[WARNING] Error loading config.json: {e}. Using default config.")
            return default_config
    else:
                                               
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        try:
            print(f"{Colors.CYAN}[INFO]{Colors.RESET} Created default config.json file")
        except:
            print(f"[INFO] Created default config.json file")
        return default_config

                                       
CONFIG = load_config()

session = tls_client.Session(
    random_tls_extension_order=True
)

cookies = {
    '__dcfduid': 'a598dfd0f4b611f09bab3fc1d23c209a',
    '__sdcfduid': 'a598dfd1f4b611f09bab3fc1d23c209ae62943a2dc6d970ec5d6ba06f55dc4bcc683b40d98249114ee8f40a50ac0ed0c',
    'locale': 'en-US',
    '_cfuvid': 'OHooIS_j66BhOTWPar5rOVymnAjvSJhB1TWIxMYvp4Y-1768818570964-0.0.1.1-604800000',
    'cf_clearance': 'X_KKc3jkfFAa3YeQ2aA52zMMQGLrX1QRu8kMFfRl0iw-1768833054-1.2.1.1-NIifnsugZsKT9D.ufyepNfm4ZE0LNMrmVUr4m6.cjO.k54yofKzUY5CemtIEV1gB5hHwq.ppn9dChU3nuVGYkb6JMgZ.MFK.a7HFagDV50WFSBDoVYfUXWX1Wx0YZi26bwAM0QWGCwGLnd1vZ1iIxyiRSnS3gzmC1ljTyjkFqx.9csbHck3hbqcrMUju_SJ_3iKmuglam5Q8NcSkFfTo._9qGd3oievBcqf9QbzKVx4',
}

base_headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.6',
    'content-type': 'application/json',
    'origin': 'https://discord.com',
    'priority': 'u=1, i',
    'referer': 'https://discord.com/channels/@me',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': CONFIG.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'),
    'x-context-properties': 'eyJsb2NhdGlvbiI6IkpvaW4gR3VpbGQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6IjEwMjkxMTcyNzAxMTY0MzM5MiIsImxvY2F0aW9uX2NoYW5uZWxfaWQiOiI1MzE2MjQ4NDEyNjczODAyMzQiLCJsb2NhdGlvbl9jaGFubmVsX3R5cGUiOjB9',
    'x-debug-options': 'bugReporterEnabled',
    'x-discord-locale': 'en-US',
    'x-discord-timezone': 'Europe/Paris',
    'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZSwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0NC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTQ0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6Imh0dHBzOi8vZGlzY29yZC5jb20vIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiZGlzY29yZC5jb20iLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjo0ODY4MjcsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImNsaWVudF9sYXVuY2hfaWQiOiJmODIwMjg4OC1iZTRhLTQzMDQtOTdjOC05NmQ1M2UxZDM3MDgiLCJsYXVuY2hfc2lnbmF0dXJlIjoiZDQzN2E1NmUtMjE4Mi00NTBmLTg5MzYtMTAxNDM4MTRkMjA5IiwiY2xpZW50X2hlYXJ0YmVhdF9zZXNzaW9uX2lkIjoiZWQwNzgyOGYtZmI2Mi00NmMzLTk4N2QtYTU3ZThkOTkwMzBmIiwiY2xpZW50X2FwcF9zdGF0ZSI6ImZvY3VzZWQifQ==',
}

json_data = {
    'session_id': 'ea2f091b284c059d4729f8df361c5291',
}

file_lock = threading.Lock()
stop_flag = threading.Event()                            

                
stats = {
    'joined': 0,
    'failed': 0,
    'captchas': 0,
    'invalid_tokens': 0,
    'banned_tokens': 0,
}
stats_lock = threading.Lock()

                                           
token_queue = queue.Queue()
invite_queue = queue.Queue()
proxy_queue = queue.Queue()

                                                 
token_captcha_count = {}
captcha_lock = threading.Lock()

                                             
active_threads = {}
threads_lock = threading.Lock()

def read_file_lines(filename: str) -> List[str]:
    """Lit les lignes d'un fichier et retourne une liste."""
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return lines

def write_file_lines(filename: str, lines: List[str]):
    """Écrit les lignes dans un fichier."""
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def append_to_file(filename: str, line: str):
    """Ajoute une ligne à la fin d'un fichier."""
    with file_lock:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

def update_window_title():
    """Met à jour le titre de la fenêtre avec les stats."""
    try:
        with stats_lock:
            title = f"Discord Joiner | Joined: {stats['joined']} | Failed: {stats['failed']} | Captchas: {stats['captchas']} | Invalid: {stats['invalid_tokens']} | Banned: {stats['banned_tokens']}"
                                           
        if sys.platform == 'win32':
            ctypes.windll.kernel32.SetConsoleTitleW(title)
    except:
        pass

def remove_from_invites(invite: str):
    """Retire une invite du fichier input/invites.txt."""
    with file_lock:
        invites_path = os.path.join(INPUT_DIR, 'invites.txt')
        invites = read_file_lines(invites_path)
        if invite in invites:
            invites.remove(invite)
            write_file_lines(invites_path, invites)

def backup_invites():
    """Copies the content of input/invites.txt to output/invitesbackup.txt on startup."""
    invites_path = os.path.join(INPUT_DIR, 'invites.txt')
    if os.path.exists(invites_path):
        invites = read_file_lines(invites_path)
        backup_path = os.path.join(OUTPUT_DIR, 'invitesbackup.txt')
        write_file_lines(backup_path, invites)
        print(f"{Colors.CYAN}[BACKUP]{Colors.RESET} {Colors.BOLD}{len(invites)}{Colors.RESET} invites backed up to {backup_path}")

                                                   
global_blacklist = set()
blacklist_lock = threading.Lock()

def load_blacklist() -> set:
    """Charge la blacklist des guild_id depuis le fichier."""
    blacklist_path = os.path.join(OUTPUT_DIR, 'blacklist.txt')
    if os.path.exists(blacklist_path):
        return set(read_file_lines(blacklist_path))
    return set()

def reload_blacklist():
    """Recharge la blacklist depuis le fichier (pour synchroniser avec les autres threads)."""
    global global_blacklist
    with blacklist_lock:
        global_blacklist = load_blacklist()

def add_to_blacklist(guild_id: str):
    """Ajoute un guild_id à la blacklist."""
    global global_blacklist
    if not guild_id:
        return
    blacklist_path = os.path.join(OUTPUT_DIR, 'blacklist.txt')
    with blacklist_lock:
        if guild_id not in global_blacklist:
            append_to_file(blacklist_path, guild_id)
            global_blacklist.add(guild_id)
            print(f"{Colors.YELLOW}[BLACKLIST]{Colors.RESET} Added guild {Colors.BOLD}{guild_id}{Colors.RESET} to blacklist")

def is_blacklisted(guild_id: str) -> bool:
    """Vérifie si un guild_id est dans la blacklist."""
    global global_blacklist
    with blacklist_lock:
        return guild_id and guild_id in global_blacklist

def parse_proxy(proxy_str: str) -> Optional[str]:
    """Parse un proxy au format user:pass@ip:port ou ip:port. Retourne une chaîne pour tls_client."""
    try:
        if '@' in proxy_str:
                                       
            auth_part, host_part = proxy_str.split('@', 1)
            username, password = auth_part.split(':', 1)
            ip, port = host_part.split(':', 1)
                                                                                   
            proxy_url = f'http://{username}:{password}@{ip}:{port}'
            return proxy_url
        else:
                             
            ip, port = proxy_str.split(':', 1)
            proxy_url = f'http://{ip}:{port}'
            return proxy_url
    except Exception as e:
        print(f"{Colors.RED}[PROXY ERROR]{Colors.RESET} Error parsing proxy: {e}")
        return None

def get_next_proxy() -> Optional[str]:
    """Récupère le prochain proxy disponible depuis la queue. Retourne une chaîne pour tls_client."""
    try:
        proxy_str = proxy_queue.get_nowait()
        return parse_proxy(proxy_str)
    except queue.Empty:
        return None

def extract_version_from_useragent(useragent: str) -> str:
    """Extrait la version Chrome du user-agent."""
    match = re.search(r'Chrome/(\d+)', useragent)
    return match.group(1) if match else "144"

def make_request_with_timeout_and_retry(session, method, url, max_retries=None, timeout=None, **kwargs):
    """Fait une requête avec timeout et retry."""
    if max_retries is None:
        max_retries = CONFIG.get('max_retries', 3) if CONFIG.get('retry_on_failure', True) else 1
    if timeout is None:
        timeout = CONFIG.get('timeout', 30)
    
    last_exception = None
    for attempt in range(max_retries):
        try:
                                                                              
            with ThreadPoolExecutor(max_workers=1) as executor:
                if method.lower() == 'get':
                    future = executor.submit(session.get, url, **kwargs)
                elif method.lower() == 'post':
                    future = executor.submit(session.post, url, **kwargs)
                elif method.lower() == 'put':
                    future = executor.submit(session.put, url, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                try:
                    response = future.result(timeout=timeout)
                    return response
                except FutureTimeoutError:
                    last_exception = f"Timeout after {timeout}s (attempt {attempt + 1}/{max_retries})"
                    if attempt < max_retries - 1:
                        time.sleep(0.5)                           
                        continue
                    raise Exception(last_exception)
        except FutureTimeoutError:
            last_exception = f"Timeout after {timeout}s (attempt {attempt + 1}/{max_retries})"
            if attempt < max_retries - 1:
                time.sleep(0.5)                           
        except Exception as e:
            last_exception = str(e)
            if attempt < max_retries - 1:
                time.sleep(0.5)                           
            else:
                raise
    
                                                              
    raise Exception(f"Request failed after {max_retries} attempts: {last_exception}")

def get_guild_id_from_invite(token: str, invite_code: str, token_session: tls_client.Session, proxy: Optional[str] = None) -> Optional[str]:
    """Récupère le guild_id depuis l'invite."""
    headers = base_headers.copy()
    headers['authorization'] = token
    try:
                                       
        request_kwargs = {'headers': headers}
        if proxy and CONFIG.get('use_proxy', True):
            try:
                token_session.proxies = proxy
            except:
                try:
                    token_session.proxies = {'http': proxy, 'https': proxy}
                except:
                    pass
            request_kwargs['proxy'] = proxy
        
        response = make_request_with_timeout_and_retry(
            token_session,
            'get',
            f'https://discord.com/api/v9/invites/{invite_code}?with_counts=true&with_expiration=true',
            **request_kwargs
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('guild', {}).get('id')
    except Exception as e:
        print(f"{Colors.YELLOW}[GET_GUILD_ID]{Colors.RESET} Error: {e}")
    return None

def check_onboarding(token: str, guild_id: str, token_session: tls_client.Session) -> Optional[bool]:
    """Vérifie si le serveur a un onboarding."""
    headers = base_headers.copy()
    headers['authorization'] = token
    try:
        response = token_session.get(
            f'https://discord.com/api/v9/guilds/{guild_id}/onboarding',
            headers=headers,
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('enabled', False)
        return False
    except:
        return None

def check_rules(token: str, guild_id: str, token_session: tls_client.Session) -> Optional[bool]:
    """Vérifie si le serveur a des règles de vérification."""
    headers = base_headers.copy()
    headers['authorization'] = token
    try:
        response = token_session.get(
            f'https://discord.com/api/v9/guilds/{guild_id}/member-verification?with_guild=false&invite_code=',
            headers=headers,
        )
        if response.status_code == 200:
            return True
        if response.status_code == 403:
            return False
        return None
    except:
        return None

def bypass_onboarding(token: str, guild_id: str, token_session: tls_client.Session) -> bool:
    """Bypass l'onboarding d'un serveur."""
    headers = base_headers.copy()
    headers['authorization'] = token
    headers['referer'] = f'https://discord.com/channels/{guild_id}/@home'
    
    try:
                                            
        response = token_session.get(
            f'https://discord.com/api/v9/guilds/{guild_id}/onboarding',
            headers=headers,
        )
        
        if response.status_code != 200:
            return False
        
        onboarding_data = response.json()
        prompts = onboarding_data.get('prompts', [])
        responses = []
        prompts_seen = {}
        responses_seen = {}
        current_time = int(time.time() * 1000)
        
        for prompt in prompts:
            prompt_id = prompt.get('id')
            prompts_seen[prompt_id] = current_time
            
            options = prompt.get('options', [])
            for option in options:
                option_id = option.get('id')
                responses_seen[option_id] = current_time
            
            if prompt.get('single_select'):
                if prompt.get('required', False) or random.choice([True, False]):
                    selected_option = random.choice(options) if options else None
                    if selected_option:
                        responses.append(selected_option['id'])
            else:
                if not prompt.get('required', False):
                    selected_options = random.sample(
                        options,
                        k=random.randint(0, len(options))
                    ) if options else []
                    for option in selected_options:
                        responses.append(option['id'])
                else:
                    for option in options:
                        responses.append(option['id'])
        
        if not responses:
            return False
        
                              
        response = token_session.post(
            f'https://discord.com/api/v9/guilds/{guild_id}/onboarding-responses',
            headers=headers,
            json={
                'onboarding_responses': responses,
                'onboarding_prompts_seen': prompts_seen,
                'onboarding_responses_seen': responses_seen,
            },
        )
        
        return response.status_code == 200
    except:
        return False

def bypass_rules(token: str, guild_id: str, token_session: tls_client.Session) -> bool:
    """Bypass les règles de vérification d'un serveur."""
    headers = base_headers.copy()
    headers['authorization'] = token
    
    try:
                                          
        response = token_session.get(
            f'https://discord.com/api/v9/guilds/{guild_id}/member-verification?with_guild=false&invite_code=',
            headers=headers,
        )
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        version = data.get('version')
        form_fields = data.get('form_fields', [])
        
                              
        response = token_session.put(
            f'https://discord.com/api/v9/guilds/{guild_id}/requests/@me',
            headers=headers,
            json={
                'version': version,
                'form_fields': form_fields,
            },
        )
        
        return response.status_code == 201
    except:
        return False

def create_session_for_token(token: str, proxy: Optional[str] = None) -> Optional[tls_client.Session]:
    """Creates a session with fresh cookies for a token via a first request. NO PROXY for cookies."""
                                                                             
                                                                     
    token_session = tls_client.Session(
        random_tls_extension_order=True
    )
    
                                                                                  
    
                                    
    headers = base_headers.copy()
    headers['authorization'] = token
                                              
    if 'content-type' in headers:
        del headers['content-type']
    
    try:
                                                                                             
                                                                 
        response = make_request_with_timeout_and_retry(
            token_session,
            'get',
            'https://discord.com/api/v9/users/@me',
            headers=headers,
            cookies=cookies,
            max_retries=CONFIG.get('max_retries', 3)
        )
        
        if response.status_code == 200:
                                                                    
                                                                                         
            print(f"{Colors.GREEN}[COOKIES]{Colors.RESET} Fresh cookies retrieved for token {Colors.CYAN}{token[:20]}...{Colors.RESET}")
            return token_session
        else:
            print(f"{Colors.YELLOW}[COOKIES]{Colors.RESET} Failed to retrieve cookies (status {response.status_code})")
            return None
    except Exception as e:
        print(f"{Colors.RED}[COOKIES]{Colors.RESET} Error retrieving cookies: {str(e)}")
        return None

def increment_captcha(token: str) -> bool:
    """Incrémenter le compteur de captcha pour un token. Retourne True si le token doit être banni."""
    with captcha_lock:
        if token not in token_captcha_count:
            token_captcha_count[token] = 0
        token_captcha_count[token] += 1
        
        if token_captcha_count[token] >= CONFIG['max_captcha_before_ban']:
                             
            captcha_path = os.path.join(OUTPUT_DIR, 'tokenscaptcha.txt')
            append_to_file(captcha_path, token)
            with stats_lock:
                stats['banned_tokens'] += 1
            update_window_title()
            return True
        return False

def reset_captcha_count(token: str):
    """Réinitialise le compteur de captcha pour un token (après un succès)."""
    with captcha_lock:
        if token in token_captcha_count:
            token_captcha_count[token] = 0

def test_proxy_ip(proxy: str, token_session: tls_client.Session) -> Optional[str]:
    """Teste le proxy en récupérant l'IP visible. Retourne l'IP ou None si erreur."""
    try:
                                            
        token_session.proxies = {
            'http': proxy,
            'https': proxy
        }
                                        
        response = token_session.get('https://api.ipify.org?format=json', proxy=proxy)
        if response.status_code == 200:
            return response.json().get('ip')
    except:
        pass
    return None

def join_server(token: str, invite_code: str, token_session: tls_client.Session, proxy: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
    """Attempts to join a Discord server with a token. Returns (success, message, guild_id)."""
    headers = base_headers.copy()
    headers['authorization'] = token
    
    try:
                         
        url = f'https://discord.com/api/v9/invites/{invite_code}'
        
                                                                                         
        request_kwargs = {
            'headers': headers,
            'json': json_data
        }
        
        if proxy and CONFIG.get('use_proxy', True):
                                                                                    
                                       
            try:
                                                                             
                token_session.proxies = proxy
            except:
                try:
                                                              
                    token_session.proxies = {
                        'http': proxy,
                        'https': proxy
                    }
                except:
                    pass
            
                                                                       
            request_kwargs['proxy'] = proxy
                                              
            proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
            print(f"{Colors.CYAN}[PROXY]{Colors.RESET} Using proxy for join: {Colors.BOLD}{proxy_display}{Colors.RESET}")
            
                                                                                                  
                                                                                               
                                                             
                                                     
                                                          
                      
                                                                          
                                        
                                
                                                              
                                      
                                        
                                   
                       
                                                          
                                                                              
                                                                                                                                
                                                                
                                        
                                                                                                        
        
                                                    
        response = make_request_with_timeout_and_retry(
            token_session,
            'post',
            url,
            max_retries=CONFIG.get('max_retries', 3) if CONFIG.get('retry_on_failure', True) else 1,
            **request_kwargs
        )
        
        if response.status_code == 200:
                                                
            try:
                data = response.json()
                guild_id = data.get('guild', {}).get('id')
                reset_captcha_count(token)                                              
                return True, "Success", str(guild_id) if guild_id else None
            except:
                reset_captcha_count(token)
                return True, "Success", None
        elif response.status_code == 403:
                                          
            with stats_lock:
                stats['captchas'] += 1
            update_window_title()
            should_ban = increment_captcha(token)
            if should_ban:
                return False, "Token banned (too many captchas)", None
            return False, "Captcha or Rate limit", None
        elif response.status_code == 400:
                                          
            try:
                error_data = response.json()
                error_message = str(error_data)
                                                       
                if 'captcha' in error_message.lower() or 'captcha_key' in error_message.lower():
                                                               
                    with stats_lock:
                        stats['captchas'] += 1
                    update_window_title()
                    should_ban = increment_captcha(token)
                    if should_ban:
                        return False, "Token banned (too many captchas)", None
                    return False, "Captcha", None
            except:
                error_message = response.text[:200] if response.text else "Aucun détail disponible"
                if 'captcha' in error_message.lower():
                    with stats_lock:
                        stats['captchas'] += 1
                    update_window_title()
                    should_ban = increment_captcha(token)
                    if should_ban:
                        return False, "Token banned (too many captchas)", None
                    return False, "Captcha", None
            
                                                                    
            print(f"{Colors.RED}[ERROR 400]{Colors.RESET} {Colors.BOLD}{invite_code}{Colors.RESET} - Details: {error_message}")
            return False, f"Error 400: {error_message[:100]}", None
        elif response.status_code == 401:
            return False, "Invalid token", None
        elif response.status_code == 404:
            return False, "Invalid invite", None
        elif response.status_code == 429:
                                                  
            return False, "Rate limit", None
        else:
                                              
            try:
                error_data = response.json()
                error_message = str(error_data)
                                                
                if len(error_message) > 200:
                    error_message = error_message[:200] + "..."
            except:
                                                                    
                error_text = response.text[:200] if response.text else "Aucun détail disponible"
                if error_text.startswith("<!DOCTYPE") or error_text.startswith("<html"):
                    error_message = "HTML response (likely rate limit or Cloudflare)"
                else:
                    error_message = error_text
            
            print(f"{Colors.RED}[ERROR {response.status_code}]{Colors.RESET} {Colors.BOLD}{invite_code}{Colors.RESET} - {error_message}")
            return False, f"Error {response.status_code}", None
    
    except Exception as e:
        return False, str(e), None

def detect_and_bypass(token: str, guild_id: str, token_session: tls_client.Session, useragent: str, invite_code: str, proxy: Optional[str] = None):
    """Detects and bypasses server restrictions (onboarding, rules, restorecord). Returns True if bypass was needed."""
    if not guild_id:
        print(f"{Colors.CYAN}[BYPASS]{Colors.RESET} No need - Token: {Colors.CYAN}{token[:20]}...{Colors.RESET} | Invite: {Colors.BOLD}{invite_code}{Colors.RESET}")
        return False
    
    bypass_needed = False
    bypass_success = False
    
    try:
                                                                             
        headers = base_headers.copy()
        headers['authorization'] = token
        
                                                               
        if proxy and CONFIG.get('use_proxy', True):
            token_session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
                                                          
        request_kwargs = {'headers': headers, 'cookies': cookies}
        if proxy and CONFIG.get('use_proxy', True):
            request_kwargs['proxy'] = proxy
        
                                       
        if CONFIG.get('bypass_onboarding', True):
            try:
                response = make_request_with_timeout_and_retry(
                    token_session,
                    'get',
                    f'https://discord.com/api/v9/guilds/{guild_id}/onboarding',
                    max_retries=2,
                    **request_kwargs
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('enabled'):
                        bypass_needed = True
                        success = bypass_onboarding_simple(token, guild_id, token_session, useragent, proxy)
                        if success:
                            bypass_success = True
            except Exception as e:
                print(f"{Colors.YELLOW}[BYPASS]{Colors.RESET} Error checking onboarding: {e}")
        
                               
        if CONFIG.get('bypass_rules', True):
            try:
                response = make_request_with_timeout_and_retry(
                    token_session,
                    'get',
                    f'https://discord.com/api/v9/guilds/{guild_id}/member-verification?with_guild=false&invite_code=',
                    max_retries=2,
                    **request_kwargs
                )
                
                if response.status_code == 200:
                    bypass_needed = True
                    success = bypass_rules_simple(token, guild_id, token_session, useragent, proxy)
                    if success:
                        bypass_success = True
            except Exception as e:
                print(f"{Colors.YELLOW}[BYPASS]{Colors.RESET} Error checking rules: {e}")
        
                              
        if bypass_needed:
            if bypass_success:
                print(f"{Colors.GREEN}[BYPASS]{Colors.RESET} Bypassed - Token: {Colors.CYAN}{token[:20]}...{Colors.RESET} | Invite: {Colors.BOLD}{invite_code}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[BYPASS]{Colors.RESET} Bypass attempted - Token: {Colors.CYAN}{token[:20]}...{Colors.RESET} | Invite: {Colors.BOLD}{invite_code}{Colors.RESET}")
        else:
            print(f"{Colors.CYAN}[BYPASS]{Colors.RESET} No need - Token: {Colors.CYAN}{token[:20]}...{Colors.RESET} | Invite: {Colors.BOLD}{invite_code}{Colors.RESET}")
        
        return bypass_needed
            
    except Exception as e:
        print(f"{Colors.RED}[BYPASS]{Colors.RESET} Error during detection: {str(e)}")
        return False

def bypass_onboarding_simple(token: str, guild_id: str, token_session: tls_client.Session, useragent: str, proxy: Optional[str] = None) -> bool:
    """Bypasses a server's onboarding. Returns True if successful."""
    try:
        headers = base_headers.copy()
        headers['authorization'] = token
        headers['referer'] = f'https://discord.com/channels/{guild_id}/@home'
        
                                                               
        if proxy and CONFIG.get('use_proxy', True):
            try:
                token_session.proxies = proxy                         
            except:
                try:
                    token_session.proxies = {'http': proxy, 'https': proxy}                    
                except:
                    pass
        
                                        
        request_kwargs = {'headers': headers, 'cookies': cookies}
        if proxy and CONFIG.get('use_proxy', True):
            request_kwargs['proxy'] = proxy
        
                                            
        response = make_request_with_timeout_and_retry(
            token_session,
            'get',
            f'https://discord.com/api/v9/guilds/{guild_id}/onboarding',
            max_retries=2,
            **request_kwargs
        )
        
        if response.status_code != 200:
            return False
        
        onboarding_data = response.json()
        prompts = onboarding_data.get('prompts', [])
        responses = []
        prompts_seen = {}
        responses_seen = {}
        current_time = int(time.time() * 1000)
        
        for prompt in prompts:
            prompt_id = prompt.get('id')
            prompts_seen[prompt_id] = current_time
            
            options = prompt.get('options', [])
            for option in options:
                option_id = option.get('id')
                responses_seen[option_id] = current_time
            
            if prompt.get('single_select'):
                if prompt.get('required', False) or random.choice([True, False]):
                    selected_option = random.choice(options) if options else None
                    if selected_option:
                        responses.append(selected_option['id'])
            else:
                if not prompt.get('required', False):
                    selected_options = random.sample(
                        options,
                        k=random.randint(0, len(options))
                    ) if options else []
                    for option in selected_options:
                        responses.append(option['id'])
                else:
                    for option in options:
                        responses.append(option['id'])
        
        if not responses:
            return False
        
                                                               
        if proxy and CONFIG.get('use_proxy', True):
            try:
                token_session.proxies = proxy                         
            except:
                try:
                    token_session.proxies = {'http': proxy, 'https': proxy}                    
                except:
                    pass
        
                                                  
        post_kwargs = {
            'headers': headers,
            'cookies': cookies,
            'json': {
                'onboarding_responses': responses,
                'onboarding_prompts_seen': prompts_seen,
                'onboarding_responses_seen': responses_seen,
            }
        }
        if proxy and CONFIG.get('use_proxy', True):
            post_kwargs['proxy'] = proxy
        
                              
        response = make_request_with_timeout_and_retry(
            token_session,
            'post',
            f'https://discord.com/api/v9/guilds/{guild_id}/onboarding-responses',
            max_retries=2,
            **post_kwargs
        )
        
        return response.status_code == 200
    except Exception as e:
        return False

def bypass_rules_simple(token: str, guild_id: str, token_session: tls_client.Session, useragent: str, proxy: Optional[str] = None) -> bool:
    """Bypasses a server's verification rules. Returns True if successful."""
    try:
        headers = base_headers.copy()
        headers['authorization'] = token
        
                                                               
        if proxy and CONFIG.get('use_proxy', True):
            try:
                token_session.proxies = proxy                         
            except:
                try:
                    token_session.proxies = {'http': proxy, 'https': proxy}                    
                except:
                    pass
        
                                        
        request_kwargs = {'headers': headers, 'cookies': cookies}
        if proxy and CONFIG.get('use_proxy', True):
            request_kwargs['proxy'] = proxy
        
                                          
        response = make_request_with_timeout_and_retry(
            token_session,
            'get',
            f'https://discord.com/api/v9/guilds/{guild_id}/member-verification?with_guild=false&invite_code=',
            max_retries=2,
            **request_kwargs
        )
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        version = data.get('version')
        form_fields = data.get('form_fields', [])
        
                                                                      
        if proxy and CONFIG.get('use_proxy', True):
            try:
                token_session.proxies = proxy                         
            except:
                try:
                    token_session.proxies = {'http': proxy, 'https': proxy}                    
                except:
                    pass
        
                                                 
        put_kwargs = {
            'headers': headers,
            'cookies': cookies,
            'json': {
                'version': version,
                'form_fields': form_fields,
            }
        }
        if proxy and CONFIG.get('use_proxy', True):
            put_kwargs['proxy'] = proxy
        
                              
        response = make_request_with_timeout_and_retry(
            token_session,
            'put',
            f'https://discord.com/api/v9/guilds/{guild_id}/requests/@me',
            max_retries=2,
            **put_kwargs
        )
        
        return response.status_code == 201
    except Exception as e:
        return False

def get_next_token() -> Optional[str]:
    """Récupère le prochain token disponible depuis la queue."""
    try:
        return token_queue.get_nowait()
    except queue.Empty:
        return None

def get_next_invite() -> Optional[str]:
    """Récupère la prochaine invite disponible depuis la queue."""
    try:
        return invite_queue.get_nowait()
    except queue.Empty:
        return None

def worker(thread_id: int):
    """Worker function for a thread. Gère automatiquement la réallocation des tokens."""
    current_token = None
    current_proxy = None
    
    print(f"{Colors.GREEN}[THREAD {thread_id}]{Colors.RESET} Thread started and ready")
    
    try:
        while not stop_flag.is_set():
                                                 
            if current_token is None:
                current_token = get_next_token()
                if current_token is None:
                                                                    
                    with threads_lock:
                        if thread_id in active_threads:
                            del active_threads[thread_id]
                    print(f"{Colors.YELLOW}[THREAD {thread_id}]{Colors.RESET} No more tokens available, stopping thread")
                    time.sleep(0.25)
                    return
            
                                                                                
            if current_proxy is None and CONFIG.get('use_proxy', True):
                current_proxy = get_next_proxy()
            
                                  
            invite_code = get_next_invite()
            if invite_code is None:
                                                                
                with threads_lock:
                    if thread_id in active_threads:
                        del active_threads[thread_id]
                print(f"{Colors.YELLOW}[THREAD {thread_id}]{Colors.RESET} No more invites available, stopping thread")
                return
            
            proxy_info = ""
            if current_proxy:
                proxy_display = current_proxy.split('@')[-1] if '@' in current_proxy else current_proxy
                proxy_info = f" with proxy {Colors.CYAN}{proxy_display}{Colors.RESET}"
            print(f"{Colors.BLUE}[THREAD {thread_id}]{Colors.RESET} Attempting to join {Colors.BOLD}{invite_code}{Colors.RESET} with token {Colors.CYAN}{current_token[:20]}...{Colors.RESET}{proxy_info}")
            
                                     
            if stop_flag.is_set():
                return
            
                                                                                            
            token_session = create_session_for_token(current_token, None)
            
                                                                       
            if stop_flag.is_set():
                return
            
            if token_session is None:
                failed_path = os.path.join(OUTPUT_DIR, 'invitesfailed.txt')
                append_to_file(failed_path, invite_code)
                print(f"{Colors.RED}{Colors.BOLD}✗ FAILED{Colors.RESET} {Colors.RED}→ {Colors.BOLD}{invite_code}{Colors.RESET} {Colors.RED}- Reason: Unable to retrieve cookies{Colors.RESET}")
                with stats_lock:
                    stats['failed'] += 1
                update_window_title()
                                                                                    
                invite_queue.put(invite_code)
                                                       
                current_token = get_next_token()
                if current_token is None:
                    with threads_lock:
                        if thread_id in active_threads:
                            del active_threads[thread_id]
                    return
                                                               
                current_proxy = get_next_proxy()
                continue
            
                                                    
                                                   
            print(f"{Colors.CYAN}[THREAD {thread_id}]{Colors.RESET} Checking blacklist for invite {Colors.BOLD}{invite_code}{Colors.RESET}...")
            try:
                guild_id_from_invite = get_guild_id_from_invite(current_token, invite_code, token_session, current_proxy)
                if guild_id_from_invite:
                                                                                          
                    if is_blacklisted(guild_id_from_invite):
                        print(f"{Colors.YELLOW}[BLACKLIST]{Colors.RESET} Server {Colors.BOLD}{guild_id_from_invite}{Colors.RESET} is blacklisted, skipping invite {Colors.BOLD}{invite_code}{Colors.RESET}")
                                                                             
                        remove_from_invites(invite_code)
                        continue
            except Exception as e:
                print(f"{Colors.RED}[THREAD {thread_id}]{Colors.RESET} Error checking blacklist: {e}")
                import traceback
                traceback.print_exc()
                                                   
            
                                                                                       
            print(f"{Colors.CYAN}[THREAD {thread_id}]{Colors.RESET} Attempting to join server with invite {Colors.BOLD}{invite_code}{Colors.RESET}...")
            try:
                success, message, guild_id = join_server(current_token, invite_code, token_session, current_proxy)
                print(f"{Colors.CYAN}[THREAD {thread_id}]{Colors.RESET} Join result: success={success}, message={message}")
            except Exception as e:
                print(f"{Colors.RED}[THREAD {thread_id}]{Colors.RESET} Error in join_server: {e}")
                import traceback
                traceback.print_exc()
                                        
                success = False
                message = f"Exception: {str(e)}"
                guild_id = None
            
                                                        
            if stop_flag.is_set():
                return
            
            if success:
                                                                      
                remove_from_invites(invite_code)
                done_path = os.path.join(OUTPUT_DIR, 'invitesdone.txt')
                append_to_file(done_path, invite_code)
                print(f"{Colors.GREEN}{Colors.BOLD}✓ SUCCESS{Colors.RESET} {Colors.GREEN}→ Token: {Colors.CYAN}{current_token[:20]}...{Colors.RESET} | Invite: {Colors.BOLD}{invite_code}{Colors.RESET} {Colors.GREEN}has been added successfully!{Colors.RESET}")
                with stats_lock:
                    stats['joined'] += 1
                update_window_title()
                
                                                                                             
                                                                                                
                if guild_id:
                    add_to_blacklist(guild_id)
                
                                                             
                if guild_id and (CONFIG.get('bypass_onboarding', True) or CONFIG.get('bypass_rules', True)):
                    useragent = base_headers.get('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                    detect_and_bypass(current_token, guild_id, token_session, useragent, invite_code, current_proxy)
            else:
                                                            
                if "Invalid token" in message:
                    print(f"{Colors.RED}[TOKEN INVALID]{Colors.RESET} Token {Colors.CYAN}{current_token[:20]}...{Colors.RESET} is invalid, getting new token...")
                    with stats_lock:
                        stats['invalid_tokens'] += 1
                    update_window_title()
                                                
                    current_token = get_next_token()
                    if current_token is None:
                        with threads_lock:
                            if thread_id in active_threads:
                                del active_threads[thread_id]
                        return
                                                     
                    invite_queue.put(invite_code)
                    continue
                elif "Token banned" in message:
                    print(f"{Colors.RED}[TOKEN BANNED]{Colors.RESET} Token {Colors.CYAN}{current_token[:20]}...{Colors.RESET} banned due to too many captchas")
                                                
                    current_token = get_next_token()
                    if current_token is None:
                        with threads_lock:
                            if thread_id in active_threads:
                                del active_threads[thread_id]
                        return
                                                     
                    invite_queue.put(invite_code)
                    continue
                
                                                                                                            
                if "Invalid invite" not in message:
                                                                                           
                    invite_queue.put(invite_code)
                
                                                                  
                failed_path = os.path.join(OUTPUT_DIR, 'invitesfailed.txt')
                append_to_file(failed_path, invite_code)
                
                                                          
                if "Captcha" in message or "captcha" in message.lower():
                    print(f"{Colors.YELLOW}{Colors.BOLD}⚠ CAPTCHA{Colors.RESET} {Colors.YELLOW}→ Token: {Colors.CYAN}{current_token[:20]}...{Colors.RESET} | Invite: {Colors.BOLD}{invite_code}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}{Colors.BOLD}✗ FAILED{Colors.RESET} {Colors.RED}→ {Colors.BOLD}{invite_code}{Colors.RESET} {Colors.RED}- Reason: {message}{Colors.RESET}")
                
                with stats_lock:
                    stats['failed'] += 1
                update_window_title()
            
                                                                               
                                                                                   
            delay_min = CONFIG.get('delay_between_joins_min', 45)
            delay_max = CONFIG.get('delay_between_joins_max', 75)
            delay = random.randint(delay_min, delay_max)
            
                                                                     
            print(f"{Colors.CYAN}[THREAD {thread_id}]{Colors.RESET} Waiting {Colors.BOLD}{delay}s{Colors.RESET} before next join...")
            
                                                        
            if stop_flag.wait(delay):
                return
            
                                                                                         
                                                      
            print(f"{Colors.GREEN}[THREAD {thread_id}]{Colors.RESET} Delay finished, continuing to next invite...")
                                                                                         
    except Exception as e:
        print(f"{Colors.RED}[THREAD {thread_id}]{Colors.RESET} Fatal error in worker: {e}")
        import traceback
        traceback.print_exc()
    finally:
        with threads_lock:
            if thread_id in active_threads:
                del active_threads[thread_id]
        print(f"{Colors.YELLOW}[THREAD {thread_id}]{Colors.RESET} Thread stopped")

def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}        Discord Server Joiner{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * 60}{Colors.RESET}\n")
    
                       
    backup_invites()
    
                                      
    tokens_path = os.path.join(INPUT_DIR, 'tokens.txt')
    invites_path = os.path.join(INPUT_DIR, 'invites.txt')
    proxies_path = os.path.join(INPUT_DIR, 'proxies.txt')
    
    tokens = read_file_lines(tokens_path)
    invites = read_file_lines(invites_path)
    proxies = read_file_lines(proxies_path)
    
    if not tokens:
        print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.RESET} {Colors.RED}No tokens found in {tokens_path}{Colors.RESET}")
        return
    
    if not invites:
        print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.RESET} {Colors.RED}No invites found in {invites_path}{Colors.RESET}")
        return
    
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {Colors.BOLD}{len(tokens)}{Colors.RESET} token(s) loaded")
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {Colors.BOLD}{len(invites)}{Colors.RESET} invite(s) to process")
    if CONFIG.get('use_proxy', True):
        if proxies:
            print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {Colors.BOLD}{len(proxies)}{Colors.RESET} proxy(ies) loaded")
        else:
            print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Proxies enabled but no proxies found in {proxies_path}")
    else:
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Proxies disabled (proxyless mode)")
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Max captchas before ban: {Colors.BOLD}{CONFIG['max_captcha_before_ban']}{Colors.RESET}")
    delay_min = CONFIG.get('delay_between_joins_min', 45)
    delay_max = CONFIG.get('delay_between_joins_max', 75)
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Delay between joins: {Colors.BOLD}{delay_min}-{delay_max}s{Colors.RESET} (random)")
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Bypass onboarding: {Colors.BOLD}{CONFIG.get('bypass_onboarding', True)}{Colors.RESET}")
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} Bypass rules: {Colors.BOLD}{CONFIG.get('bypass_rules', True)}{Colors.RESET}")
    
                                             
    done_path = os.path.join(OUTPUT_DIR, 'invitesdone.txt')
    failed_path = os.path.join(OUTPUT_DIR, 'invitesfailed.txt')
    captcha_path = os.path.join(OUTPUT_DIR, 'tokenscaptcha.txt')
    blacklist_path = os.path.join(OUTPUT_DIR, 'blacklist.txt')
    
    if not os.path.exists(done_path):
        write_file_lines(done_path, [])
    if not os.path.exists(failed_path):
        write_file_lines(failed_path, [])
    if not os.path.exists(captcha_path):
        write_file_lines(captcha_path, [])
    if not os.path.exists(blacklist_path):
        write_file_lines(blacklist_path, [])
    
                                                     
    banned_tokens = set(read_file_lines(captcha_path))
    
                                               
    reload_blacklist()
    if global_blacklist:
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {Colors.BOLD}{len(global_blacklist)}{Colors.RESET} server(s) in blacklist")
    
                                                                           
    valid_tokens = [token for token in tokens if token not in banned_tokens]
    if len(valid_tokens) < len(tokens):
        print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {Colors.BOLD}{len(tokens) - len(valid_tokens)}{Colors.RESET} banned token(s) excluded")
    
    if not valid_tokens:
        print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.RESET} {Colors.RED}No valid tokens available (all are banned){Colors.RESET}")
        return
    
                                   
    while True:
        try:
            max_threads_input = input(f"\n{Colors.CYAN}[CONFIG]{Colors.RESET} Enter number of threads (max {min(len(valid_tokens), len(invites))}): ")
            max_threads = int(max_threads_input)
            if max_threads <= 0:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Number of threads must be greater than 0")
                continue
            if max_threads > min(len(valid_tokens), len(invites)):
                print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Limiting threads to {min(len(valid_tokens), len(invites))}")
                max_threads = min(len(valid_tokens), len(invites))
            break
        except ValueError:
            print(f"{Colors.RED}[ERROR]{Colors.RESET} Please enter a valid number")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[STOPPING]{Colors.RESET} Exiting...")
            return
    
    for token in valid_tokens:
        token_queue.put(token)
    for invite in invites:
        invite_queue.put(invite)
                                              
    if CONFIG.get('use_proxy', True):
        if not proxies:
            print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Proxies enabled but no proxies found in {proxies_path}")
        else:
            for proxy in proxies:
                proxy_str = proxy.strip()
                if proxy_str:
                                                  
                    parsed_proxy = parse_proxy(proxy_str)
                    if parsed_proxy:
                        proxy_queue.put(proxy_str)
                        print(f"{Colors.GREEN}[PROXY LOADED]{Colors.RESET} {Colors.CYAN}{parsed_proxy.split('@')[-1] if '@' in parsed_proxy else parsed_proxy}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}[PROXY ERROR]{Colors.RESET} Failed to parse proxy: {proxy_str}")
    
    threads = []
    
    print(f"\n{Colors.CYAN}[STARTING]{Colors.RESET} Creating {Colors.BOLD}{max_threads}{Colors.RESET} thread(s)...\n")
    
                                 
    for i in range(max_threads):
        thread = threading.Thread(target=worker, args=(i+1,), daemon=True)
        thread.start()
        threads.append(thread)
        with threads_lock:
            active_threads[i+1] = thread
    
                                    
    update_window_title()
    
    try:
                                                                                         
        while True:
                                                          
            if invite_queue.empty():
                                                                                 
                time.sleep(2)
                if invite_queue.empty():
                    print(f"\n{Colors.GREEN}[INFO]{Colors.RESET} All invites processed")
                    break
            
                                                        
            with threads_lock:
                if len(active_threads) == 0:
                    print(f"\n{Colors.GREEN}[INFO]{Colors.RESET} All threads finished")
                    break
            
            time.sleep(1)
        
                                                               
        for thread in threads:
            thread.join(timeout=10)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}{Colors.BOLD}[STOPPING]{Colors.RESET} {Colors.YELLOW}Interruption detected (Ctrl+C), stopping all threads...{Colors.RESET}")
        stop_flag.set()                              
        
                                                 
        print(f"{Colors.YELLOW}[STOPPING]{Colors.RESET} Waiting for threads to finish...")
        for thread in threads:
            thread.join(timeout=5)                                 
        
        print(f"{Colors.YELLOW}[STOPPING]{Colors.RESET} {Colors.GREEN}All threads have been stopped.{Colors.RESET}\n")
        sys.exit(0)
    
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}        All threads are finished{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * 60}{Colors.RESET}\n")
    
                              
    remaining_invites = read_file_lines(invites_path)
    done_invites = read_file_lines(done_path)
    failed_invites = read_file_lines(failed_path)
    
    print(f"{Colors.CYAN}[STATS]{Colors.RESET} Remaining invites: {Colors.BOLD}{len(remaining_invites)}{Colors.RESET}")
    print(f"{Colors.CYAN}[STATS]{Colors.RESET} Successful invites: {Colors.GREEN}{Colors.BOLD}{stats['joined']}{Colors.RESET}")
    print(f"{Colors.CYAN}[STATS]{Colors.RESET} Failed invites: {Colors.RED}{Colors.BOLD}{stats['failed']}{Colors.RESET}")
    print(f"{Colors.CYAN}[STATS]{Colors.RESET} Captchas encountered: {Colors.YELLOW}{Colors.BOLD}{stats['captchas']}{Colors.RESET}")
    print(f"{Colors.CYAN}[STATS]{Colors.RESET} Invalid tokens: {Colors.RED}{Colors.BOLD}{stats['invalid_tokens']}{Colors.RESET}")
    print(f"{Colors.CYAN}[STATS]{Colors.RESET} Banned tokens (captcha): {Colors.RED}{Colors.BOLD}{stats['banned_tokens']}{Colors.RESET}\n")

if __name__ == "__main__":
    main()

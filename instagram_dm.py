import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import database as db
from datetime import datetime
import random
import os

st.set_page_config(
    page_title="MISS ALIYA | INSTAGRAM DM",
    page_icon="📷",
    layout="wide"
)

# ============ PREMIUM CSS ============
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

* {
    font-family: 'Outfit', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #f5f0ff 0%, #e9eaff 40%, #fdf4ff 100%);
}

.main .block-container {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(12px);
    border-radius: 32px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
}

.main-header {
    background: linear-gradient(135deg, #fff, #faf5ff);
    border-radius: 28px;
    padding: 30px;
    text-align: center;
}

.main-header h1 {
    background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 3rem;
    font-weight: 900;
}

.center-image-container {
    display: flex;
    justify-content: center;
    margin: -50px auto 20px auto;
}

.center-image {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.stButton>button {
    background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
    color: white;
    font-weight: 700;
    padding: 12px 28px;
    border-radius: 40px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(131,58,180,0.3);
}

.console-output {
    background: #0f172a;
    border-radius: 20px;
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
    color: #00ff88;
    font-family: monospace;
}

.console-line {
    border-left: 3px solid #833ab4;
    padding: 8px 15px;
    margin-bottom: 8px;
    background: #1e293b;
    border-radius: 10px;
    font-family: monospace;
}

.footer {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #833ab4, #fd1d1d);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: 800;
}

.success-box {
    background: linear-gradient(135deg, #10b981, #34d399);
    border-radius: 20px;
    padding: 15px;
    color: white;
    font-weight: 700;
    text-align: center;
}

.error-box {
    background: linear-gradient(135deg, #ef4444, #f87171);
    border-radius: 20px;
    padding: 15px;
    color: white;
    font-weight: 700;
    text-align: center;
}
</style>
"""

center_image_html = """
<div class="center-image-container">
    <img class="center-image" src="https://i.ibb.co/rG4yDJ7D/f5b610892f1e.jpg" alt="MISS ALIYA">
</div>
"""

st.markdown(custom_css + center_image_html, unsafe_allow_html=True)

# ============ SESSION STATE ============
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        st.session_state.logs.append(formatted_msg)
    print(formatted_msg)

def setup_instagram_browser(automation_state=None):
    log_message("Setting up Chrome for Instagram...", automation_state)
    
    chrome_options = Options()
    # HEADLESS MODE OFF - Instagram detect nahi karega
    # chrome_options.add_argument('--headless=new')  # COMMENTED - visible mode me chalega
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    # Instagram ke liye important
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        log_message("Instagram browser ready!", automation_state)
        return driver
    except Exception as e:
        log_message(f"Browser error: {e}", automation_state)
        raise

def find_instagram_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding Instagram message input...', automation_state)
    time.sleep(5)
    
    # Instagram DM input selectors (updated)
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][placeholder*="Message"]',
        'div[aria-label*="Message" i]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="Message"]',
        'div[role="textbox"][contenteditable="true"]',
        'div[class*="x1i10hfl"]',
        'div[class*="x6s0dn4"]',
        'div[class*="x1ypdohk"]'
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    log_message(f'{process_id}: ✅ Found input with: {selector}', automation_state)
                    return element
        except:
            continue
    
    # Try JavaScript to find any editable div
    try:
        element = driver.execute_script("""
            const elements = document.querySelectorAll('[contenteditable="true"]');
            for (let el of elements) {
                if (el.offsetParent !== null) {
                    return el;
                }
            }
            return null;
        """)
        if element:
            log_message(f'{process_id}: ✅ Found via JavaScript', automation_state)
            return element
    except:
        pass
    
    # Screenshot for debugging
    try:
        driver.save_screenshot('debug_instagram.png')
        log_message(f'{process_id}: Screenshot saved as debug_instagram.png', automation_state)
        log_message(f'{process_id}: Current URL: {driver.current_url}', automation_state)
    except:
        pass
    
    return None

def send_instagram_messages(config, automation_state, user_id, process_id='IG-1'):
    driver = None
    try:
        log_message(f'{process_id}: 🚀 Starting Instagram DM automation...', automation_state)
        driver = setup_instagram_browser(automation_state)
        
        # Step 1: Open Instagram
        log_message(f'{process_id}: Opening Instagram...', automation_state)
        driver.get('https://www.instagram.com/')
        time.sleep(5)
        
        # Step 2: Add cookies if available
        if config.get('cookies') and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            try:
                cookie_string = config['cookies']
                cookie_pairs = cookie_string.split(';')
                
                for cookie in cookie_pairs:
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        try:
                            driver.add_cookie({'name': name, 'value': value, 'domain': '.instagram.com'})
                        except:
                            pass
                
                driver.refresh()
                time.sleep(5)
                log_message(f'{process_id}: Cookies added and page refreshed!', automation_state)
            except Exception as e:
                log_message(f'{process_id}: Cookie error: {e}', automation_state)
        
        # Step 3: Get chat target (username or numeric ID)
        chat_target = config.get('chat_id', '').strip()
        if not chat_target:
            log_message(f'{process_id}: ❌ No chat target specified!', automation_state)
            automation_state.running = False
            return 0
        
        log_message(f'{process_id}: Opening DM with @{chat_target}...', automation_state)
        
        # Try both URL formats
        dm_url = f'https://www.instagram.com/direct/t/{chat_target}/'
        log_message(f'{process_id}: URL: {dm_url}', automation_state)
        driver.get(dm_url)
        time.sleep(8)
        
        # Check if we're on the right page
        current_url = driver.current_url
        log_message(f'{process_id}: Current URL after navigation: {current_url}', automation_state)
        
        if '/direct/inbox' in current_url:
            log_message(f'{process_id}: ⚠️ User not found or username invalid!', automation_state)
            log_message(f'{process_id}: Check if @{chat_target} is correct Instagram username', automation_state)
            automation_state.running = False
            return 0
        
        # Step 4: Find message input
        message_input = find_instagram_message_input(driver, process_id, automation_state)
        
        if not message_input:
            log_message(f'{process_id}: ❌ Message input not found!', automation_state)
            log_message(f'{process_id}: Try: Visible mode, check if DM page opened correctly', automation_state)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        log_message(f'{process_id}: ✅ Message input found!', automation_state)
        
        # Step 5: Prepare messages
        delay = max(int(config.get('delay', 30)), 25)
        messages_sent = 0
        messages_list = [msg.strip() for msg in config.get('messages', 'Hello!').split('\n') if msg.strip()]
        
        if not messages_list:
            messages_list = ['Hello!']
        
        log_message(f'{process_id}: Loaded {len(messages_list)} messages. Delay: {delay}s', automation_state)
        
        # Step 6: Start sending loop
        while automation_state.running:
            base_message = messages_list[automation_state.message_rotation_index % len(messages_list)]
            automation_state.message_rotation_index += 1
            
            if config.get('name_prefix'):
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                # Click on input first
                driver.execute_script("arguments[0].click();", message_input)
                time.sleep(1)
                
                # Type message using JavaScript
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    element.focus();
                    element.innerText = message;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                """, message_input, message_to_send)
                
                time.sleep(2)
                
                # Send with Enter key
                driver.execute_script("""
                    const element = arguments[0];
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    });
                    const enterEvent2 = new KeyboardEvent('keypress', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    });
                    element.dispatchEvent(enterEvent);
                    element.dispatchEvent(enterEvent2);
                """, message_input)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: ✅ Sent #{messages_sent}: "{message_to_send[:40]}..."', automation_state)
                
                # Random delay to avoid detection
                actual_delay = random.randint(delay, delay + 15)
                log_message(f'{process_id}: Waiting {actual_delay}s before next message...', automation_state)
                
                # Wait for send to complete
                time.sleep(3)
                
                # Clear input for next message
                driver.execute_script("arguments[0].innerText = '';", message_input)
                
                time.sleep(actual_delay)
                
            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:100]}', automation_state)
                time.sleep(60)
        
        log_message(f'{process_id}: 🛑 Automation stopped. Total sent: {messages_sent}', automation_state)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: 💥 Fatal error: {str(e)}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def start_automation(user_config, user_id):
    automation_state = st.session_state.automation_state
    if automation_state.running:
        return
    
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    automation_state.message_rotation_index = 0
    db.set_automation_running(user_id, True)
    
    username = db.get_username(user_id)
    thread = threading.Thread(target=send_instagram_messages, args=(user_config, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)

# ============ LOGIN PAGE ============
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>📷 MISS ALIYA INSTAGRAM DM</h1>
        <p>INSTAGRAM DM AUTOMATION SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 SIGN-UP"])
    
    with tab1:
        st.markdown("### WELCOME BACK! 👋")
        username = st.text_input("USERNAME", key="login_username", placeholder="Enter your username")
        password = st.text_input("PASSWORD", key="login_password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🚀 LOGIN", use_container_width=True):
                if username and password:
                    user_id = db.verify_user(username, password)
                    if user_id:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success(f"✅ WELCOME {username}!")
                        st.rerun()
                    else:
                        st.error("❌ INVALID USERNAME OR PASSWORD!")
                else:
                    st.warning("⚠️ FILL BOTH FIELDS")
    
    with tab2:
        st.markdown("### CREATE NEW ACCOUNT 🎉")
        new_username = st.text_input("CHOOSE USERNAME", key="signup_username", placeholder="Choose username")
        new_password = st.text_input("CHOOSE PASSWORD", key="signup_password", type="password", placeholder="Create password")
        confirm_password = st.text_input("CONFIRM PASSWORD", key="confirm_password", type="password", placeholder="Re-enter password")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🎉 CREATE ACCOUNT", use_container_width=True):
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        success, msg = db.create_user(new_username, new_password)
                        if success:
                            st.success(f"✅ {msg} PLEASE LOGIN!")
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.error("❌ PASSWORDS DON'T MATCH!")
                else:
                    st.warning("⚠️ FILL ALL FIELDS")

def main_app():
    st.markdown("""
    <div class="main-header">
        <h1>📷 MISS ALIYA INSTAGRAM DM</h1>
        <p>AUTOMATE YOUR INSTAGRAM DIRECT MESSAGES</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)
        st.session_state.logged_in = False
        st.rerun()
    
    user_config = db.get_user_config(st.session_state.user_id)
    
    if not user_config:
        user_config = {
            'chat_id': '',
            'name_prefix': '',
            'delay': 35,
            'cookies': '',
            'messages': 'Hello!\nHow are you?\nNice to meet you!'
        }
    
    tab1, tab2 = st.tabs(["⚙️ SETTINGS", "🔥 AUTOMATION"])
    
    with tab1:
        st.markdown("### 🔐 INSTAGRAM DM SETTINGS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chat_id = st.text_input(
                "📎 INSTAGRAM USERNAME/ID", 
                value=user_config.get('chat_id', ''),
                placeholder="e.g., john_doe or 123456789",
                help="Jisko DM bhejna hai uska Instagram username ya numeric ID"
            )
            
            name_prefix = st.text_input(
                "🏷️ YOUR NAME PREFIX", 
                value=user_config.get('name_prefix', ''),
                placeholder="e.g., Aliya",
                help="Message ke pehle lagna wala naam"
            )
            
            delay = st.number_input(
                "⏱️ DELAY (SECONDS)", 
                min_value=25, 
                max_value=300,
                value=user_config.get('delay', 35),
                help="Instagram ke liye kam se kam 25-30 sec delay rakhein"
            )
        
        with col2:
            cookies = st.text_area(
                "🍪 INSTAGRAM COOKIES", 
                value=user_config.get('cookies', ''),
                placeholder="sessionid=xxx; csrftoken=xxx; ds_user_id=xxx; mid=xxx",
                height=150,
                help="Apne Instagram account ki cookies paste karein"
            )
            
            messages = st.text_area(
                "💬 MESSAGES (one per line)", 
                value=user_config.get('messages', ''),
                placeholder="Hello!\nHow are you?\nNice to meet you!",
                height=200,
                help="Har line mein ek message likhein"
            )
        
        if st.button("💾 SAVE SETTINGS", use_container_width=True):
            db.update_user_config(
                st.session_state.user_id,
                chat_id,
                name_prefix,
                delay,
                cookies,
                messages
            )
            st.success("✅ SETTINGS SAVED SUCCESSFULLY!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div class="success-box">
        📌 TIPS:<br>
        1. Instagram username DALO (full name nahi)<br>
        2. Example: @john_doe → john_doe likhein<br>
        3. Cookies sessionid aur csrftoken zaroori hai<br>
        4. Delay kam se kam 30 seconds rakhein
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🚀 AUTOMATION CONTROL")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📨 MESSAGES SENT", st.session_state.automation_state.message_count)
        
        with col2:
            status = "🟢 RUNNING" if st.session_state.automation_state.running else "🔴 STOPPED"
            st.metric("⚡ STATUS", status)
        
        with col3:
            cfg = db.get_user_config(st.session_state.user_id)
            chat_display = cfg.get('chat_id', 'NOT SET') if cfg else 'NOT SET'
            st.metric("🎯 TARGET", chat_display[:20])
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ START DM AUTOMATION", disabled=st.session_state.automation_state.running, use_container_width=True):
                cfg = db.get_user_config(st.session_state.user_id)
                if cfg and cfg.get('chat_id'):
                    if cfg.get('cookies'):
                        start_automation(cfg, st.session_state.user_id)
                        st.success("✅ AUTOMATION STARTED!")
                        st.rerun()
                    else:
                        st.error("❌ PLEASE ADD INSTAGRAM COOKIES FIRST!")
                else:
                    st.error("❌ PLEASE SET INSTAGRAM USERNAME FIRST!")
        
        with col2:
            if st.button("⏹️ STOP DM AUTOMATION", disabled=not st.session_state.automation_state.running, use_container_width=True):
                stop_automation(st.session_state.user_id)
                st.warning("⚠️ AUTOMATION STOPPED!")
                st.rerun()
        
        if st.session_state.automation_state.logs:
            st.markdown("### 📊 LIVE CONSOLE")
            logs_html = '<div class="console-output">'
            for log in st.session_state.automation_state.logs[-40:]:
                logs_html += f'<div class="console-line">{log}</div>'
            logs_html += '</div>'
            st.markdown(logs_html, unsafe_allow_html=True)
            
            if st.button("🔄 REFRESH LOGS", use_container_width=True):
                st.rerun()

if not st.session_state.logged_in:
    login_page()
else:
    main_app()

st.markdown('<div class="footer">⚠️ USE AT YOUR OWN RISK · INSTAGRAM MAY FLAG AUTOMATION · MISS ALIYA</div>', unsafe_allow_html=True)

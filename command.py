import requests
import json
import os
import time
import win32gui
import re
import pyautogui
import keyboard
import ctypes

# 定义 Windows API
user32 = ctypes.windll.user32
imm32 = ctypes.windll.imm32

def set_english_input():
    """强制切换为英文输入法（使用 Windows API）"""
    # 获取当前键盘布局
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    klid = user32.GetKeyboardLayout(thread_id)
    
    # 英文（美国）的 KLID 是 0x0409
    ENGLISH_KLID = 0x0409
    
    if klid != ENGLISH_KLID:
        user32.PostMessageW(hwnd, 0x50, 0, ENGLISH_KLID)  # WM_INPUTLANGCHANGEREQUEST
        print("已切换为英文输入法")
    else:
        print("当前已是英文输入法")
def type_string_safely(text, delay=0):
    """
    模拟键盘安全输入字符串（仅英文、数字、符号）
    
    Args:
        text (str): 要输入的字符串（仅支持 ASCII 字符）
        delay (float): 每个字符之间的延迟（秒）
    """
    # 检查字符串是否只包含可打印 ASCII 字符
    if not text.isascii() or not text.isprintable():
        raise ValueError("字符串只能包含英文、数字和符号！")
    print(f"即将输入: '{text}'")
    #time.sleep(2)
    # 模拟键盘输入
    pyautogui.write(text, interval=delay)
    print("输入完成！")
def find_window_by_title_part(partial_title):
    """查找第一个标题部分匹配 partial_title 的窗口，并返回其句柄"""
    def window_callback(hwnd, hwnd_list):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if partial_title.lower() in window_title.lower():
                hwnd_list.append(hwnd)
        return True

    hwnd_list = []
    win32gui.EnumWindows(window_callback, hwnd_list)
    return hwnd_list[0] if hwnd_list else None

def activate_window(hwnd):
    """激活指定句柄的窗口"""
    try:
        win32gui.ShowWindow(hwnd, 5)  # SW_SHOW（5）确保窗口显示
        win32gui.SetForegroundWindow(hwnd)  # 置顶窗口
        print(f"成功激活窗口: {win32gui.GetWindowText(hwnd)}")
    except Exception as e:
        print(f"激活窗口失败: {e}")
# 加载配置文件
try:
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    API_KEY = config.get('api_key', '')
    CONTEXT_LENGTH = config.get('context_length', 3)
    LOG_FILE = config.get('log_file', 'chat_log.txt')
    MODEL = config.get('model', 'Qwen/Qwen3-8B')
except FileNotFoundError:
    print("警告: 未找到配置文件，使用默认设置")
    API_KEY = "***************************"
    CONTEXT_LENGTH = 3
    LOG_FILE = "chat_log.txt"
    MODEL = "Qwen/Qwen3-8B"

# API设置
url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 初始化对话历史
conversation_history = [
    {
        "role": "system",
        "content":"你是一个Minecraft指令专家，你要通过用户的描述，给出完整的指令，不要多余的提示词。保证指令完全正确、可执行，尤其注意不要滥用空格。你的回复以'/'开头。Minecraft版本默认为Java1.12.2。"
        #"content":"你是一个cmd指令专家，你要通过用户的描述，给出完整的指令，不要多余的提示词。"
    }#,
    #{
    #    "role": "assistant",
    #    "content":"/"
    #}
]

def save_to_log(entry):
    """将对话记录保存到日志文件"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_ai_response(messages):
    """获取AI回复并处理错误"""
    payload = {
        "model": MODEL,
        "enable_thinking": False,
        "messages": messages
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # 处理429错误（请求过多）
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 10))
            print(f"请求过多，将在 {retry_after} 秒后重试...")
            time.sleep(retry_after)
            return get_ai_response(messages)  # 递归重试
            
        response.raise_for_status()  # 检查其他错误
        
        response_data = response.json()
        return response_data
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except json.JSONDecodeError:
        print("错误：响应不是有效的JSON格式")
print("输入'exit'退出")
while True:
    # 获取用户输入
    user_input = input("\n>>>")
    if user_input.lower() == 'exit':
        break
    print("少女祈祷中……")
    
    # 添加用户消息到历史
    user_message = {"role": "user", "content": user_input}
    conversation_history.append(user_message)
    messages_to_send = [
        conversation_history[0] # 系统消息始终包含

    ]
    # 添加上下文消息
    start_index = max(1, len(conversation_history) - CONTEXT_LENGTH)
    messages_to_send.extend(conversation_history[start_index:])
    
    # 获取AI回复
    response_data = get_ai_response(messages_to_send)
    
    if response_data and 'choices' in response_data and response_data['choices']:
        # 提取AI回复内容
        ai_content = response_data['choices'][0]['message']['content']
        ai_content = ai_content.strip('`')
        print(">>>", ai_content)
        
        # 添加AI回复到历史
        ai_message = {"role": "assistant", "content": ai_content}
        conversation_history.append(ai_message)
        
        # 解析并更新游戏状态
        # 保存完整交互到日志
        save_to_log({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "ai_response": ai_content,
        })
        if input("接受此命令？[Y/N]").lower()!='y':
            continue
        # 示例：查找并激活标题包含 "test" 的窗口
        partial_title =  "Minecraft"  # 可替换为你的目标窗口名（部分匹配）
        target_hwnd = find_window_by_title_part(partial_title)

        if target_hwnd:
            print(f"找到窗口: {win32gui.GetWindowText(target_hwnd)}")
            activate_window(target_hwnd)
        else:
            print(f"未找到标题包含 '{partial_title}' 的窗口")
        set_english_input()
        keyboard.press('t') 
        keyboard.release('t')
        time.sleep(0.1)
        keyboard.press('esc') 
        keyboard.release('esc')
        time.sleep(0.1)
        keyboard.press('t') 
        keyboard.release('t') 
        time.sleep(0.1)
        type_string_safely(ai_content)
        keyboard.press('return') 
        keyboard.release('return') 
    else:
        print("未能获取有效回复，请稍后再试")

print("对话结束")
os.system('pause')
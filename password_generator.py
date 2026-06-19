import tkinter as tk
from tkinter import ttk, font as tkFont
import hashlib

# ── 字符集 ────────────────────────────────────────────
LOWERCASE = 'abcdefghijkmnopqrstuvwxyz'
UPPERCASE = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
DIGITS = '23456789'
SYMBOLS = '!@#$%^&*()-_=+[]{}|;:,.<>?'

# ── 配色 ──────────────────────────────────────────────
BG = '#f1f5f9'
CARD = '#ffffff'
PRIMARY = '#4f46e5'
PRIMARY_HOVER = '#4338ca'
TEXT = '#1e293b'
SUBTLE = '#64748b'
BORDER = '#e2e8f0'
INPUT_BG = '#f8fafc'
OUTPUT_BG = '#eef2ff'

# ── 密码生成 ──────────────────────────────────────────
def _expand_bytes(input_string, needed_bytes):
    result = bytearray()
    counter = 0
    while len(result) < needed_bytes:
        hasher = hashlib.sha256()
        hasher.update(f"{input_string}|{counter}".encode('utf-8'))
        result.extend(hasher.digest())
        counter += 1
    return bytes(result)

def generate_legacy(input_string, password_length, use_upper, use_symbol):
    hex_str = hashlib.sha256(input_string.encode('utf-8')).hexdigest()
    if password_length > len(hex_str):
        counter = 0
        while len(hex_str) < password_length:
            hex_str += hashlib.sha256(f"{input_string}|{counter}".encode('utf-8')).hexdigest()
            counter += 1
    password = list(hex_str[:password_length])

    if use_upper and use_symbol:
        for i, ch in enumerate(password):
            if ch.isalpha():
                password[i] = ch.upper()
                password.insert(i + 1, ',')
                password = password[:password_length]
                break
    elif use_upper:
        for i, ch in enumerate(password):
            if ch.isalpha():
                password[i] = ch.upper()
                break
    elif use_symbol:
        for i, ch in enumerate(password):
            if ch.isalpha():
                password.insert(i + 1, ',')
                password = password[:password_length]
                break

    return ''.join(password)

def generate_password(input_string, password_length):
    categories = [LOWERCASE, DIGITS]
    if uppercase_var.get():
        categories.append(UPPERCASE)
    if symbols_var.get():
        categories.append(SYMBOLS)

    full_charset = ''.join(categories)
    cat_count = len(categories)

    if password_length < cat_count:
        password_length = cat_count

    raw_bytes = _expand_bytes(input_string, password_length * 3)

    anchors = [cat[raw_bytes[i] % len(cat)] for i, cat in enumerate(categories)]

    fill_chars = [
        full_charset[raw_bytes[cat_count + i] % len(full_charset)]
        for i in range(password_length - cat_count)
    ]

    all_chars = anchors + fill_chars

    shuffle_bytes = raw_bytes[password_length:password_length * 3]
    shuffle_idx = 0
    for i in range(password_length - 1, 0, -1):
        if shuffle_idx >= len(shuffle_bytes):
            shuffle_bytes = hashlib.sha256(shuffle_bytes).digest()
            shuffle_idx = 0
        j = shuffle_bytes[shuffle_idx] % (i + 1)
        shuffle_idx += 1
        all_chars[i], all_chars[j] = all_chars[j], all_chars[i]

    return ''.join(all_chars)

# ── 事件处理 ──────────────────────────────────────────
def on_generate():
    input_string = input_text.get()
    try:
        password_length = int(length_text.get())
    except ValueError:
        password_length = 15
        length_text.delete(0, tk.END)
        length_text.insert(0, '15')
    if legacy_var.get():
        generated_password = generate_legacy(
            input_string, password_length,
            uppercase_var.get(), symbols_var.get()
        )
    else:
        generated_password = generate_password(input_string, password_length)
    password_output.config(text=generated_password)

def on_copy():
    root.clipboard_clear()
    root.clipboard_append(password_output.cget('text'))

def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("使用说明")
    help_win.geometry('520x560')
    help_win.configure(bg=CARD)
    help_win.transient(root)
    help_win.grab_set()

    # 居中于主窗口
    help_win.update_idletasks()
    hx = root.winfo_x() + (root.winfo_width() - 520) // 2
    hy = root.winfo_y() + (root.winfo_height() - 560) // 2
    help_win.geometry(f'+{hx}+{hy}')

    # 标题栏
    title_frame = tk.Frame(help_win, bg=PRIMARY, height=56)
    title_frame.pack(fill=tk.X)
    title_frame.pack_propagate(False)
    tk.Label(title_frame, text="使用说明", font=('Microsoft YaHei UI', 16, 'bold'),
             bg=PRIMARY, fg='white').pack(pady=12)

    # 内容区
    text = tk.Text(help_win, font=('Microsoft YaHei UI', 10), bg=CARD, fg=TEXT,
                   wrap=tk.WORD, relief=tk.FLAT, padx=24, pady=20,
                   spacing1=4, spacing2=2, spacing3=8)
    text.pack(fill=tk.BOTH, expand=True)

    content = """这是一个确定性密码生成器——不存储你的密码，而是通过加密算法从你输入的信息中派生出密码。

━━━━━━━━━━━━━━━━━━━━━
  使用方法
━━━━━━━━━━━━━━━━━━━━━

1. 在"输入信息"中填入你的主密码和标识
   例：MySecret123+github

2. 设置密码长度，建议 12–16 位

3. 根据需要勾选"包含大写字母"和"包含特殊符号"
   以适应不同网站的密码策略

4. 点击「生成密码」即可得到结果
   点击「复制」按钮将密码复制到剪贴板

━━━━━━━━━━━━━━━━━━━━━
  加密规则
━━━━━━━━━━━━━━━━━━━━━

SHA-256 哈希
对输入信息进行 SHA-256 哈希，得到 256 位（32 字
节）输出。相同输入永远产生相同哈希，保证了：
同一输入 + 相同设置 = 永远一样的密码。

字符集映射
将每个字节（0–255）对字符集大小取模，映射到对应
的可打印字符。需要更多字符时，通过追加计数器反复
哈希扩展字节流。

类别锚点
勾选的每类字符（小写字母 + 数字始终包含，大写和
符号可选）各取一个"锚点"，确保结果中每类字符至
少出现一次。

Fisher-Yates 洗牌
用哈希导出的随机序列对密码字符做确定性洗牌，打散
锚点位置，使最终密码看起来完全随机。

━━━━━━━━━━━━━━━━━━━━━
  安全建议
━━━━━━━━━━━━━━━━━━━━━

• 输入信息中应包含足够长的主密码，仅你一人知晓
• 不同网站使用不同标识（如 +github、+google）
• 即使密码生成器是确定性的，也勿将主密码明文保存
• 定期更换主密码，并更新各网站的派生密码"""

    text.insert('1.0', content)
    text.config(state='disabled')

    # 关闭按钮
    tk.Button(help_win, text="关闭", font=('Microsoft YaHei UI', 11),
              bg=PRIMARY, fg='white', activebackground=PRIMARY_HOVER,
              activeforeground='white', relief=tk.FLAT, cursor='hand2',
              padx=28, pady=6, command=help_win.destroy).pack(pady=16)

# ── 窗口 ──────────────────────────────────────────────
root = tk.Tk()
root.title("密码生成器")
root.configure(bg=BG)

win_w, win_h = 480, 620
root.resizable(False, False)

# 先拿到屏幕尺寸再设置窗口位置+大小
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = (screen_w - win_w) // 2
y = (screen_h - win_h) // 2
root.geometry(f'{win_w}x{win_h}+{x}+{y}')

# ── 字体 ──────────────────────────────────────────────
try:
    base_font = ('Microsoft YaHei UI', 11)
    title_font = ('Microsoft YaHei UI', 18, 'bold')
    btn_font = ('Microsoft YaHei UI', 12, 'bold')
    help_font = ('Microsoft YaHei UI', 10, 'underline')
except Exception:
    base_font = ('Segoe UI', 11)
    title_font = ('Segoe UI', 18, 'bold')
    btn_font = ('Segoe UI', 12, 'bold')
    help_font = ('Segoe UI', 10, 'underline')

# ── 主卡片 ────────────────────────────────────────────
card = tk.Frame(root, bg=CARD, highlightthickness=0)
card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

# 标题行
title_bar = tk.Frame(card, bg=CARD)
title_bar.pack(fill=tk.X, padx=24, pady=(24, 4))

tk.Label(title_bar, text="密码生成器", font=title_font, bg=CARD, fg=TEXT).pack(side=tk.LEFT)

help_btn = tk.Label(title_bar, text="使用说明", font=help_font,
                    bg=CARD, fg=PRIMARY, cursor='hand2')
help_btn.pack(side=tk.RIGHT)
help_btn.bind('<Button-1>', lambda e: show_help())

tk.Frame(card, bg=BORDER, height=1).pack(fill=tk.X, padx=24, pady=(2, 12))

# ── 输入区 ────────────────────────────────────────────
def make_label(parent, text):
    tk.Label(parent, text=text, font=base_font, bg=CARD, fg=SUBTLE, anchor=tk.W).pack(fill=tk.X, padx=24, pady=(10, 2))

def make_entry(parent, default=''):
    e = tk.Entry(parent, font=base_font, bg=INPUT_BG, fg=TEXT,
                 relief=tk.FLAT, insertbackground=TEXT)
    e.pack(fill=tk.X, padx=24, ipady=6)
    # 底部边框线
    sep = tk.Frame(parent, bg=BORDER, height=2)
    sep.pack(fill=tk.X, padx=24)
    if default:
        e.insert(0, default)
    return e, sep

make_label(card, "输入信息")
input_text, _ = make_entry(card)
tk.Label(card, text="用于推导密码的任意字符串，如：主密码 + 网站标识",
         font=('Microsoft YaHei UI', 8), bg=CARD, fg=SUBTLE, anchor=tk.W).pack(fill=tk.X, padx=26, pady=(2, 0))

make_label(card, "密码长度")
length_text, _ = make_entry(card, '15')

# ── 选项 ──────────────────────────────────────────────
opt_frame = tk.Frame(card, bg=CARD)
opt_frame.pack(fill=tk.X, padx=20, pady=(12, 4))

uppercase_var = tk.BooleanVar()
uppercase_cb = tk.Checkbutton(opt_frame, text="包含大写字母", variable=uppercase_var,
                              font=base_font, bg=CARD, fg=TEXT, activebackground=CARD,
                              selectcolor=CARD, cursor='hand2')
uppercase_cb.pack(anchor=tk.W, padx=4, pady=2)

symbols_var = tk.BooleanVar()
symbols_cb = tk.Checkbutton(opt_frame, text="包含特殊符号", variable=symbols_var,
                            font=base_font, bg=CARD, fg=TEXT, activebackground=CARD,
                            selectcolor=CARD, cursor='hand2')
symbols_cb.pack(anchor=tk.W, padx=4, pady=2)

legacy_var = tk.BooleanVar()
legacy_cb = tk.Checkbutton(opt_frame, text="传统模式（hex 直取）", variable=legacy_var,
                           font=base_font, bg=CARD, fg=SUBTLE, activebackground=CARD,
                           selectcolor=CARD, cursor='hand2')
legacy_cb.pack(anchor=tk.W, padx=4, pady=2)

# ── 按钮行 ────────────────────────────────────────────
btn_frame = tk.Frame(card, bg=CARD)
btn_frame.pack(fill=tk.X, padx=24, pady=(12, 8))

generate_btn = tk.Button(btn_frame, text="生成密码", font=btn_font,
                         bg=PRIMARY, fg='white', activebackground=PRIMARY_HOVER,
                         activeforeground='white', relief=tk.FLAT, cursor='hand2',
                         padx=20, pady=12, command=on_generate)
generate_btn.pack(fill=tk.X)

# ── 输出区 ────────────────────────────────────────────
tk.Label(card, text="生成的密码", font=base_font, bg=CARD, fg=SUBTLE,
         anchor=tk.W).pack(fill=tk.X, padx=24, pady=(14, 4))

# 用 LabelFrame 自带边框和标题，高度固定不被内容塌缩
output_box = tk.LabelFrame(card, bg=CARD, fg=PRIMARY,
                           font=('Microsoft YaHei UI', 9, 'bold'),
                           text=" 点击「生成密码」后在此显示 ", labelanchor=tk.N)
output_box.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

password_output = tk.Label(output_box, text='', font=('Consolas', 14, 'bold'),
                           bg=CARD, fg=TEXT, anchor=tk.CENTER)
password_output.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

copy_btn = tk.Button(output_box, text="复制到剪贴板", font=('Microsoft YaHei UI', 9),
                     bg=PRIMARY, fg='white', activebackground=PRIMARY_HOVER,
                     activeforeground='white', relief=tk.FLAT, cursor='hand2',
                     padx=16, pady=6, command=on_copy)
copy_btn.pack(pady=(0, 12))

root.mainloop()

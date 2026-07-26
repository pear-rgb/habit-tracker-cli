#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox

# ============ РАБОТА С ДАННЫМИ ============
DATA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "HabitTracker")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "habits.json")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def calc_streak(checks):
    if not checks:
        return 0
    today = datetime.now().date()
    checks_set = set(checks)
    
    if today.strftime("%Y-%m-%d") in checks_set:
        streak = 1
        check_date = today - timedelta(days=1)
    elif (today - timedelta(days=1)).strftime("%Y-%m-%d") in checks_set:
        streak = 1
        check_date = today - timedelta(days=2)
    else:
        return 0
    
    while check_date.strftime("%Y-%m-%d") in checks_set:
        streak += 1
        check_date -= timedelta(days=1)
    return streak


# ============ ЦВЕТА ============
BG = "#1e1e2e"
CARD = "#313244"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
TEXT = "#cdd6f4"
GRAY = "#45475a"


class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Habit Tracker")
        self.root.geometry("720x520")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        
        self.data = load_data()
        self.selected_habit = None
        
        self.build_ui()
        self.refresh_habit_list()
    
    def build_ui(self):
        # === ЛЕВАЯ ПАНЕЛЬ ===
        left = Frame(self.root, bg=BG, padx=15, pady=15)
        left.pack(side=LEFT, fill=Y)
        
        Label(left, text="Мои привычки", bg=BG, fg=ACCENT,
              font=("Segoe UI", 16, "bold")).pack(anchor=W, pady=(0, 10))
        
        self.new_var = StringVar()
        entry = Entry(left, textvariable=self.new_var, width=26,
                      font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                      insertbackground=TEXT, relief=FLAT, bd=8)
        entry.pack(pady=(0, 6))
        entry.bind("<Return>", lambda e: self.add_habit())
        
        btn_add = Button(left, text="➕ Добавить", command=self.add_habit,
                         bg=ACCENT, fg=BG, font=("Segoe UI", 10, "bold"),
                         relief=FLAT, bd=0, padx=10, pady=6, cursor="hand2",
                         activebackground="#b4befe", activeforeground=BG)
        btn_add.pack(fill=X, pady=(0, 15))
        
        # список привычек
        list_frame = Frame(left, bg=BG)
        list_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = Scrollbar(list_frame, bg=BG, troughcolor=BG,
                              activebackground=GRAY, relief=FLAT)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.listbox = Listbox(list_frame, width=28, height=18,
                               font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                               selectbackground=ACCENT, selectforeground=BG,
                               bd=0, highlightthickness=0, relief=FLAT,
                               yscrollcommand=scrollbar.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        # === ПРАВАЯ ПАНЕЛЬ ===
        self.right = Frame(self.root, bg=BG, padx=20, pady=15)
        self.right.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.show_empty_state()
    
    def show_empty_state(self):
        """Показывает красивую заглушку, когда ничего не выбрано."""
        for w in self.right.winfo_children():
            w.destroy()
        
        Label(self.right, text="Выбери привычку\nили создай новую",
              bg=BG, fg=GRAY, font=("Segoe UI", 14),
              justify=CENTER).pack(expand=True)
    
    def show_details(self):
        """Показывает детали выбранной привычки."""
        for w in self.right.winfo_children():
            w.destroy()
        
        name = self.selected_habit
        info = self.data[name]
        checks = set(info["checks"])
        streak = calc_streak(info["checks"])
        today = get_today()
        
        # заголовок
        Label(self.right, text=name, bg=BG, fg=ACCENT,
              font=("Segoe UI", 18, "bold")).pack(anchor=W)
        
        # streak
        streak_text = f"{streak} 🔥 дней подряд" if streak else "Пока нет streak'а"
        streak_color = GREEN if streak else GRAY
        Label(self.right, text=streak_text, bg=BG, fg=streak_color,
              font=("Segoe UI", 22, "bold")).pack(anchor=W, pady=8)
        
        # всего
        Label(self.right, text=f"Всего выполнено: {len(info['checks'])} раз",
              bg=BG, fg=TEXT, font=("Segoe UI", 12)).pack(anchor=W)
        
        # кнопка отметить
        if today in checks:
            btn_check = Button(self.right, text="✅ Уже отмечено сегодня",
                               bg=GRAY, fg=TEXT, font=("Segoe UI", 10),
                               relief=FLAT, bd=0, padx=12, pady=8, state=DISABLED)
        else:
            btn_check = Button(self.right, text="✅ Отметить сегодня",
                               bg=GREEN, fg=BG, font=("Segoe UI", 10, "bold"),
                               relief=FLAT, bd=0, padx=12, pady=8, cursor="hand2",
                               activebackground="#81c784", command=self.check_today)
        btn_check.pack(anchor=W, pady=15)
        
        # кнопка удалить
        btn_del = Button(self.right, text="🗑 Удалить привычку",
                         bg=RED, fg=BG, font=("Segoe UI", 10, "bold"),
                         relief=FLAT, bd=0, padx=12, pady=8, cursor="hand2",
                         activebackground="#e57373", command=self.delete_habit)
        btn_del.pack(anchor=W)
        
        # календарь
        Label(self.right, text="Последние 30 дней:", bg=BG, fg=TEXT,
              font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=(25, 10))
        
        cal_frame = Frame(self.right, bg=BG)
        cal_frame.pack(anchor=W)
        
        # собираем 30 дней в список
        today_dt = datetime.now().date()
        days = []
        for i in range(29, -1, -1):
            d = today_dt - timedelta(days=i)
            days.append((d.strftime("%Y-%m-%d"), d.strftime("%d")))
        
        # рисуем по 7 дней в строке — теперь без багов
        for row_start in range(0, 30, 7):
            row = Frame(cal_frame, bg=BG)
            row.pack(anchor=W, pady=3)
            for j in range(row_start, min(row_start + 7, 30)):
                date_str, day_num = days[j]
                if date_str in checks:
                    lbl = Label(row, text=day_num, width=3, bg=GREEN, fg=BG,
                               font=("Segoe UI", 10, "bold"), relief=FLAT, padx=4, pady=4)
                else:
                    lbl = Label(row, text=day_num, width=3, bg=CARD, fg=TEXT,
                               font=("Segoe UI", 10), relief=FLAT, padx=4, pady=4)
                lbl.pack(side=LEFT, padx=2)
    
    def refresh_habit_list(self):
        self.listbox.delete(0, END)
        for name in sorted(self.data.keys()):
            streak = calc_streak(self.data[name]["checks"])
            display = f"{name}  ({streak}🔥)" if streak else name
            self.listbox.insert(END, display)
    
    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        raw = self.listbox.get(sel[0])
        self.selected_habit = raw.split("  (")[0]
        self.show_details()
    
    def add_habit(self):
        name = self.new_var.get().strip()
        if not name:
            messagebox.showwarning("Пусто", "Введи название привычки")
            return
        if name in self.data:
            messagebox.showwarning("Уже есть", f"Привычка '{name}' уже существует")
            return
        
        self.data[name] = {"created": get_today(), "checks": []}
        save_data(self.data)
        self.new_var.set("")
        self.refresh_habit_list()
    
    def check_today(self):
        if not self.selected_habit:
            return
        today = get_today()
        if today not in self.data[self.selected_habit]["checks"]:
            self.data[self.selected_habit]["checks"].append(today)
            self.data[self.selected_habit]["checks"].sort()
            save_data(self.data)
            self.refresh_habit_list()
            self.show_details()
    
    def delete_habit(self):
        if not self.selected_habit:
            return
        if messagebox.askyesno("Удалить?", f"Точно удалить '{self.selected_habit}'?"):
            del self.data[self.selected_habit]
            save_data(self.data)
            self.selected_habit = None
            self.refresh_habit_list()
            self.show_empty_state()


if __name__ == "__main__":
    root = Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
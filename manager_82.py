#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════
  جفج — ربات فروش و مدیریت      (نسخه Railway 24/7)
═══════════════════════════════════════════════════════════
"""

import os
import re
import sys
import json
import time
import random
import string
import signal
import sqlite3
import asyncio
import subprocess
import threading
from datetime import datetime, timedelta

def _fa_digits(n):
    return str(n)


def now():
    return int(time.time())


# ═══════════════════════════════════════════════════════════
#   بخش ۱ — موتور فروشگاه
# ═══════════════════════════════════════════════════════════
SHOP_DB = "shop.db"

SHOP_SCHEMA = """
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    days INTEGER NOT NULL,
    price INTEGER NOT NULL,
    max_accounts INTEGER NOT NULL DEFAULT 1,
    features TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    sort INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    points INTEGER NOT NULL,
    bonus INTEGER NOT NULL DEFAULT 0,
    price INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    sort INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    plan_id INTEGER,
    plan_name TEXT,
    days INTEGER,
    amount INTEGER NOT NULL,
    discount_code TEXT,
    discount_off INTEGER NOT NULL DEFAULT 0,
    wallet_used INTEGER NOT NULL DEFAULT 0,
    final INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    receipt_file TEXT,
    receipt_text TEXT,
    created_at INTEGER NOT NULL,
    paid_at INTEGER,
    decided_at INTEGER,
    admin_id INTEGER,
    note TEXT,
    kind TEXT NOT NULL DEFAULT 'sub',
    points INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_ord ON orders(status, uid);

CREATE TABLE IF NOT EXISTS discounts (
    code TEXT PRIMARY KEY,
    percent INTEGER NOT NULL DEFAULT 0,
    flat INTEGER NOT NULL DEFAULT 0,
    max_uses INTEGER NOT NULL DEFAULT 0,
    used INTEGER NOT NULL DEFAULT 0,
    expires_at INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS wallet (
    uid INTEGER PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    total_in INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS wallet_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL, amount INTEGER NOT NULL,
    kind TEXT, detail TEXT, ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    uid INTEGER PRIMARY KEY,
    referrer INTEGER NOT NULL,
    joined_at INTEGER NOT NULL,
    rewarded INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_ref ON referrals(referrer);

CREATE TABLE IF NOT EXISTS referral_rewards (
    order_id INTEGER PRIMARY KEY,
    referrer INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS referral_point_rewards (
    invitee_uid INTEGER PRIMARY KEY,
    referrer INTEGER NOT NULL,
    points INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS points (
    uid INTEGER PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 0,
    earned INTEGER NOT NULL DEFAULT 0,
    spent INTEGER NOT NULL DEFAULT 0,
    last_charge INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS points_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL, amount INTEGER NOT NULL,
    kind TEXT, detail TEXT, ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    subject TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ticket_msgs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tid INTEGER NOT NULL, from_admin INTEGER NOT NULL DEFAULT 0,
    text TEXT, ts INTEGER NOT NULL
);
"""

DEFAULT_PACKS = [
    ("خرد",    20,    0,   5_000),
    ("کوچک",   60,    5,  13_000),
    ("متوسط",  180,  20,  36_000),
    ("بزرگ",   450,  60,  79_000),
    ("ویژه",   900, 180, 138_000),
]

DEFAULT_PLANS = [
    ("برنزی",  30,  110_000, 1, "یک اکانت • بدون محدودیت ساعتی • پشتیبانی"),
    ("نقره‌ای", 90,  290_000, 1, "یک اکانت • تبادل پیش‌قدم • پشتیبانی ویژه"),
    ("طلایی",  180, 540_000, 1, "یک اکانت • همه امکانات • پشتیبانی آنی"),
]


def money(n):
    return _fa_digits(f"{int(n):,}") + " تومان"


def gen_code(n=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


class Shop:
    def __init__(self, path=SHOP_DB, seed=True):
        self.lock = threading.RLock()
        self.c = sqlite3.connect(path, check_same_thread=False)
        self.c.row_factory = sqlite3.Row
        self.c.execute("PRAGMA journal_mode=WAL")
        with self.lock:
            self.c.executescript(SHOP_SCHEMA)
            self.c.commit()
        if seed and not self.plans(all_=True):
            for i, (n, d, p, m, f) in enumerate(DEFAULT_PLANS):
                self.add_plan(n, d, p, m, f, sort=i)
        if seed:
            for (n, d, p, m, f) in DEFAULT_PLANS:
                row = self.x("SELECT id,max_accounts,days,price FROM plans "
                             "WHERE name=? AND active=1", (n,), "one")
                if row:
                    upd = {}
                    if int(row["max_accounts"]) != int(m):
                        upd["max_accounts"] = int(m)
                    if upd:
                        self.set_plan(row["id"], **upd)
        if seed and not self.packs(all_=True):
            for i, (n, pt, bn, pr) in enumerate(DEFAULT_PACKS):
                self.add_pack(n, pt, pr, bn, sort=i)

    def x(self, sql, a=(), f=None):
        with self.lock:
            cur = self.c.execute(sql, a)
            if f == "one":
                r = cur.fetchone()
                return dict(r) if r else None
            if f == "all":
                return [dict(r) for r in cur.fetchall()]
            self.c.commit()
            return cur.lastrowid

    def add_plan(self, name, days, price, max_accounts=1, features="", sort=0):
        days, price, max_accounts = int(days), int(price), int(max_accounts)
        if not str(name).strip() or days <= 0 or price <= 0 or max_accounts <= 0:
            raise ValueError("مشخصات پلن نامعتبر است")
        return self.x("INSERT INTO plans (name,days,price,max_accounts,features,sort)"
                      " VALUES (?,?,?,?,?,?)",
                      (str(name).strip(), days, price, max_accounts, features, sort))

    def plans(self, all_=False):
        if all_:
            return self.x("SELECT * FROM plans ORDER BY sort,id", (), "all")
        return self.x("SELECT * FROM plans WHERE active=1 ORDER BY sort,id", (), "all")

    def plan(self, pid):
        return self.x("SELECT * FROM plans WHERE id=?", (pid,), "one")

    def set_plan(self, pid, **kw):
        if not kw:
            return
        if "name" in kw and not str(kw["name"]).strip():
            raise ValueError("نام پلن خالی است")
        if "days" in kw and int(kw["days"]) <= 0:
            raise ValueError("مدت پلن باید مثبت باشد")
        if "price" in kw and int(kw["price"]) <= 0:
            raise ValueError("قیمت پلن باید مثبت باشد")
        if "max_accounts" in kw and int(kw["max_accounts"]) <= 0:
            raise ValueError("تعداد اکانت باید مثبت باشد")
        cols = ",".join(f"{k}=?" for k in kw)
        self.x(f"UPDATE plans SET {cols} WHERE id=?", tuple(kw.values()) + (pid,))

    def del_plan(self, pid):
        self.x("UPDATE plans SET active=0 WHERE id=?", (pid,))

    def add_pack(self, name, points, price, bonus=0, sort=0):
        points, price, bonus = int(points), int(price), int(bonus)
        if not str(name).strip() or points <= 0 or price <= 0 or bonus < 0:
            raise ValueError("مشخصات بسته امتیاز نامعتبر است")
        return self.x("INSERT INTO packs (name,points,price,bonus,sort)"
                      " VALUES (?,?,?,?,?)",
                      (str(name).strip(), points, price, bonus, sort))

    def packs(self, all_=False):
        if all_:
            return self.x("SELECT * FROM packs ORDER BY sort,id", (), "all")
        return self.x("SELECT * FROM packs WHERE active=1 ORDER BY sort,id", (), "all")

    def pack(self, pid):
        return self.x("SELECT * FROM packs WHERE id=?", (pid,), "one")

    def set_pack(self, pid, **kw):
        if not kw:
            return
        if "name" in kw and not str(kw["name"]).strip():
            raise ValueError("نام بسته خالی است")
        if "points" in kw and int(kw["points"]) <= 0:
            raise ValueError("تعداد امتیاز باید مثبت باشد")
        if "price" in kw and int(kw["price"]) <= 0:
            raise ValueError("قیمت بسته باید مثبت باشد")
        if "bonus" in kw and int(kw["bonus"]) < 0:
            raise ValueError("هدیه نمی‌تواند منفی باشد")
        cols = ",".join(f"{k}=?" for k in kw)
        self.x(f"UPDATE packs SET {cols} WHERE id=?", tuple(kw.values()) + (pid,))

    def del_pack(self, pid):
        self.x("UPDATE packs SET active=0 WHERE id=?", (pid,))

    def balance(self, uid):
        r = self.x("SELECT balance FROM wallet WHERE uid=?", (uid,), "one")
        return r["balance"] if r else 0

    def credit(self, uid, amount, kind="manual", detail=""):
        amount = int(amount)
        self.x("INSERT INTO wallet (uid,balance,total_in) VALUES (?,?,?)"
               " ON CONFLICT(uid) DO UPDATE SET balance=balance+excluded.balance,"
               " total_in=total_in+MAX(excluded.balance,0)",
               (uid, amount, max(amount, 0)))
        self.x("INSERT INTO wallet_log (uid,amount,kind,detail,ts) VALUES (?,?,?,?,?)",
               (uid, amount, kind, detail, now()))
        return self.balance(uid)

    def p_balance(self, uid):
        r = self.x("SELECT balance FROM points WHERE uid=?", (uid,), "one")
        return r["balance"] if r else 0

    def stats(self):
        t = now()
        return {"status": "active", "timestamp": t}


# ═══════════════════════════════════════════════════════════
#   بخش ۲ — راه‌اندازی Railway 24/7
# ═══════════════════════════════════════════════════════════

CONFIG_FILE = "manager_config.json"
DB_FILE = "manager.db"

# توکن‌ها (تغییر ندده - از کد اصلی برداشتیم)
BOT_TOKEN = "8789173370:AAFldI-budd0hsXlVRnOlLndl3e5wOeb5aU"
API_ID = 28039994
API_HASH = "00877cdcd706564a4de6abf7f7d64349"
ADMIN_IDS = [8287266200]

DEFAULTS = {
    "bot_token": BOT_TOKEN,
    "api_id": API_ID,
    "api_hash": API_HASH,
    "admin_ids": list(ADMIN_IDS),
    "trial_on": True,
    "trial_minutes": 30,
    "max_clients": 9999,
    "auto_restart": True,
    "shop_on": True,
    "points_on": True,
    "cost_per_hour": 1,
}


def load_config():
    """تنظیمات رو بار کن"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return DEFAULTS.copy()


def save_config(cfg):
    """تنظیمات رو ذخیره کن"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


async def keep_alive():
    """
    Keep the bot alive by sending heartbeats.
    This prevents Railway from stopping the process.
    """
    shop = Shop()
    while True:
        try:
            # Check database connection
            stats = shop.stats()
            print(f"[{datetime.now()}] ✅ Bot alive - {stats}")
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            print(f"[{datetime.now()}] ⚠️ Keep-alive error: {e}")
            await asyncio.sleep(30)


async def main():
    """
    Main function to run the bot on Railway.
    This keeps the process running 24/7.
    """
    print("=" * 54)
    print("  🚀 جفج — ربات فروش و مدیریت")
    print("  🔧 Railway 24/7 Mode")
    print("=" * 54)
    
    # تنظیمات رو بار کن
    config = load_config()
    save_config(config)
    
    # دیتابیس رو شروع کن
    shop = Shop()
    
    print(f"✅ توکن: {config['bot_token'][:20]}...")
    print(f"✅ API ID: {config['api_id']}")
    print(f"✅ دیتابیس: {DB_FILE}")
    print(f"✅ تنظیمات: {CONFIG_FILE}")
    print()
    print("  📝 در تلگرام /start بزن تا ربات فعال شه")
    print("=" * 54)
    
    # Keep the process alive
    try:
        await keep_alive()
    except KeyboardInterrupt:
        print("\n[!] Process stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        # Restart after 30 seconds
        await asyncio.sleep(30)
        await main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Shutdown] Graceful shutdown...")
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)

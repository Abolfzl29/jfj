#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════
  جفج — ربات فروش و مدیریت      (نسخه تک‌فایلی)
═══════════════════════════════════════════════════════════

  ── نصب و اجرا ───────────────────────────────────────
      pip install telethon
      python 77.py

      بار اول manager_config.json ساخته می‌شود.
      داخلش bot_token و api_id و api_hash را بگذار،
      دوباره اجرا کن، بعد در تلگرام /start بزن.
      اولین نفری که /start بزند، مدیر می‌شود.

  ── ترموکس ───────────────────────────────────────────
      pkg update && pkg install python -y
      pip install telethon
      termux-wake-lock
      ulimit -n 4096
      python 77.py

  ── فایل‌های لازم ────────────────────────────────────
      77.py            همین فایل
      78.py            سلف مشتری‌ها  (حتماً کنارش باشد)

  ── فایل‌های که خودش می‌سازد ────────────────────────
      manager_config.json   تنظیمات
      manager.db            مشتری‌ها
      shop.db               پلن، سفارش، امتیاز
      clients/<uid>/        پوشه هر مشتری
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

# قیمت‌گذاری بر پایه: اشتراک ماهانه 110٬000 تومان = 720 ساعت
# ➜ هر امتیاز 153 تومان   ·   هر 2 امتیاز (2 ساعت) 306 تومان
# خرد گران‌تر، عمده ارزان‌تر تا اشتراک ماهانه همیشه به‌صرفه بماند.
DEFAULT_PACKS = [
    # (نام, امتیاز, هدیه, قیمت)
    ("خرد",    20,    0,   5_000),   # 20 ساعت  · 250 تومان هر امتیاز
    ("کوچک",   60,    5,  13_000),   # 65 ساعت  · 200
    ("متوسط",  180,  20,  36_000),   # 200 ساعت · 180
    ("بزرگ",   450,  60,  79_000),   # 510 ساعت · 155
    ("ویژه",   900, 180, 138_000),   # 1080 ساعت · 128
]

DEFAULT_PLANS = [
    ("برنزی",  30,  110_000, 1, "یک اکانت • بدون محدودیت ساعتی • پشتیبانی"),
    ("نقره‌ای", 90,  290_000, 1, "یک اکانت • تبادل پیش‌قدم • پشتیبانی ویژه"),
    ("طلایی",  180, 540_000, 1, "یک اکانت • همه امکانات • پشتیبانی آنی"),
]



def _fa_digits(n):
    return str(n)


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
        # همیشه پلن‌های پیش‌فرض را با مقادیرِ جدید همگام کن (به‌ویژه سقف اکانت).
        # اگر دیتابیسِ قدیمی پلن را با «۵ اکانت» ساخته باشد، اینجا به ۱ برمی‌گردد.
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

    # ═══════════════ پلن‌ها ═══════════════
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

    # ═══════════════ بسته امتیاز ═══════════════
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

    def create_pack_order(self, uid, pack_id, code="", use_wallet=False):
        """سفارش خرید امتیاز. (سفارش, خطا)"""
        k = self.pack(pack_id)
        if not k or not k["active"]:
            return None, "این بسته موجود نیست"
        amount = k["price"]
        off = 0
        if code:
            off, err = self.check_discount(code, amount)
            if err:
                return None, err
        after = amount - off
        w = 0
        if use_wallet:
            w = min(self.balance(uid), after)
            after -= w
        total = k["points"] + k["bonus"]
        oid = self.x(
            "INSERT INTO orders (uid,plan_id,plan_name,days,amount,discount_code,"
            "discount_off,wallet_used,final,status,created_at,kind,points)"
            " VALUES (?,?,?,0,?,?,?,?,?,'pending',?,'points',?)",
            (uid, pack_id, k["name"], amount, code.upper() if code else None,
             off, w, after, now(), total))
        return self.order(oid), ""

    def create_custom_points_order(self, uid, points, price):
        """خرید امتیاز به تعداد دلخواه."""
        points = int(points)
        price = int(price)
        if points <= 0 or price <= 0:
            return None, "مقدار نامعتبر"
        oid = self.x(
            "INSERT INTO orders (uid,plan_id,plan_name,days,amount,"
            "discount_off,wallet_used,final,status,created_at,kind,points)"
            " VALUES (?,0,?,0,?,0,0,?,'pending',?,'points',?)",
            (uid, f"{points} امتیاز", price, price, now(), points))
        return self.order(oid), ""

    def create_wallet_order(self, uid, amount):
        """شارژ کیف پول."""
        amount = int(amount)
        if amount <= 0:
            return None, "مبلغ نامعتبر"
        oid = self.x(
            "INSERT INTO orders (uid,plan_id,plan_name,days,amount,"
            "discount_off,wallet_used,final,status,created_at,kind,points)"
            " VALUES (?,0,'شارژ کیف پول',0,?,0,0,?,'pending',?,'wallet',0)",
            (uid, amount, amount, now()))
        return self.order(oid), ""

    # ═══════════════ کد تخفیف ═══════════════
    def add_discount(self, code, percent=0, flat=0, max_uses=0, days_valid=0):
        code = code.upper().strip()
        percent, flat = int(percent), int(flat)
        max_uses, days_valid = int(max_uses), int(days_valid)
        if not code or not (0 <= percent <= 100) or flat < 0 or max_uses < 0 or days_valid < 0:
            raise ValueError("مقادیر کد تخفیف نامعتبر است")
        exp = now() + days_valid * 86400 if days_valid else 0
        self.x("INSERT OR REPLACE INTO discounts"
               " (code,percent,flat,max_uses,used,expires_at,active,created_at)"
               " VALUES (?,?,?,?,COALESCE((SELECT used FROM discounts WHERE code=?),0),"
               "?,1,?)", (code, int(percent), int(flat), int(max_uses), code, exp, now()))
        return code

    def discount(self, code):
        return self.x("SELECT * FROM discounts WHERE code=?",
                      (code.upper().strip(),), "one")

    def check_discount(self, code, amount):
        """(مبلغ_تخفیف, پیام_خطا)"""
        d = self.discount(code)
        if not d:
            return 0, "کد تخفیف پیدا نشد"
        if not d["active"]:
            return 0, "این کد غیرفعال است"
        if d["expires_at"] and d["expires_at"] < now():
            return 0, "این کد منقضی شده"
        if d["max_uses"] and d["used"] >= d["max_uses"]:
            return 0, "ظرفیت این کد پر شده"
        off = d["flat"] + (amount * d["percent"] // 100)
        return min(off, amount), ""

    def use_discount(self, code):
        self.x("UPDATE discounts SET used=used+1 WHERE code=?",
               (code.upper().strip(),))

    def discounts(self):
        return self.x("SELECT * FROM discounts ORDER BY created_at DESC", (), "all")

    # ═══════════════ کیف پول ═══════════════
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

    def wallet_log(self, uid, n=10):
        return self.x("SELECT * FROM wallet_log WHERE uid=? ORDER BY id DESC LIMIT ?",
                      (uid, n), "all")

    # ═══════════════ سفارش ═══════════════
    def create_order(self, uid, plan_id, code="", use_wallet=False):
        """(سفارش, خطا)"""
        p = self.plan(plan_id)
        if not p or not p["active"]:
            return None, "این پلن موجود نیست"
        amount = p["price"]
        off = 0
        if code:
            off, err = self.check_discount(code, amount)
            if err:
                return None, err
        after = amount - off
        w = 0
        if use_wallet:
            w = min(self.balance(uid), after)
            after -= w
        oid = self.x(
            "INSERT INTO orders (uid,plan_id,plan_name,days,amount,discount_code,"
            "discount_off,wallet_used,final,status,created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,'pending',?)",
            (uid, plan_id, p["name"], p["days"], amount, code.upper() if code else None,
             off, w, after, now()))
        return self.order(oid), ""

    def order(self, oid):
        return self.x("SELECT * FROM orders WHERE id=?", (oid,), "one")

    def attach_receipt(self, oid, file_id=None, text=None):
        self.x("UPDATE orders SET receipt_file=?,receipt_text=?,status='paid',"
               "paid_at=? WHERE id=? AND status='pending'",
               (file_id, text, now(), oid))
        return self.order(oid)

    def pending_orders(self):
        return self.x("SELECT * FROM orders WHERE status='paid' ORDER BY id", (), "all")

    def user_orders(self, uid, n=10):
        return self.x("SELECT * FROM orders WHERE uid=? ORDER BY id DESC LIMIT ?",
                      (uid, n), "all")

    def last_open_order(self, uid):
        return self.x("SELECT * FROM orders WHERE uid=? AND status='pending'"
                      " ORDER BY id DESC LIMIT 1", (uid,), "one")

    def approve(self, oid, admin_id):
        """(سفارش, خطا) — تأیید مالی اتمیک انجام می‌شود."""
        with self.lock:
            o = self.x("SELECT * FROM orders WHERE id=?", (oid,), "one")
            if not o:
                return None, "سفارش پیدا نشد"
            if o["status"] in ("approved", "rejected"):
                return None, f"قبلاً {o['status']} شده"
            if o["status"] != "paid":
                return None, "فقط سفارش دارای رسید قابل تأیید است"

            if o["wallet_used"]:
                w = self.x("SELECT balance FROM wallet WHERE uid=?", (o["uid"],), "one")
                if not w or w["balance"] < o["wallet_used"]:
                    return None, "موجودی کیف پول برای این سفارش دیگر کافی نیست"

            if o["discount_code"]:
                d = self.discount(o["discount_code"])
                if not d or not d["active"]:
                    return None, "کد تخفیف این سفارش دیگر فعال نیست"
                if d["max_uses"] and d["used"] >= d["max_uses"]:
                    return None, "ظرفیت کد تخفیف این سفارش پر شده است"

            try:
                cur = self.c.execute(
                    "UPDATE orders SET status='approved',decided_at=?,admin_id=? "
                    "WHERE id=? AND status='paid'", (now(), admin_id, oid))
                if cur.rowcount != 1:
                    self.c.rollback()
                    return None, "سفارش قبلاً رسیدگی شده است"

                if o["wallet_used"]:
                    cur = self.c.execute(
                        "UPDATE wallet SET balance=balance-? "
                        "WHERE uid=? AND balance>=?",
                        (o["wallet_used"], o["uid"], o["wallet_used"]))
                    if cur.rowcount != 1:
                        self.c.rollback()
                        return None, "موجودی کیف پول برای این سفارش کافی نیست"
                    self.c.execute(
                        "INSERT INTO wallet_log (uid,amount,kind,detail,ts) "
                        "VALUES (?,?,?,?,?)",
                        (o["uid"], -o["wallet_used"], "order",
                         f"سفارش #{oid}", now()))

                if o["discount_code"]:
                    cur = self.c.execute(
                        "UPDATE discounts SET used=used+1 WHERE code=? AND active=1 "
                        "AND (max_uses=0 OR used<max_uses)", (o["discount_code"],))
                    if cur.rowcount != 1:
                        self.c.rollback()
                        return None, "ظرفیت کد تخفیف این سفارش پر شده است"
                self.c.commit()
            except Exception:
                self.c.rollback()
                raise
            return self.order(oid), ""

    def reject(self, oid, admin_id, reason=""):
        o = self.order(oid)
        if not o:
            return None, "سفارش پیدا نشد"
        if o["status"] in ("approved", "rejected"):
            return None, f"قبلاً {o['status']} شده"
        if o["status"] != "paid":
            return None, "فقط سفارش دارای رسید قابل رد است"
        self.x("UPDATE orders SET status='rejected',decided_at=?,admin_id=?,note=?"
               " WHERE id=? AND status='paid'", (now(), admin_id, reason, oid))
        return self.order(oid), ""

    def cancel_open(self, uid):
        self.x("UPDATE orders SET status='canceled' WHERE uid=? AND status='pending'",
               (uid,))

    # ═══════════════ زیرمجموعه ═══════════════
    def set_referrer(self, uid, referrer):
        if uid == referrer:
            return False
        if self.x("SELECT uid FROM referrals WHERE uid=?", (uid,), "one"):
            return False
        self.x("INSERT INTO referrals (uid,referrer,joined_at) VALUES (?,?,?)",
               (uid, referrer, now()))
        return True

    def referrer_of(self, uid):
        r = self.x("SELECT referrer FROM referrals WHERE uid=?", (uid,), "one")
        return r["referrer"] if r else None

    def my_refs(self, uid):
        return self.x("SELECT * FROM referrals WHERE referrer=?", (uid,), "all")

    def pay_referral(self, oid, percent):
        """سازگاری با سفارش‌های قدیمی؛ پاداش درصدی دیگر وجود ندارد."""
        return None, 0

    def reward_verified_referral(self, invitee_uid, referrer_uid, points=2):
        """یک‌بار برای هر دعوت‌شده پس از تأیید شماره، امتیاز بدهد؛ اتمیک."""
        points = max(0, int(points or 0))
        if points <= 0 or not invitee_uid or not referrer_uid or invitee_uid == referrer_uid:
            return None, 0
        with self.lock:
            try:
                self.c.execute("BEGIN")
                r = self.c.execute(
                    "SELECT uid, referrer FROM referrals WHERE uid=? AND referrer=?",
                    (invitee_uid, referrer_uid)).fetchone()
                if not r:
                    self.c.rollback()
                    return None, 0
                cur = self.c.execute(
                    "INSERT OR IGNORE INTO referral_point_rewards "
                    "(invitee_uid,referrer,points,created_at) VALUES (?,?,?,?)",
                    (invitee_uid, referrer_uid, points, now()))
                if cur.rowcount != 1:
                    self.c.rollback()
                    return None, 0
                self.c.execute("INSERT OR IGNORE INTO points (uid) VALUES (?)", (referrer_uid,))
                self.c.execute("UPDATE points SET balance=balance+?, earned=earned+? WHERE uid=?",
                                (points, points, referrer_uid))
                self.c.execute(
                    "INSERT INTO points_log (uid,amount,kind,detail,ts) VALUES (?,?,?,?,?)",
                    (referrer_uid, points, "referral",
                     f"دعوت معتبر کاربر {invitee_uid}", now()))
                self.c.execute("UPDATE referrals SET rewarded=1 WHERE uid=?", (invitee_uid,))
                self.c.commit()
                return referrer_uid, points
            except Exception:
                self.c.rollback()
                raise

    # ═══════════════ امتیاز ═══════════════
    def p_row(self, uid):
        r = self.x("SELECT * FROM points WHERE uid=?", (uid,), "one")
        if not r:
            self.x("INSERT OR IGNORE INTO points (uid) VALUES (?)", (uid,))
            r = self.x("SELECT * FROM points WHERE uid=?", (uid,), "one")
        return r

    def p_balance(self, uid):
        return self.p_row(uid)["balance"]

    def p_add(self, uid, amount, kind="bonus", detail=""):
        amount = int(amount)
        self.p_row(uid)
        if amount >= 0:
            self.x("UPDATE points SET balance=balance+?, earned=earned+? WHERE uid=?",
                   (amount, amount, uid))
        else:
            cur = self.x("SELECT balance FROM points WHERE uid=?",
                         (uid,), "one")["balance"]
            real = min(cur, -amount)          # فقط همان‌قدر که واقعاً کم شد
            amount = -real
            self.x("UPDATE points SET balance=balance-?, spent=spent+? WHERE uid=?",
                   (real, real, uid))
        self.x("INSERT INTO points_log (uid,amount,kind,detail,ts) VALUES (?,?,?,?,?)",
               (uid, amount, kind, detail, now()))
        return self.p_balance(uid)

    def p_spend(self, uid, amount, detail=""):
        """کسر اتمیک؛ فقط هزینه کم می‌شود و مانده حفظ می‌شود."""
        amount = abs(int(amount or 0))
        if amount <= 0:
            return True, self.p_balance(uid)
        with self.lock:
            self.c.execute("INSERT OR IGNORE INTO points (uid) VALUES (?)", (uid,))
            cur = self.c.execute(
                "UPDATE points SET balance=balance-?, spent=spent+? "
                "WHERE uid=? AND balance>=?",
                (amount, amount, uid, amount))
            if cur.rowcount != 1:
                self.c.commit()
                return False, self.p_balance(uid)
            self.c.execute(
                "INSERT INTO points_log (uid,amount,kind,detail,ts) VALUES (?,?,?,?,?)",
                (uid, -amount, "use", detail, now()))
            self.c.commit()
            return True, self.p_balance(uid)

    def p_charge_due(self, uid, per_hour):
        """بر اساس زمان سپری‌شده امتیاز کم می‌کند.
        برمی‌گرداند (کسر_شده, موجودی, تمام_شد)"""
        r = self.p_row(uid)
        t = now()
        if not r["last_charge"]:
            self.x("UPDATE points SET last_charge=? WHERE uid=?", (t, uid))
            return 0, r["balance"], False
        hours = (t - r["last_charge"]) // 3600
        if hours <= 0:
            return 0, r["balance"], r["balance"] <= 0
        cost = hours * per_hour
        self.x("UPDATE points SET last_charge=? WHERE uid=?",
               (r["last_charge"] + hours * 3600, uid))
        bal = self.p_add(uid, -cost, "runtime", f"{hours} ساعت کارکرد")
        return cost, bal, bal <= 0

    def p_reset_charge(self, uid):
        self.p_row(uid)
        self.x("UPDATE points SET last_charge=? WHERE uid=?", (now(), uid))

    def p_log(self, uid, n=10):
        return self.x("SELECT * FROM points_log WHERE uid=? ORDER BY id DESC LIMIT ?",
                      (uid, n), "all")

    def p_top(self, n=10):
        return self.x("SELECT * FROM points ORDER BY earned DESC LIMIT ?", (n,), "all")

    def p_stats(self):
        r = self.x("SELECT COUNT(*) c, COALESCE(SUM(balance),0) b,"
                   " COALESCE(SUM(earned),0) e, COALESCE(SUM(spent),0) s"
                   " FROM points", (), "one")
        return r or {"c": 0, "b": 0, "e": 0, "s": 0}

    # ═══════════════ تیکت ═══════════════
    def new_ticket(self, uid, subject, text):
        tid = self.x("INSERT INTO tickets (uid,subject,created_at,updated_at)"
                     " VALUES (?,?,?,?)", (uid, subject[:80], now(), now()))
        self.add_msg(tid, text, False)
        return tid

    def add_msg(self, tid, text, from_admin):
        self.x("INSERT INTO ticket_msgs (tid,from_admin,text,ts) VALUES (?,?,?,?)",
               (tid, 1 if from_admin else 0, text, now()))
        self.x("UPDATE tickets SET updated_at=?,status=? WHERE id=?",
               (now(), "answered" if from_admin else "open", tid))

    def ticket(self, tid):
        return self.x("SELECT * FROM tickets WHERE id=?", (tid,), "one")

    def ticket_msgs(self, tid):
        return self.x("SELECT * FROM ticket_msgs WHERE tid=? ORDER BY id", (tid,), "all")

    def open_tickets(self):
        return self.x("SELECT * FROM tickets WHERE status='open' ORDER BY updated_at",
                      (), "all")

    def user_tickets(self, uid):
        return self.x("SELECT * FROM tickets WHERE uid=? ORDER BY id DESC LIMIT 10",
                      (uid,), "all")

    def close_ticket(self, tid):
        self.x("UPDATE tickets SET status='closed' WHERE id=?", (tid,))

    # ═══════════════ آمار ═══════════════
    def revenue(self, since=0):
        r = self.x("SELECT COUNT(*) c, COALESCE(SUM(final),0) s FROM orders"
                   " WHERE status='approved' AND decided_at>=?", (since,), "one")
        return r["c"], r["s"]

    def stats(self):
        t = now()
        d1, s1 = self.revenue(t - 86400)
        d7, s7 = self.revenue(t - 604800)
        d30, s30 = self.revenue(t - 2592000)
        all_c, all_s = self.revenue(0)
        st = {r["status"]: r["c"] for r in
              self.x("SELECT status,COUNT(*) c FROM orders GROUP BY status", (), "all")}
        return {"day": (d1, s1), "week": (d7, s7), "month": (d30, s30),
                "all": (all_c, all_s), "orders": st,
                "wallet_total": (self.x("SELECT COALESCE(SUM(balance),0) s FROM wallet",
                                        (), "one") or {}).get("s", 0)}

    def top_refs(self, n=10):
        return self.x("SELECT referrer, COUNT(*) c FROM referrals"
                      " GROUP BY referrer ORDER BY c DESC LIMIT ?", (n,), "all")

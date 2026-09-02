#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# JAFJ_V54_STAMP — پاسخ فوریِ قابل‌تنظیم و بررسی کامل تبادل
"""
═══════════════════════════════════════════════════════════
  جفج (Jafj) — سلف‌بات تلگرام
  با شماره وارد اکانت خودت می‌شود | کنترل از Saved Messages
═══════════════════════════════════════════════════════════

  ▸ ورود با شماره موبایل + کد تأیید (مثل خود تلگرام)
  ▸ پنل مدیریت داخل «پیام‌های ذخیره‌شده» (Saved Messages)
  ▸ فعالیت/استراحت و سقف ساعتی — همه با دستور قابل تنظیم
  ▸ دو پروفایل مستقل: عادی و VIP
  ▸ هوش مصنوعی فقط پیام را تحلیل می‌کند و پاسخ خودکار نمی‌سازد

  ── نصب ──────────────────────────────────────────────
      pip install telethon

  ── راه‌اندازی ────────────────────────────────────────
   ۱) pip install telethon
   ۲) python 32.py
   ۳) شماره را وارد کن → کد در تلگرام می‌آید → وارد کن
      (رمز دو مرحله‌ای داشته باشی، آن را هم می‌پرسد)
   ۴) در تلگرام برو Saved Messages و بفرست:  .panel

   هیچ ویرایشی لازم نیست — api_id از قبل داخل فایل است.

  همه‌چیز در jafj_creds.json و jafj.session ذخیره می‌شود؛
  دفعات بعد دیگر هیچ‌چیز نمی‌پرسد.

  تنظیمات را خودت تعیین می‌کنی. چیزی تنظیم نکنی هم
  ربات روشن می‌ماند و کار می‌کند — با مقادیر پیش‌فرض.
═══════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════
#  ۱) اینجا را پر کن
# ═══════════════════════════════════════════════════════

#  آماده است — نیازی به ویرایش نیست.
#  فقط اجرا کن و شماره و کدی که تلگرام می‌فرستد را وارد کن.
API_ID = 28039994
API_HASH = "00877cdcd706564a4de6abf7f7d64349"
PHONE = ""            # خالی بگذار — موقع اجرا می‌پرسد

PREFIX = "."          # پیشوند دستورها. هم "." و هم "/" کار می‌کند.
DRY_RUN = False       # True = چیزی واقعاً ارسال نمی‌شود (تست)


# ═══════════════════════════════════════════════════════
#  ۲) پیش‌فرض‌ها — همه با دستور قابل تغییرند
# ═══════════════════════════════════════════════════════

DEFAULTS = {
    "standard": {
        "mode": "cycle",         # always = ۲۴ساعته | cycle = فعالیت/استراحت
        "active_minutes": 60,
        "rest_minutes": 30,
        "max_per_hour": 12,      # سقف ارسال در ساعت (۰ = نامحدود)
        "min_gap_sec": 45,
        "max_gap_sec": 120,
        "quiet_hours": [],
        "channel": "",           # با دستور .setch تنظیم می‌شود
    },
    "vip": {
        "mode": "always",
        "active_minutes": 60,
        "rest_minutes": 15,
        "max_per_hour": 30,
        "min_gap_sec": 20,
        "max_gap_sec": 45,
        "quiet_hours": [],
        "channel": "",           # با دستور .setvip تنظیم می‌شود
    },
    "paused": False,

    # ── تبادل دوطرفه ──────────────────────────────────
    #  طرف پیام می‌دهد «جوین شدم» → ربات چک می‌کند
    #  واقعاً عضو کانال تو شده یا نه → اگر شده بود جوین می‌شود
    #  اگر بعداً لفت داد، ربات هم از کانالش لفت می‌دهد
    "exchange": {
        "enabled": False,          # .ex on
        "auto_join": True,         # False = اول از تو تأیید می‌گیرد
        "groups": [],              # گروه‌های تبادل که رصد شوند (خالی = فقط PV)
        "min_join_gap_sec": 30,    # فاصله پیش‌فرض بین دو جوین (از یک عدد ثابت به بازه تصادفی)
        "max_join_gap_sec": 60,
        # بررسی عضویت طرف بی‌صدا و با فاصله تصادفی انجام می‌شود.
        # check_interval_sec فقط برای سازگاری با تنظیم‌های خیلی قدیمی است.
        "check_min_sec": 15,
        "check_max_sec": 30,
        "check_interval_sec": 30,
        "response_delay_sec": 15,  # تأخیر پاسخ بعد از Join واقعی
        "max_joins_per_day": 0,    # Join بدون سقف روزانه
        "recheck_hours": 12,       # سازگاری با نسخه‌های قدیمی
        "recheck_minutes": 1,       # بررسی پیش‌فرض عضویت هر یک دقیقه
        "max_strikes": 3,          # چند بار نبود → لفت
        # متن جواب‌ها را خودت تعیین می‌کنی:
        #   .ex msgok متن   → وقتی جوین شد
        #   .ex msgno متن   → وقتی طرف هنوز عضو نشده
        #   .ex msgwait متن → وقتی در حال بررسی است
        # هرکدام خالی باشد، همان مورد جواب داده نمی‌شود.
        "reply": True,
        # هیچ متن ثابتی از طرف کد ارسال نمی‌شود؛ متن‌ها را خودت ثبت می‌کنی.
        "msg_ok": "",
        "msg_no": "",
        "msg_wait": "",
        "msg_nolink": "",
        "msg_come": "",
        "come_delay_sec": 0,         # تأخیر پیام «بیا» بعد از جوین
        "reminder_min_sec": 5,       # فاصله کمینه یادآوری عضو‌نشده
        "reminder_max_sec": 15,      # فاصله بیشینه یادآوری عضو‌نشده
        # برای جلوگیری از مزاحمت، پیش‌فرض فقط یک پیام «عضو نیست» است.
        # ۰ = هیچ یادآوری؛ بررسی عضویت همچنان بی‌صدا ادامه دارد.
        "max_reminders": 1,
        # ── حالت پیش‌قدم: خودت اول جوین می‌شوی ──
        "initiate": True,         # پیش‌فرض روشن
        "scan_every_sec": 30,     # پیش‌قدم: هر ۳۰ ثانیه پیام‌های جدید را می‌بیند
        "scan_every_min": 1,      # سازگاری با تنظیم قدیمیِ دقیقه‌ای
        "scan_limit": 50,         # چند پیام آخر هر گروه
        "scan_max_age_sec": 300,   # فقط لینک حداکثر ۵ دقیقه اخیر
        "scan_age_version": 1,
        "scan_pick": 1,           # تازه‌ترین لینک جدید
        "msg_first": "",          # متنی که بعد از جوینِ خودت ریپلای می‌شود
        "scan_last": {},          # آخرین پیام دیده‌شده هر گروه
        # فقط به ریپلای‌هایی که این کلمات را دارند واکنش نشان بده.
        # خالی = به هر ریپلایی روی پیام تو واکنش نشان می‌دهد.
        "words": [],
        # گزارش خصوصی در Saved Messages؛ پیش‌فرض لحظه‌ای است.
        "report_mode": "live",                 # live | summary | off
        "report_summary_interval_sec": 86400,   # خلاصه خودکار هر ۲۴ ساعت
        "report_last_sent": 0,
        # ── سقف جوین/ساعت (محدودیت آهسته، جدا از محافظ ریسک) ──
        #  خاموش پیش‌فرض؛ اگر روشن باشد، در یک ساعتِ غلتان از این تعداد
        #  بیشتر جوین نمی‌زند و تا باز شدن پنجره صبر می‌کند.
        "hour_cap_on": False,        # پیش‌فرض خاموش (فقط با دستور فعال می‌شود)
        "hour_cap": 60,              # عددِ امنِ پیشنهادی: ۶۰ جوین/ساعت
        "_hour_cap_blocked": 0,      # آخرین باری که به‌خاطر سقف متوقف شده
    },

    # ── محافظ ریپورت ───────────────────────────────────
    #  با چند معیار (ارسال، جوین، لفت، خطای جوین، فلاد/محدودیت، برنگشتنی)
    #  درصدِ تقریبیِ خطرِ ریپورت/محدود شدن حساب را می‌سازد.
    #  وقتی به آستانه (trigger) برسد، تبادل را کاملاً خودکار خاموش می‌کند
    #  تا اکانت در خطر نیفتد؛ وقتی زیر آستانه‌ی بازگشت (resume) رفت،
    #  خودش دوباره روشنش می‌کند. فقط اگر خودِ محافظ خاموشش کرده باشد
    #  برمی‌گرداند تا تصمیم دستیِ کاربر (روشن/خاموشِ .ex) را نادیده نگیرد.
    "risk": {
        # ── حالت پیش‌فرض: توقف بر اساس «امتیازِ انتزاعی» خاموش است ──
        "on": False,             # توقفِ خودکار بر اساس درصدِ تخیلیِ ریسک: خاموش در حالت پیش‌فرض
        # ── پایشِ «واقعی» (همیشه فعال): فقط وقتی اکانت واقعاً در مرز ریپ است ──
        "hard_on": True,         # چکِ سیگنال‌های واقعیِ ریپ — همیشه روشن
        "hard_trigger": 80,      # امتیازِ واقعی بالای این → توقف اجباری
        "hard_window_min": 30,   # بازه‌ی پایشِ سیگنال واقعی (دقیقه)
        "window_hours": 24,      # بازه‌ی آماری (ساعت اخیر)
        "trigger": 75,           # بالای این درصد (فقط زمانی که on=True) → تبادل خاموش
        "resume": 55,            # زیر این درصد → تبادل روشن دوباره
        "check_interval_sec": 60, # هر چند ثانیه یک‌بار محاسبه
        "_auto_off": False,      # آیا محافظ خودش خاموش کرده؟
        "_last_off": 0,          # زمان آخرین خاموشی خودکار
        "_last_alert": 0,        # زمان آخرین هشدار (ضد اسپم نوتیف)
    },
}

SESSION = "jafj"
CREDS_FILE = "jafj_creds.json"
AI_FILE = "jafj_ai.json"
LIMITS_FILE = "jafj_limits.json"     # سقف‌های پلن — از سمت پنل نوشته می‌شود
STATUS_FILE = "jafj_status.json"     # گزارش زنده — پنل می‌خواندش
SETTINGS_FILE = "jafj_settings.json"
DB_FILE = "jafj.db"
LOG_FILE = "jafj.log"


# ═══════════════════════════════════════════════════════
#  ۳) کد
# ═══════════════════════════════════════════════════════

import os
import re
import sys
import json
import time
import random
import sqlite3
import asyncio
import threading
import traceback
import http.cookiejar
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime

VERSION = "3.0"
BUILD_TAG = "JAFJ_SELF_69_70_EN_2026_08_28"
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
EN = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def fa(n):
    return str(n)


def num(s):
    """عدد فارسی یا انگلیسی → int"""
    return int(str(s).translate(EN).strip())


def dur(m):
    m = int(m)
    if m <= 0:
        return "ندارد"
    if m < 60:
        return f"{fa(m)} دقیقه"
    h, r = divmod(m, 60)
    return f"{fa(h)} ساعت" + (f" و {fa(r)} دقیقه" if r else "")


def secs(s):
    s = int(s)
    if s < 60:
        return f"{fa(s)} ثانیه"
    m, r = divmod(s, 60)
    if m < 60:
        return f"{fa(m)} دقیقه" + (f" و {fa(r)} ثانیه" if r else "")
    h, m = divmod(m, 60)
    return f"{fa(h)} ساعت" + (f" و {fa(m)} دقیقه" if m else "")


# ─────────────────────────────────────────────
#  تنظیمات
# ─────────────────────────────────────────────
class Settings:
    def __init__(self, path=SETTINGS_FILE):
        self.path = path
        self.data = json.loads(json.dumps(DEFAULTS))
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    saved = json.load(f)
                for k, v in saved.items():
                    if isinstance(v, dict) and isinstance(self.data.get(k), dict):
                        self.data[k].update(v)
                    else:
                        self.data[k] = v
                old_ex = saved.get("exchange") or {}
                if ("msg_come" not in old_ex and old_ex.get("msg_first")):
                    self.data["exchange"]["msg_come"] = old_ex["msg_first"]
                # متن‌های پیش‌فرض نسخه‌های قبلی متن ثابت بودند؛ در این نسخه
                # فقط متن‌هایی که خود کاربر ثبت کرده‌اند نگه داشته می‌شوند.
                if old_ex.get("msg_come") in ("بیا", "اومدم", "اومدم بیا"):
                    self.data["exchange"]["msg_come"] = ""
                    self.data["exchange"]["msg_first"] = ""
                if old_ex.get("msg_ok") in ("بیا", "اومدم", "اومدم بیا"):
                    self.data["exchange"]["msg_ok"] = ""
                if old_ex.get("msg_no") == "اول عضو شو":
                    self.data["exchange"]["msg_no"] = ""
                if old_ex.get("msg_nolink") == "لینک کانالت را بفرست":
                    self.data["exchange"]["msg_nolink"] = ""
                # تنظیم‌های قدیمی (فاصله‌ی دقیقاً ثابت) به بازه‌ی تصادفی جدید منتقل شوند.
                # فاصله‌ی ثابت الگوی ماشینی و قابل شناسایی است؛ پس به ۳۰–۶۰ ثانیه تصادفی می‌رود.
                if ((old_ex.get("min_join_gap_sec"), old_ex.get("max_join_gap_sec"))
                        in ((90, 240), (30, 30), (60, 60), (45, 45))):
                    self.data["exchange"]["min_join_gap_sec"] = 30
                    self.data["exchange"]["max_join_gap_sec"] = 60
                if old_ex.get("scan_age_version") != 1:
                    self.data["exchange"]["scan_max_age_sec"] = 300
                    self.data["exchange"]["scan_age_version"] = 1
                if "scan_every_sec" not in old_ex:
                    # درخواست فعلی: پیش‌قدم هر ۳۰ ثانیه یک فرصت اسکن/Join داشته باشد؛
                    # مقدارهای دقیقه‌ای نسخه‌های قبل (حتی ۲ دقیقه) به این cadence منتقل می‌شوند.
                    self.data["exchange"]["scan_every_sec"] = 30
                    self.data["exchange"]["scan_every_min"] = 1
                    # یک بار بعد از ارتقا دوباره آخرین پیام‌ها را ببین تا کانال
                    # معطل‌مانده‌ای از اسکن قبلی جا نماند.
                    self.data["exchange"]["scan_last"] = {}
                if old_ex.get("recheck_minutes") in (None, 0):
                    self.data["exchange"]["recheck_minutes"] = 1
                # مقدار پیش‌فرض بررسی عضویت: تصادفی بین ۱۵ تا ۳۰ ثانیه.
                # جفت قدیمی ۵ تا ۱۵ و عدد ثابت ۱۵، تنظیم پیش‌فرض قبلی بودند.
                old_pair = (old_ex.get("check_min_sec"), old_ex.get("check_max_sec"))
                if ("check_min_sec" not in old_ex or "check_max_sec" not in old_ex
                        or old_pair in ((5, 15), (15, 15))):
                    self.data["exchange"]["check_min_sec"] = 15
                    self.data["exchange"]["check_max_sec"] = 30
                if "check_interval_sec" not in old_ex or old_ex.get("check_interval_sec") == 15:
                    self.data["exchange"]["check_interval_sec"] = 30
                if "response_delay_sec" not in old_ex:
                    self.data["exchange"]["response_delay_sec"] = 15
                # سه پیام، پیش‌فرض نسخه قبل بود؛ برای ضداسپم به یک پیام تبدیلش کن.
                # اگر مقدار دیگری از قبل ثبت شده، آن را دست نزن.
                if old_ex.get("max_reminders") in (None, 3):
                    self.data["exchange"]["max_reminders"] = 1
                if old_ex.get("initiate") is False:
                    self.data["exchange"]["initiate"] = True
                if old_ex.get("auto_join") is False:
                    self.data["exchange"]["auto_join"] = True
                if not old_ex.get("scan_pick") or old_ex.get("scan_pick") == 2:
                    self.data["exchange"]["scan_pick"] = 1
            except Exception as e:
                print(f"⚠️ خواندن تنظیمات ناموفق: {e}")
        # سقف روزانه Join از این نسخه حذف شده؛ حتی تنظیم قدیمی ۲۰ هم نادیده گرفته می‌شود.
        self.data["exchange"]["max_joins_per_day"] = 0

    def save(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            print(f"⚠️ ذخیره ناموفق: {e}")

    def prof(self, tier):
        return self.data["vip" if tier == "vip" else "standard"]

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v


# ─────────────────────────────────────────────
#  دیتابیس
# ─────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    text TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'standard',
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at INTEGER NOT NULL,
    scheduled_at INTEGER NOT NULL DEFAULT 0,
    sent_at INTEGER,
    message_id INTEGER
);
CREATE INDEX IF NOT EXISTS idx_q ON queue(status, tier, scheduled_at);

CREATE TABLE IF NOT EXISTS exchange (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_id INTEGER,
    peer_name TEXT,
    link TEXT NOT NULL UNIQUE,
    channel_title TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    strikes INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    joined_at INTEGER,
    last_check INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    src_chat INTEGER,
    src_msg INTEGER,
    replied INTEGER NOT NULL DEFAULT 0,
    direction TEXT NOT NULL DEFAULT 'in',
    reminders INTEGER NOT NULL DEFAULT 0,
    next_reminder INTEGER NOT NULL DEFAULT 0,
    next_check INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_ex ON exchange(status, last_check);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL, level TEXT NOT NULL,
    kind TEXT NOT NULL, detail TEXT
);
"""


class DB:
    def __init__(self, path=DB_FILE):
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(path, check_same_thread=False, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout = 30000")
        with self.lock:
            self.conn.executescript(SCHEMA)
            # مهاجرت: ستون‌های جدید روی دیتابیس قدیمی
            have = {r[1] for r in self.conn.execute("PRAGMA table_info(exchange)")}
            for col, decl in (("src_chat", "INTEGER"), ("src_msg", "INTEGER"),
                              ("replied", "INTEGER NOT NULL DEFAULT 0"),
                              ("direction", "TEXT NOT NULL DEFAULT 'in'"),
                              ("reminders", "INTEGER NOT NULL DEFAULT 0"),
                              ("next_reminder", "INTEGER NOT NULL DEFAULT 0"),
                              ("next_check", "INTEGER NOT NULL DEFAULT 0")):
                if col not in have:
                    self.conn.execute(f"ALTER TABLE exchange ADD COLUMN {col} {decl}")
            # بعد از مهاجرت ساخته شود؛ وگرنه دیتابیس قدیمی هنوز ستون next_check ندارد.
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ex_next_check "
                              "ON exchange(status, next_check)")
            self.conn.commit()

    def _x(self, sql, a=(), f=None):
        with self.lock:
            c = self.conn.execute(sql, a)
            if f == "one":
                r = c.fetchone()
                return dict(r) if r else None
            if f == "all":
                return [dict(r) for r in c.fetchall()]
            self.conn.commit()
            return c.lastrowid

    def enqueue(self, target, text, tier="standard", when=0):
        now = int(time.time())
        return self._x("INSERT INTO queue (target,text,tier,created_at,scheduled_at)"
                       " VALUES (?,?,?,?,?)", (target, text, tier, now, when or now))

    def next_pending(self, tier):
        """آیتم‌های بدون مقصد نگه داشته می‌شوند تا کانال تعیین شود."""
        return self._x("SELECT * FROM queue WHERE status='pending' AND tier=?"
                       " AND target<>'' AND scheduled_at<=? ORDER BY id LIMIT 1",
                       (tier, int(time.time())), "one")

    def held_count(self, tier=None):
        """پیام‌هایی که منتظر تعیین کانال‌اند."""
        if tier:
            return self._x("SELECT COUNT(*) c FROM queue WHERE status='pending'"
                           " AND target='' AND tier=?", (tier,), "one")["c"]
        return self._x("SELECT COUNT(*) c FROM queue WHERE status='pending'"
                       " AND target=''", (), "one")["c"]

    def assign_target(self, tier, channel):
        """وقتی کانال تعیین شد، پیام‌های معلق همان بخش آزاد می‌شوند."""
        with self.lock:
            c = self.conn.execute("UPDATE queue SET target=? WHERE status='pending'"
                                  " AND target='' AND tier=?", (channel, tier))
            self.conn.commit()
            return c.rowcount

    def retarget_pending(self, tier, old_channel, new_channel):
        """پیام‌های صف‌مانده را از کانال قبلی به کانال جدید منتقل می‌کند."""
        if not old_channel or old_channel == new_channel:
            return 0
        with self.lock:
            c = self.conn.execute(
                "UPDATE queue SET target=? WHERE status='pending' AND tier=? AND target=?",
                (new_channel, tier, old_channel))
            self.conn.commit()
            return c.rowcount

    def mark_sent(self, qid, mid=None):
        self._x("UPDATE queue SET status='sent',sent_at=?,message_id=? WHERE id=?",
                (int(time.time()), mid, qid))

    def mark_failed(self, qid, err, retry_at=None, mx=3):
        r = self._x("SELECT attempts FROM queue WHERE id=?", (qid,), "one")
        n = (r["attempts"] if r else 0) + 1
        if retry_at and n < mx:
            self._x("UPDATE queue SET attempts=?,last_error=?,scheduled_at=?,"
                    "status='pending' WHERE id=?", (n, str(err)[:400], int(retry_at), qid))
        else:
            self._x("UPDATE queue SET attempts=?,last_error=?,status='failed' WHERE id=?",
                    (n, str(err)[:400], qid))

    def counts(self):
        return {r["status"]: r["c"] for r in
                self._x("SELECT status,COUNT(*) c FROM queue GROUP BY status", (), "all")}

    def pending_count(self, tier=None):
        if tier:
            return self._x("SELECT COUNT(*) c FROM queue WHERE status='pending'"
                           " AND tier=?", (tier,), "one")["c"]
        return self._x("SELECT COUNT(*) c FROM queue WHERE status='pending'",
                       (), "one")["c"]

    def list_pending(self, n=10):
        return self._x("SELECT * FROM queue WHERE status='pending' ORDER BY id LIMIT ?",
                       (n,), "all")

    def clear_pending(self):
        with self.lock:
            c = self.conn.execute("DELETE FROM queue WHERE status='pending'")
            self.conn.commit()
            return c.rowcount

    def delete_item(self, qid):
        with self.lock:
            c = self.conn.execute("DELETE FROM queue WHERE id=? AND status='pending'",
                                  (qid,))
            self.conn.commit()
            return c.rowcount

    def retry_failed(self):
        with self.lock:
            c = self.conn.execute("UPDATE queue SET status='pending',attempts=0,"
                                  "scheduled_at=? WHERE status='failed'",
                                  (int(time.time()),))
            self.conn.commit()
            return c.rowcount

    def sent_since(self, ts):
        return self._x("SELECT COUNT(*) c FROM queue WHERE status='sent' AND sent_at>=?",
                       (ts,), "one")["c"]

    # ---------- تبادل ----------
    def ex_add(self, peer_id, peer_name, link):
        """برمی‌گرداند (رکورد, آیا_جدید_بود)"""
        cur = self.ex_by_link(link)
        if cur:
            if peer_id and not cur.get("peer_id"):
                self.ex_set(cur["id"], peer_id=peer_id, peer_name=peer_name)
                cur = self.ex_get(cur["id"])
            return cur, False
        self._x("INSERT INTO exchange (peer_id,peer_name,link,created_at)"
                " VALUES (?,?,?,?)", (peer_id, peer_name, link, int(time.time())))
        return self.ex_by_link(link), True

    def ex_by_link(self, link):
        if not link:
            return None
        r = self._x("SELECT * FROM exchange WHERE link=?", (link,), "one")
        if r:
            return r
        return self._x("SELECT * FROM exchange WHERE lower(link)=lower(?)",
                       (link,), "one")

    def ex_get(self, eid):
        return self._x("SELECT * FROM exchange WHERE id=?", (eid,), "one")

    def ex_find(self, key):
        """با آیدی عددی یا لینک/یوزرنیم پیدا کن"""
        try:
            r = self.ex_get(num(key))
            if r:
                return r
        except (ValueError, TypeError):
            pass
        k = key.strip().lstrip("@").lower()
        return self._x("SELECT * FROM exchange WHERE lower(link) LIKE ?"
                       " ORDER BY id DESC LIMIT 1", (f"%{k}%",), "one")

    def ex_set(self, eid, **kw):
        if not kw:
            return
        cols = ",".join(f"{k}=?" for k in kw)
        self._x(f"UPDATE exchange SET {cols} WHERE id=?",
                tuple(kw.values()) + (eid,))

    def ex_list(self, status=None, limit=30):
        if status:
            return self._x("SELECT * FROM exchange WHERE status=? ORDER BY id DESC"
                           " LIMIT ?", (status, limit), "all")
        return self._x("SELECT * FROM exchange ORDER BY id DESC LIMIT ?",
                       (limit,), "all")

    def ex_due(self, ts, limit=15):
        """تبادل‌های انجام‌شده‌ای که زمان بررسی بعدی‌شان رسیده است.
        next_check برای فاصله تصادفی جدید است؛ last_check پشتیبان دیتابیس قدیمی است.
        """
        return self._x(
            "SELECT * FROM exchange WHERE status='joined' AND "
            "((next_check>0 AND next_check<=?) OR "
            " (next_check=0 AND last_check<=?)) "
            "ORDER BY CASE WHEN next_check>0 THEN next_check ELSE last_check END "
            "LIMIT ?", (ts, ts, limit), "all")

    def ex_reminder_due(self, ts, limit=20):
        return self._x("SELECT * FROM exchange WHERE status='pending'"
                       " AND peer_id IS NOT NULL"
                       " AND next_reminder>0 AND next_reminder<=?"
                       " ORDER BY next_reminder LIMIT ?", (ts, limit), "all")

    def ex_counts(self):
        return {r["status"]: r["c"] for r in
                self._x("SELECT status,COUNT(*) c FROM exchange GROUP BY status",
                        (), "all")}

    def ex_report_counts(self, since):
        """آمار تبادل برای گزارش خصوصی، از timestamp داده‌شده تا الان."""
        since = int(since or 0)
        q = lambda sql, args=(): int(self._x(sql, args, "one")["c"])
        return {
            "joined": q("SELECT COUNT(*) c FROM exchange WHERE joined_at IS NOT NULL AND joined_at>=?", (since,)),
            "out_joined": q("SELECT COUNT(*) c FROM exchange WHERE direction='out' AND joined_at IS NOT NULL AND joined_at>=?", (since,)),
            "in_joined": q("SELECT COUNT(*) c FROM exchange WHERE direction='in' AND joined_at IS NOT NULL AND joined_at>=?", (since,)),
            "left": q("SELECT COUNT(*) c FROM events WHERE kind='ex_left' AND ts>=?", (since,)),
            "failed": q("SELECT COUNT(*) c FROM events WHERE kind='ex_join_fail' AND ts>=?", (since,)),
            "pending": q("SELECT COUNT(*) c FROM exchange WHERE status='pending'"),
            "approved": q("SELECT COUNT(*) c FROM exchange WHERE status='approved'"),
            "not_returned": q("SELECT COUNT(*) c FROM exchange WHERE direction='out' AND status='joined' AND strikes>0"),
        }

    def ex_joins_today(self):
        start = int(time.mktime(datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0).timetuple()))
        return self._x("SELECT COUNT(*) c FROM exchange WHERE joined_at>=?",
                       (start,), "one")["c"]

    # ---------- محافظ ریپورت ----------
    def ex_delete(self, eid):
        with self.lock:
            c = self.conn.execute("DELETE FROM exchange WHERE id=?", (eid,))
            self.conn.commit()
            return c.rowcount

    def log(self, lvl, kind, detail=""):
        self._x("INSERT INTO events (ts,level,kind,detail) VALUES (?,?,?,?)",
                (int(time.time()), lvl, kind, str(detail)[:600]))

    def recent(self, n=15):
        return self._x("SELECT * FROM events ORDER BY id DESC LIMIT ?", (n,), "all")


# ─────────────────────────────────────────────
#  کنترل نرخ ارسال
# ─────────────────────────────────────────────
class Throttle:
    def __init__(self, p):
        self.apply(p)
        self.last = 0.0
        self.hist = []
        self.blocked_until = 0.0
        self.next_gap = self.min_gap

    def apply(self, p):
        self.min_gap = max(1, int(p["min_gap_sec"]))
        self.max_gap = max(self.min_gap, int(p["max_gap_sec"]))
        self.cap = max(0, int(p["max_per_hour"]))
        if hasattr(self, "next_gap"):
            self.next_gap = min(max(self.next_gap, self.min_gap), self.max_gap)

    def wait_time(self, now=None):
        now = now if now is not None else time.time()
        if now < self.blocked_until:
            return self.blocked_until - now
        gap = max(0.0, (self.last + self.next_gap) - now) if self.last else 0.0
        self.hist = [t for t in self.hist if t > now - 3600]
        if self.cap and len(self.hist) >= self.cap:
            gap = max(gap, (min(self.hist) + 3600) - now)
        return gap

    def record(self, now=None):
        now = now if now is not None else time.time()
        self.last = now
        self.hist.append(now)
        self.next_gap = (random.uniform(self.min_gap, self.max_gap)
                         if self.max_gap > self.min_gap else self.min_gap)

    def penalize(self, sec):
        self.blocked_until = time.time() + float(sec) + 1

    def sent_last_hour(self):
        now = time.time()
        self.hist = [t for t in self.hist if t > now - 3600]
        return len(self.hist)


# ─────────────────────────────────────────────
#  چرخه فعالیت / استراحت
# ─────────────────────────────────────────────
class Cycle:
    def __init__(self, p):
        self.anchor = time.time()
        self.apply(p)

    def apply(self, p):
        self.mode = p["mode"]
        self.active = max(1, int(p["active_minutes"]))
        self.rest = max(0, int(p["rest_minutes"]))
        self.quiet = set(p.get("quiet_hours") or [])

    def reset(self):
        self.anchor = time.time()

    def phase(self, now=None):
        now = now if now is not None else time.time()
        d = datetime.fromtimestamp(now)
        if self.quiet and d.hour in self.quiet:
            return "quiet", 3600 - (d.minute * 60 + d.second)
        if self.mode == "always" or self.rest == 0:
            return "active", 0
        period = (self.active + self.rest) * 60
        act = self.active * 60
        pos = (now - self.anchor) % period
        return ("active", act - pos) if pos < act else ("rest", period - pos)

    def label(self):
        p, rem = self.phase()
        if p == "active":
            return f"🟢 فعال — تا شروع استراحت: {secs(rem)}" if rem else "🟢 فعال"
        if p == "rest":
            return f"😴 استراحت — تا شروع فعالیت: {secs(rem)}" if rem else "😴 استراحت"
        return f"🌙 ساعت سکوت — تا پایان: {secs(rem)}" if rem else "🌙 ساعت سکوت"


# ─────────────────────────────────────────────
#  سقف‌های پلن  (اگر فایلش نباشد، هیچ محدودیتی نیست)
# ─────────────────────────────────────────────
LIMIT_DEFAULTS = {
    "plan": "",
    "max_channels": 0,
    "max_per_hour": 0,
    "min_gap_sec": 0,
    "exchange": True,
    "initiate": True,
    "max_joins_per_day": 0,
    "ai": True,
    "points": 0,
    "hours_left": 0,
    "points_mode": False,
    "expires_at": 0,
}


class Limits:
    def __init__(self, path=LIMITS_FILE):
        self.path = path
        self.d = dict(LIMIT_DEFAULTS)
        self.active = False
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                self.d.update(json.load(f))
            # حالت پیش‌قدم در این نسخه برای همه پلن‌ها آزاد است.
            self.d["initiate"] = True
            # محدودیت روزانه Join عمداً وجود ندارد.
            self.d["max_joins_per_day"] = 0
            self.active = True
        except Exception as e:
            print(f"⚠️ خواندن {self.path}: {e}")

    def __getitem__(self, k):
        return self.d.get(k, LIMIT_DEFAULTS.get(k))

    def cap_int(self, key, value):
        """مقدار را به سقف می‌چسباند. برمی‌گرداند (مقدار, آیا_محدود_شد)"""
        lim = self.d.get(key) or 0
        if not lim:
            return value, False
        if key == "min_gap_sec":                 # اینجا کف است نه سقف
            return (max(value, lim), value < lim)
        if value == 0 or value > lim:            # ۰ یعنی نامحدود
            return lim, True
        return value, False

    def allowed(self, key):
        return bool(self.d.get(key, True))

    def summary(self):
        if not self.active:
            return ""
        o = []
        if self.d["plan"]:
            o.append(f"📦 پلن: <b>{self.d['plan']}</b>")
        if self.d["max_channels"]:
            o.append(f"📡 حداکثر کانال: {fa(self.d['max_channels'])}")
        if self.d["max_per_hour"]:
            o.append(f"🚦 سقف ارسال: {fa(self.d['max_per_hour'])}/ساعت")
        if self.d["min_gap_sec"]:
            o.append(f"⏱ کف فاصله: {fa(self.d['min_gap_sec'])} ثانیه")
        if self.d["max_joins_per_day"]:
            o.append(f"🔁 سقف جوین: {fa(self.d['max_joins_per_day'])}/روز")
        if not self.d["exchange"]:
            o.append("🔒 تبادل غیرفعال")
        if not self.d["initiate"]:
            o.append("🔒 پیش‌قدم غیرفعال")
        if not self.d["ai"]:
            o.append("🔒 هوش مصنوعی غیرفعال")
        return "\n".join(o)


# ─────────────────────────────────────────────
#  هوش مصنوعی (سازگار با OpenAI / nano-gpt / OpenRouter …)
# ─────────────────────────────────────────────
AI_DEFAULTS = {
    "enabled": True,
    "key": "sk-nry-lgTU-k8Jkm1goQBVCq8-MBolO_xhW6bkBpcPSni2RKs",
    "base_url": "https://nano-gpt.com/api/v1",
    "model": "qwen3.8-27b",
    "temperature": 0.4,
    "max_tokens": 700,
    "smart_detect": True,
    "pv_answer": False,       # AI فقط تحلیل می‌کند؛ به دیگران پیام نمی‌دهد
    "persona": "",
}


class AI:
    def __init__(self, path=AI_FILE):
        self.path = path
        self.cfg = dict(AI_DEFAULTS)
        self.last_error = ""
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    self.cfg.update(json.load(f))
            except Exception as e:
                print(f"⚠️ خواندن {self.path}: {e}")
        if not (self.cfg.get("key") or "").strip():
            self.cfg["key"] = AI_DEFAULTS["key"]

    def save(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
            try:
                os.chmod(self.path, 0o600)
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ ذخیره {self.path}: {e}")

    @property
    def ready(self):
        return bool(self.cfg["enabled"] and self.cfg["key"] and self.cfg["base_url"])

    # ---------- تماس با سرویس ----------
    def chat(self, messages, temperature=None, max_tokens=None, timeout=60):
        """برمی‌گرداند (متن, خطا)"""
        if not self.ready:
            return "", "AI فعال نیست یا کلید ندارد"
        url = self.cfg["base_url"].rstrip("/") + "/chat/completions"
        payload = {
            "model": self.cfg["model"],
            "messages": messages,
            "temperature": (self.cfg["temperature"] if temperature is None
                            else temperature),
            "max_tokens": max_tokens or self.cfg["max_tokens"],
        }
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.cfg["key"],
                     "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
            out = (d["choices"][0]["message"]["content"] or "").strip()
            self.last_error = ""
            return out, ""
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")[:200]
            msg = f"HTTP {e.code}"
            try:
                j = json.loads(body)
                msg += ": " + str((j.get("error") or {}).get("message", body))[:150]
            except Exception:
                msg += ": " + body
            if e.code in (401, 403):
                msg += "\n(کلید پذیرفته نشد — با `.ai key کلید` عوضش کن)"
            self.last_error = msg
            return "", msg
        except urllib.error.URLError as e:
            self.last_error = f"شبکه: {e.reason}"
            return "", self.last_error
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            return "", self.last_error

    async def achat(self, messages, **kw):
        return await asyncio.to_thread(self.chat, messages, **kw)

    # ---------- تشخیص هوشمند پیام ----------
    SNIFF = (
        "تو فقط تحلیل‌گر پیام تبادل تلگرام هستی. هیچ متن پاسخی تولید نکن. "
        "فقط یک JSON خالص و کوتاه بده.\n"
        '{"joined":true/false,"asking":true/false,'
        '"intent":"join_claim|join_request|question|other"}\n'
        "joined=true فقط وقتی طرف درباره خودش صریحاً می‌گوید جوین شدم، عضو شدم، "
        "اومدم، داخل شدم یا عبارت هم‌معنی.\n"
        "عبارت‌های دستوری مثل «جوین شو»، «عضو شو»، «جوین کن»، "
        "«بیا جوین شو» و «برو عضو شو» درخواست از ربات هستند و حتماً "
        "joined=false و intent=join_request هستند. عبارت‌های دوم‌شخص مثل "
        "«جوین شدی بگو بیام» یا «تو عضو شدی؟» هم ادعای Join فرستنده نیستند.\n"
        "اگر صرفاً سوال یا لینک فرستاده، joined=false باشد."
    )

    async def sniff(self, text):
        """تحلیل پیام. اگر AI در دسترس نباشد None برمی‌گرداند."""
        if not (self.ready and self.cfg["smart_detect"]) or not text:
            return None
        out, err = await self.achat(
            [{"role": "system", "content": self.SNIFF},
             {"role": "user", "content": text[:1500]}],
            temperature=0, max_tokens=300, timeout=40)
        if err or not out:
            return None
        raw = out.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.lstrip().lower().startswith("json"):
                raw = raw.lstrip()[4:]
        i, j = raw.find("{"), raw.rfind("}")
        if i < 0 or j <= i:
            return None
        try:
            d = json.loads(raw[i:j + 1])
        except Exception:
            return None
        if not isinstance(d, dict):
            return None
        d["links"] = [str(l) for l in (d.get("links") or []) if l]

        def as_bool(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return bool(v)
            return str(v).strip().lower() in (
                "1", "true", "yes", "y", "بله", "درست")

        d["joined"] = as_bool(d.get("joined"))
        d["asking"] = as_bool(d.get("asking"))
        return d

    def _join_text(self, text):
        t = (text or "").replace("\u200c", "").replace("ي", "ی").replace("ك", "ک").lower()
        return re.sub(r"\s+", " ", t).strip()

    def _has_join_phrase(self, text, phrase):
        """عبارت را با مرز کلمه بررسی می‌کند تا «شدیم» با «شدی» قاطی نشود."""
        return bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text or ""))

    def looks_like_join_request(self, text):
        """دستور «جوین شو» ادعای Join نیست؛ قبل از AI آن را قطعی رد کن."""
        t = self._join_text(text)
        if not t:
            return False
        requests = (
            "جوین شو", "جوین بشو", "جوین کن", "برو جوین", "بیا جوین",
            "عضو شو", "عضو بشو", "عضو کن", "برو عضو", "بیا عضو",
            "جوین شدی", "عضو شدی", "تو جوین شدی", "تو عضو شدی",
            "بگو بیام", "بگو بیا", "join me", "please join", "join شو", "join کن",
        )
        return any(self._has_join_phrase(t, k) for k in requests)

    def looks_like_join(self, text):
        """فقط ادعای انجام‌شدن Join را تشخیص می‌دهد، نه درخواست Join."""
        t = self._join_text(text)
        if not t or self.looks_like_join_request(t):
            return False
        # منفی‌ها اول بررسی شوند تا جمله‌هایی مثل «اومدم ولی عضو نشدم» مثبت نشوند.
        negatives = (
            "جوین نشدم", "جوین نشده", "عضو نشدم", "عضو نشده", "عضو نیستم",
            "هنوز عضو نیستم", "هنوز جوین نشدم", "نیومدم", "نیامدم",
            "جوین نکردم", "عضو نکردم", "not joined", "didn't join",
        )
        if any(self._has_join_phrase(t, k) for k in negatives):
            return False
        claims = (
            "جوین شدم", "جوینشدم", "جوین شدیم", "جوینشدیم", "جوینم",
            "عضو شدم", "عضوشدم", "عضو شدیم", "عضوشدیم", "عضوم",
            "اومدم", "آمدم", "اومدیم", "آمدیم",
            "داخل شدم", "وارد شدم", "جوین کردم", "عضو کانال شدم",
            "joined", "i joined",
        )
        return any(self._has_join_phrase(t, k) for k in claims)

    # ---------- پرسش و پاسخ درباره ربات ----------
    async def ask(self, question, context=""):
        persona = self.cfg.get("persona") or ""
        sysmsg = (
            "تو دستیار داخلی ربات «جفج» هستی؛ یک سلف‌بات تلگرام برای مدیریت "
            "کانال و تبادل. کوتاه، دقیق و فارسی جواب بده. اگر سوال درباره "
            "دستورها یا تنظیمات است، از اطلاعات زیر استفاده کن و دستور دقیق "
            "را بنویس. چیزی که نمی‌دانی را از خودت نساز.\n\n" + context
        )
        if persona:
            sysmsg += "\n\nلحن: " + persona
        return await self.achat(
            [{"role": "system", "content": sysmsg},
             {"role": "user", "content": question[:2000]}])


# ─────────────────────────────────────────────
#  استخراج لینک کانال از متن
# ─────────────────────────────────────────────
_LINK_PATTERNS = [
    re.compile(r"(?:https?://)?t\.me/(?:joinchat/|\+)([A-Za-z0-9_-]{10,})"),
    re.compile(r"(?:https?://)?t\.me/([A-Za-z][A-Za-z0-9_]{3,31})(?![\w/])"),
    re.compile(r"@([A-Za-z][A-Za-z0-9_]{3,31})"),
]
_SKIP = {"joinchat", "share", "addstickers", "proxy", "socks", "iv", "s", "c"}


def extract_links(text):
    """همه لینک‌های کانال داخل متن را برمی‌گرداند (یکتا، به ترتیب)."""
    if not text:
        return []
    out, seen = [], set()
    for m in _LINK_PATTERNS[0].finditer(text):
        v = "https://t.me/+" + m.group(1)
        if v.lower() not in seen:
            seen.add(v.lower())
            out.append(v)
    for pat in _LINK_PATTERNS[1:]:
        for m in pat.finditer(text):
            u = m.group(1)
            if u.lower() in _SKIP:
                continue
            v = "@" + u
            if v.lower() not in seen:
                seen.add(v.lower())
                out.append(v)
    return out


def is_invite(link):
    return "+" in link or "joinchat" in link


def invite_hash(link):
    return link.split("+")[-1].split("/")[-1]


# ─────────────────────────────────────────────
#  راهنما
# ─────────────────────────────────────────────
HELP = """🤖 راهنمای جفج

دستورها را در Saved Messages بفرست. نقطه و اسلش هم قابل استفاده‌اند، اما دستورهای اصلی فارسی هستند.

🏠 خانه و وضعیت
پنل — نمایش پنل اصلی
راهنما — همین راهنما
تنظیمات — تنظیمات کامل
آمار — آمار ارسال
گزارش — رویدادهای اخیر
زنده — بررسی زنده‌بودن سلف

📝 ارسال
ارسال متن — ارسال به صف عادی
ارسال فوری متن — ارسال فوری
ویژه متن — ارسال به صف ویژه

📡 کانال‌ها
کانال @channel — کانال عادی
کانال ویژه @channel — کانال ویژه
کانال‌ها — نمایش کانال‌ها
حذف کانال — حذف کانال بخش فعلی

⚙️ تنظیمات عادی
عادی — ورود به بخش عادی
فعالیت ۶۰ — مدت فعالیت به دقیقه
استراحت ۳۰ — مدت استراحت
سقف ۱۲ — سقف ارسال در ساعت
فاصله ۴۵ ۱۲۰ — فاصله بین ارسال‌ها
سکوت ۰ ۱ ۲ — ساعت‌های سکوت
حالت — تعویض حالت ۲۴ ساعته و چرخه‌ای

👑 تنظیمات ویژه
ویژه — ورود به بخش ویژه
فعالیت ویژه ۶۰
استراحت ویژه ۳۰
سقف ویژه ۳۰
فاصله ویژه ۲۰ ۴۵
سکوت ویژه ۰ ۱
حالت ویژه

⏯ کنترل صف
توقف — توقف ارسال
ادامه — ادامه ارسال
بازنشانی — شروع دوباره چرخه
صف — نمایش صف
حذف ۵ — حذف پیام شماره ۵
پاکسازی — خالی‌کردن صف
تلاش دوباره — تلاش دوباره پیام‌های ناموفق

👥 گروه‌های تبادل
گروه‌ها — نمایش منوی گروه‌ها
افزودن گروه @group — افزودن گروه
حذف گروه @group — حذف یک گروه
حذف همه گروه‌ها — حذف همه گروه‌ها

🔁 تبادل
تبادل — منوی تبادل
تبادل روشن / تبادل خاموش
تبادل خودکار — روشن یا خاموش‌کردن Join خودکار
تبادل پیش‌قدم — اسکن گروه‌ها و پیش‌قدم‌شدن
تبادل اسکن — اسکن فوری
تبادل فهرست — فهرست تبادل‌ها
تبادل منتظر — موارد منتظر
تبادل تأیید ۵ — تأیید یک مورد
تبادل رد ۵ — رد یک مورد
تبادل خروج ۵ — لفت از یک کانال
تبادل حذف ۵ — حذف یک مورد
تبادل ارسال ۵ — ارسال دوباره متن برای Join شماره ۵

⏱ تنظیم تبادل
تبادل هر ۳۰ ثانیه — فاصله پیش‌فرض ثابت بین Joinها
تبادل فاصله ۹۰ ۲۴۰ — فاصله تصادفی بین Joinها
تبادل Join روزانه بدون سقف است.
تبادل سقف ساعتی 60 — سقف جوین در هر ساعت (خاموش پیش‌فرض؛ با «روشن» فعال می‌شود)
تبادل سقف ساعتی روشن / تبادل سقف ساعتی خاموش
تبادل بررسی ۱۵ ۳۰ — بررسی عضویت با فاصله تصادفی ۱۵ تا ۳۰ ثانیه
تبادل زمان پاسخ ۱۵ — تأخیر پاسخ بعد از Join واقعی
تبادل اخطار ۳ — بعد از سه بار نبودن لفت بده (این پیام نیست)
تبادل تعداد یادآوری ۱ — حداکثر یک پیام «عضو نیست»؛ ۰ = بدون پیام
تبادل فاصله یادآوری ۵ ۱۵ — فقط اگر یادآوری بیشتر از یک باشد

📊 گزارش خصوصی تبادل
تبادل گزارش — ورود به منوی گزارش تبادل
تنظیم گزارش روشن — فعال‌کردن گزارش لحظه‌ای در PV
تنظیم گزارش لحظه‌ای — فعال‌کردن گزارش لحظه‌ای در PV
تنظیم گزارش خلاصه — یک گزارش جمعی خودکار
تنظیم گزارش هر 24 — فاصله گزارش خلاصه به ساعت
گزارش خلاصه — ارسال گزارش خلاصه همین حالا
تنظیم گزارش خاموش — خاموش‌کردن گزارش

تبادل اسکن هر ۳۰ ثانیه — اسکن پیش‌قدم؛ اسکن فوری با «تبادل اسکن»
تبادل انتخاب پیام ۲ — پیام دوم از جدیدترین لینک‌ها
تبادل عمق اسکن ۵۰ — چند پیام آخر گروه بررسی شود
تبادل سن لینک ۵ — فقط لینک‌های حداکثر ۵ دقیقه اخیر

💬 متن‌های تبادل
متن‌های تبادل — نمایش منوی متن‌ها
تبادل پیام موفق جوین شدم
تبادل پیام ناموفق اول عضو شو
تبادل پیام انتظار دارم بررسی می‌کنم
تبادل پیام بدون لینک لینک کانالت را بفرست
تبادل پیام متن دلخواه — متن بعد از هر Join موفق
مثال: تبادل پیام جوین شدم جوین شو
تبادل زمان بیا ۰ — تأخیر پیام بیا به ثانیه
برای خاموش‌کردن هر متن، در پایان بنویس: خاموش

🧠 هوش مصنوعی
هوش — وضعیت هوش مصنوعی
هوش روشن / هوش خاموش
هوش تست
هوش تشخیص
هوش پاسخ

📊 پلن
پلن — نمایش محدودیت‌های پلن

🛡 محافظ ریپورت
ریسک — وضعیت و درصد ریسک (ارسال/جوین/لفت/فلاد/…)
ریسک آستانه 75 — آستانه‌ی خاموشی خودکار تبادل
ریسک بازگشت 55 — زیر این درصد دوباره روشن می‌شود
ریسک بررسی — محاسبه‌ی همین لحظه
ریسک روشن / ریسک خاموش — فعال/غیرفعال‌کردن «توقف بر امتیاز» (پیش‌فرض: خاموش)
ریسک پایش روشن / ریسک پایش خاموش — فعال/غیرفعال‌کردن «پایشِ واقعی» (پیش‌فرض: روشن و همیشه فعال)
ریسک ریست — پاک‌کردن وضعیت خاموشی خودکار
"""


def _soft_clean(s):
    """ایموجی و فاصلهٔ اضافه را از دستور برمی‌دارد."""
    s = (s or "").replace("\u200c", " ").replace("\u200b", "")
    s = s.replace("ي", "ی").replace("ك", "ک")
    s = re.sub(r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF"
               r"\U0001F000-\U0001F0FF\u2600-\u26FF\u2300-\u23FF"
               r"🔹👑📡✍🚦🔁📮🧠🔕⏸▶🏠➕🗑📋⏱🎲💬✨⭐⏳🆔🔗👤🟢💎]",
               " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ─────────────────────────────────────────────
#  هسته
# ─────────────────────────────────────────────
class Engine:
    """موتور مستقل از تلگرام — قابل تست"""

    def __init__(self):
        self.st = Settings()
        self.db = DB()
        self.thr = {t: Throttle(self.st.prof(t)) for t in ("standard", "vip")}
        self.cyc = {t: Cycle(self.st.prof(t)) for t in ("standard", "vip")}
        x = self.st["exchange"]
        self.join_thr = Throttle({"min_gap_sec": x["min_join_gap_sec"],
                                  "max_gap_sec": x["max_join_gap_sec"],
                                  "max_per_hour": 0})
        self.ai = AI()
        self.lim = Limits()
        self.apply_limits()
        self.started = int(time.time())
        self.me = None
        self.my_username = ""
        self.my_id = 0
        self.last_error = ""

    def apply_limits(self):
        """سقف‌های پلن را روی تنظیمات فعلی اعمال می‌کند."""
        if not self.lim.active:
            return []
        hit = []
        for tier in ("standard", "vip"):
            p = self.st.prof(tier)
            v, capped = self.lim.cap_int("max_per_hour", p["max_per_hour"])
            if capped:
                p["max_per_hour"] = v
                hit.append(f"سقف ارسال {tier} → {v}/ساعت")
            v, capped = self.lim.cap_int("min_gap_sec", p["min_gap_sec"])
            if capped:
                p["min_gap_sec"] = v
                p["max_gap_sec"] = max(p["max_gap_sec"], v)
                hit.append(f"فاصله {tier} → حداقل {v} ثانیه")
            self.thr[tier].apply(p)
        x = self.st["exchange"]
        if not self.lim.allowed("exchange") and x["enabled"]:
            x["enabled"] = False
            hit.append("تبادل در پلن تو نیست")
        if not self.lim.allowed("initiate") and x["initiate"]:
            x["initiate"] = False
            hit.append("حالت پیش‌قدم در پلن تو نیست")
        # سقف روزانه Join حذف شده است؛ هیچ پلنی این بخش را محدود نمی‌کند.
        x["max_joins_per_day"] = 0
        if not self.lim.allowed("ai") and self.ai.cfg["enabled"]:
            self.ai.cfg["enabled"] = False
            hit.append("هوش مصنوعی در پلن تو نیست")
        if hit:
            self.st.save()
        return hit

    def reload(self, tier):
        self.thr[tier].apply(self.st.prof(tier))
        self.cyc[tier].apply(self.st.prof(tier))
        self.st.save()
        self.apply_limits()

    def log(self, lvl, kind, detail=""):
        if lvl in ("error", "warn"):
            self.last_error = f"{kind}: {str(detail)[:120]}"
        self.db.log(lvl, kind, detail)
        line = f"[{datetime.now():%H:%M:%S}] {lvl.upper():5} {kind} {detail}"
        print(line, flush=True)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def target(self, tier):
        ch = self.st.prof(tier)["channel"]
        if not ch and tier == "vip":
            ch = self.st.prof("standard")["channel"]
        return ch

    # ---------- دستورها (همه رشته برمی‌گردانند) ----------
    def cmd(self, cmd, arg, reply_text=None):
        c = _soft_clean(cmd).lower().strip()
        a0 = (arg or "").strip()
        # «تنظیم کانال» یک فرمان کامل است (با فاصله)
        full = (c + (" " + a0 if a0 else "")).strip()
        if c in ("عادی", "std", "normal", "بخش عادی") and not (a0 or reply_text):
            self.st.data["_menu"] = "standard"
            try:
                self.st.save()
            except Exception:
                pass
            return self.section_text("standard")
        if c in ("ویژه", "وی‌آی‌پی", "vipmenu", "بخش ویژه") and not (a0 or reply_text):
            self.st.data["_menu"] = "vip"
            try:
                self.st.save()
            except Exception:
                pass
            return self.section_text("vip")
        menus = {
            "کانال": self.submenu_channel,
            "تنظیم کانال": self.submenu_channel,
            "تنظیم‌کانال": self.submenu_channel,
            "تنظیمکانال": self.submenu_channel,
            "افزودن": self.submenu_add_channel,
            "افزودن کانال": self.submenu_add_channel,
            "افزودن‌کانال": self.submenu_add_channel,
            "تغییر": self.submenu_add_channel,
            "تغییر کانال": self.submenu_add_channel,
            "تغییر‌کانال": self.submenu_add_channel,
            "حذف": self.submenu_del_channel,
            "حذف کانال": self.cmd_del_channel,
            "حذف‌کانال": self.cmd_del_channel,
            "پاک کردن کانال": self.cmd_del_channel,
            "حذفکانال": self.cmd_del_channel,
            "لیست": self.submenu_list_channel,
            "لیست کانال": self.submenu_list_channel,
            "لیست‌کانال": self.submenu_list_channel,
            "متن": self.submenu_post,
            "تنظیم متن": self.submenu_post,
            "تنظیم‌متن": self.submenu_post,
            "گروه‌ها": self.submenu_groups,
            "گروه ها": self.submenu_groups,
            "افزودن گروه": self.submenu_add_group,
            "ثبت گروه": self.submenu_add_group,
            "حذف گروه": self.cmd_clear_groups,
            "پاک کردن گروه": self.cmd_clear_groups,
            "سقف": self.submenu_limit,
            "سقف ارسال": self.submenu_limit,
            "سقف‌ارسال": self.submenu_limit,
            "گروه": self.submenu_groups,
            "تنظیم گروه": self.submenu_groups,
            "تنظیم‌گروه": self.submenu_groups,
            "چرخه": self.submenu_cycle,
            "نوسان": self.submenu_gap,
            "متن تبادل": self.submenu_ex_msgs,
            "متن‌تبادل": self.submenu_ex_msgs,
            "متن‌های تبادل": self.submenu_ex_msgs,
            "متن های تبادل": self.submenu_ex_msgs,
            "کانال‌ها": self.submenu_list_channel,
            "کانال ها": self.submenu_list_channel,
            "حذف همه گروه‌ها": self.cmd_clear_groups,
            "حذف همه گروه ها": self.cmd_clear_groups,
        }
        if full in menus and not reply_text:
            return menus[full]()
        if c == "تنظیم" and a0.startswith("کانال"):
            return self.submenu_channel()
        if c == "تنظیم" and a0.startswith("متن"):
            return self.submenu_post()
        if c == "تنظیم":
            setting = re.sub(r"\s+", " ", a0.replace("\u200c", " ")).strip()
            if setting.startswith("تبادل "):
                setting = setting[6:].strip()
            if setting.startswith("گزارش"):
                suffix = setting[len("گزارش"):].strip()
                if not suffix:
                    return "برای ورود به منوی گزارش، `تبادل گزارش` را بفرست."
                if suffix in ("روشن", "لحظه‌ای", "لحظه ای"):
                    return self.exchange_cmd("report_live")
                if suffix == "خلاصه":
                    return self.exchange_cmd("report_summary")
                if suffix in ("خاموش", "off"):
                    return self.exchange_cmd("report_off")
                if suffix.startswith("هر "):
                    return self.exchange_cmd("report_every " + suffix[4:].strip())
                if suffix.startswith(("خلاصه الان", "خلاصه همین الان")):
                    return self.exchange_cmd("report_now")
            # سازگاری با تنظیم‌های قدیمی مثل «تنظیم تبادل ...»
            if a0.startswith("تبادل") or a0.startswith("تبادل‌"):
                rest_ex = a0[5:].strip() if a0.startswith("تبادل") else a0[6:].strip()
                return self.exchange_cmd(rest_ex)
        if c == "تنظیم" and a0.startswith("گروه"):
            return self.submenu_groups()
        if c in ("گروه", "گروه‌ها", "گروه ها") and a0:
            return self.exchange_cmd("groups " + a0)
        if c in ("افزودن گروه", "ثبت گروه") and a0:
            return self.exchange_cmd("groups " + a0)
        if c == "افزودن" and a0.startswith("گروه"):
            return self.cmd("گروه", a0[5:].strip(), reply_text)
        if c in ("حذف گروه",) and a0:
            return self.exchange_cmd("removegroup " + a0)
        if c == "حذف" and a0.startswith("همه گروه"):
            return self.cmd_clear_groups()
        if c in ("حذف گروه", "حذف همه گروه‌ها", "حذف همه گروه ها"):
            return self.cmd_clear_groups()
        if c in ("تبادل", "تبادل‌ها", "تبادل ها") and a0:
            return self.exchange_cmd(a0)
        if c == "ارسال" and a0.lower().startswith("فوری"):
            return self.cmd("now", a0[4:].strip(), reply_text)
        if c == "کانال" and (a0.lower() == "ویژه" or
                              a0.lower().startswith(("ویژه ", "ویژه‌"))):
            return self.cmd("setvip", a0[5:].strip(), reply_text)
        if c == "افزودن" and a0.startswith("کانال"):
            return self.submenu_add_channel()
        if c == "تغییر" and a0.startswith("کانال"):
            return self.submenu_add_channel()
        if c == "حذف" and a0.startswith("گروه"):
            return self.cmd("حذف گروه", a0[5:].strip(), reply_text)
        if c == "حذف" and a0.startswith("کانال"):
            return self.cmd("حذف کانال", "", reply_text)
        if c == "لیست" and a0.startswith("کانال"):
            return self.submenu_list_channel()
        if c in ("فعالیت", "استراحت", "سقف", "فاصله", "سکوت", "حالت") \
                and (a0.lower() == "ویژه" or
                     a0.lower().startswith(("ویژه ", "ویژه‌"))):
            return self.cmd(c + " ویژه", a0[5:].strip(), reply_text)
        if c == "سقف" and a0.startswith("ارسال"):
            return self.submenu_limit()
        if c == "متن" and a0.startswith("تبادل"):
            return self.submenu_ex_msgs()
        if c == "نوسان" and not a0:
            return self.submenu_gap()
        arg = a0
        # نام‌های فارسی ساده برای دستورات اصلی
        aliases = {
            "عادی": "post",
            "ارسال": "post", "پست": "post", "ارسال فوری": "now",
            "ویژه": "vip", "وی‌آی‌پی": "vip", "وی ای پی": "vip",
            "پنل": "panel", "خانه": "panel",
            "کانال": "setch", "کانال ویژه": "setvip", "کانال‌ویژه": "setvip",
            "تنظیمکانال": "setch",
            "کانالوِیژه": "setvip", "کانالویژه": "setvip",
            "کانال vip": "setvip", "کانالوی آی پی": "setvip",
            "کانالها": "chans", "کانال‌ها": "chans",
            "توقف": "pause", "ادامه": "resume", "بازنشانی": "reset",
            "صف": "queue", "حذف": "del", "پاکسازی": "clear",
            "تلاش": "retry", "راهنما": "help", "وضعیت": "panel",
            "تنظیمات": "set", "آمار": "stats", "گزارش": "log",
            "زنده": "ping", "پنل": "panel", "تبادل": "ex",
            "فعالیت": "active", "استراحت": "rest", "سقف": "limit",
            "فاصله": "gap", "نوسان": "gap", "سکوت": "quiet", "حالت": "mode",
            "فعالیت vip": "vactive", "استراحت vip": "vrest",
            "فعالیت ویژه": "vactive", "استراحت ویژه": "vrest",
            "سقف ویژه": "vlimit", "فاصله ویژه": "vgap",
            "سکوت ویژه": "vquiet", "حالت ویژه": "vmode",
            "کانال‌ویژه": "setvip", "کانالویژه": "setvip",
            "فعالیت‌ویژه": "vactive", "فعالیتویژه": "vactive",
            "استراحت‌ویژه": "vrest", "استراحتویژه": "vrest",
            "نوسان‌ویژه": "vgap", "نوسانویژه": "vgap",
            "سقف‌ویژه": "vlimit", "سقفویژه": "vlimit",
        }
        c = aliases.get(c, c)

        # ارسال
        if c in ("now", "فوری"):
            body = arg or reply_text
            if not body:
                return "متن را بنویس:\n`ارسال فوری سلام`"
            tgt = self.target("standard")
            if not tgt:
                return "اول کانال را تعیین کن: `کانال @channel`"
            qid = self.db.enqueue(tgt, body, "standard", when=int(time.time()) - 1)
            return f"⚡ فوری به صف رفت (#{fa(qid)}) → `{tgt}`"

        if c in ("id", "آیدی"):
            return "روی همین چت `.id` را از داخل تلگرام بزن؛ آیدی عددی در لایه تلگرام جواب داده می‌شود."

        if c in ("post", "vip"):
            tier = "vip" if c == "vip" else "standard"
            body = arg or reply_text
            if not body:
                return ("متن را بنویس یا روی یک پیام ریپلای کن:\n"
                        + ("`ویژه سلام`" if tier == "vip" else "`ارسال سلام`"))
            tgt = self.target(tier)
            qid = self.db.enqueue(tgt, body, tier)
            if not tgt:
                return (f"📦 ذخیره شد (#{fa(qid)}) — منتظر تعیین کانال.\n"
                        f"هر وقت `{'کانال ویژه' if tier == 'vip' else 'کانال'} @channel` "
                        f"بزنی، خودکار ارسال می‌شود.\n"
                        f"معلق: {fa(self.db.held_count(tier))}")
            ph, rem = self.cyc[tier].phase()
            w = self.thr[tier].wait_time()
            when = ("به‌زودی" if ph == "active" and w <= 0
                    else (f"بعد از {secs(rem)}" if ph != "active" else f"تا {secs(w)} دیگر"))
            return (f"✅ به صف {'VIP 👑' if tier == 'vip' else 'عادی'} اضافه شد (#{fa(qid)})\n"
                    f"مقصد: `{tgt}`\nارسال: {when}\nدر صف: {fa(self.db.pending_count(tier))}")

        # کانال‌ها
        if c in ("setch", "setvip"):
            tier = "vip" if c == "setvip" else "standard"
            if not arg:
                cur = self.st.prof(tier)["channel"] or "تنظیم نشده"
                return (f"کانال فعلی: `{cur}`\n"
                        + ("`کانال ویژه @mychannel`" if tier == "vip"
                           else "`کانال @mychannel`"))
            v = arg.strip().split()[0]
            old_channel = (self.st.prof(tier)["channel"] or "").strip()
            mc = self.lim["max_channels"]
            if mc:
                others = [self.st.prof(t)["channel"]
                          for t in ("standard", "vip") if t != tier]
                cnt = len([c for c in others if c]) + 1
                if cnt > mc:
                    return (f"⚠️ پلن تو حداکثر {fa(mc)} کانال دارد.\n"
                            f"اول یکی را خالی کن یا پلن را ارتقا بده.")
            self.st.prof(tier)["channel"] = v
            self.st.save()
            nm = "VIP 👑" if tier == "vip" else "عادی"
            freed = self.db.assign_target(tier, v)
            moved = self.db.retarget_pending(tier, old_channel, v)
            freed += moved
            if tier == "standard" and not self.st.prof("vip")["channel"]:
                freed += self.db.assign_target("vip", v)
                freed += self.db.retarget_pending("vip", old_channel, v)
            extra = f"\n📦 {fa(freed)} پیام صف به کانال جدید منتقل شد و ارسال می‌شود." if freed else ""
            return f"✅ کانال {nm}: `{v}`{extra}"

        if c == "chans":
            s = self.st.prof("standard")["channel"] or "—"
            v = self.st.prof("vip")["channel"] or "—"
            return f"📡 **کانال‌ها**\n\nعادی: `{s}`\nVIP: `{v}`"

        # تنظیمات
        tune = {
            "active": ("standard", "active"), "vactive": ("vip", "active"),
            "rest": ("standard", "rest"), "vrest": ("vip", "rest"),
            "limit": ("standard", "limit"), "vlimit": ("vip", "limit"),
            "gap": ("standard", "gap"), "vgap": ("vip", "gap"),
            "quiet": ("standard", "quiet"), "vquiet": ("vip", "quiet"),
            "mode": ("standard", "mode"), "vmode": ("vip", "mode"),
        }
        if c in tune:
            return self.tune(*tune[c], arg)

        # کنترل
        if c == "pause":
            self.st["paused"] = True
            self.st.save()
            return "⏸ ارسال متوقف شد.\n`ادامه` برای ادامه."
        if c == "resume":
            self.st["paused"] = False
            self.st.save()
            return "▶️ ارسال ادامه یافت."
        if c == "reset":
            for x in self.cyc.values():
                x.reset()
            return "♻️ چرخه هر دو بخش از الان شروع شد."
        if c == "clear":
            return f"🗑 {fa(self.db.clear_pending())} آیتم از صف حذف شد."
        if c == "retry":
            return f"♻️ {fa(self.db.retry_failed())} آیتم ناموفق دوباره به صف رفت."
        if c == "del":
            try:
                n = self.db.delete_item(num(arg))
            except (ValueError, TypeError):
                return "فرمت: `حذف ۵`"
            return "✅ حذف شد." if n else "چنین آیتمی در صف نیست."

        # تبادل
        if c in ("ex", "tb"):
            return self.exchange_cmd(arg)

        # محافظ ریپورت
        if c in ("risk", "ریسک", "امنی", "حفاظت", "امنیت"):
            out = self.risk_cmd(arg)
            return out if out is not None else self.risk_status_text()

        # نمایش
        if c in ("panel", "p", "start"):
            return self.panel()
        if c == "help":
            return HELP
        if c == "set":
            return self.settings_text()
        if c == "queue":
            return self.queue_text()
        if c == "stats":
            return self.stats_text()
        if c == "log":
            evs = self.db.recent(15)
            if not evs:
                return "رویدادی ثبت نشده."
            ic = {"info": "ℹ️", "warn": "⚠️", "error": "❌", "ok": "✅"}
            return "📜 **رویدادهای اخیر**\n\n" + "\n".join(
                f"{ic.get(e['level'], '•')} `{datetime.fromtimestamp(e['ts']):%H:%M}` "
                f"{e['kind']} {(e['detail'] or '')[:45]}" for e in evs)
        if c in ("plan", "limits", "پلن"):
            if not self.lim.active:
                return "📦 هیچ محدودیتی روی این نسخه نیست."
            sm = (self.lim.summary() or "").replace("<b>", "**").replace("</b>", "**")
            return ("📦 **پلن و سقف‌های تو**\n" + self.LINE_ + "\n"
                    + sm + "\n" + self.LINE_
                    + "\n_برای ارتقا با پشتیبانی تماس بگیر._")

        if c in ("بررسی", "هوش‌بررسی"):
            rest = (arg or "").strip()
            if rest in ("فعال", "روشن", "on"):
                return self.ai_settings_cmd("بررسی فعال")
            if rest in ("خاموش", "off"):
                return self.ai_settings_cmd("بررسی خاموش")
            return self.ai_settings_cmd("بررسی")

        if c in ("متن موفق", "متن‌موفق", "متنموفق", "پیام موفق"):
            return self.exchange_cmd(("پیام موفق " + (arg or "")).strip())
        if c in ("متن ناموفق", "متن‌ناموفق", "متنناموفق", "پیام ناموفق"):
            return self.exchange_cmd(("پیام ناموفق " + (arg or "")).strip())
        if c in ("متن انتظار", "متن‌انتظار", "متنانتظار", "پیام انتظار"):
            return self.exchange_cmd(("پیام انتظار " + (arg or "")).strip())
        if c in ("متن بدون لینک", "متن‌بدون‌لینک", "متنبدونلینک", "پیام بدون لینک"):
            return self.exchange_cmd(("پیام بدون لینک " + (arg or "")).strip())
        if c in ("لیست",) and (not arg or "تبادل" in (arg or "")):
            return self.exchange_cmd("list")
        if c in ("لیست تبادل", "لیست‌تبادل", "لیستتبادل"):
            return self.exchange_cmd("list")

        if c in ("ver", "version", "نسخه"):
            return (f"🧬 نسخه همین پروسه: **{VERSION}**\n"
                    f"ساخت: `{BUILD_TAG}`\n"
                    "اگر این ساخت را نمی‌بینی، هنوز فایل قدیمی اجرا می‌شود.")
        if c == "ping":
            return f"🏓 زنده‌ام — آپ‌تایم {secs(int(time.time()) - self.started)}"

        return None  # دستور ناشناخته → بی‌صدا رد شود

    # ---------- تغییر مقادیر ----------
    def tune(self, tier, field, arg):
        p = self.st.prof(tier)
        nm = "👑 ویژه" if tier == "vip" else "🔹 عادی"

        def label(name):
            return f"{name} ویژه" if tier == "vip" else name

        if field == "mode":
            p["mode"] = "cycle" if p["mode"] == "always" else "always"
            self.reload(tier)
            m = "چرخه‌ای (فعالیت/استراحت)" if p["mode"] == "cycle" else "۲۴ ساعته"
            return f"{nm} — حالت: **{m}**\n{self.brief(tier)}"

        if field == "active":
            if not arg:
                return f"فعالیت فعلی: {dur(p['active_minutes'])}\n`{label('فعالیت')} ۹۰`"
            try:
                v = num(arg)
            except ValueError:
                return f"عدد بده: `{label('فعالیت')} ۶۰`"
            v = max(1, v)
            p["active_minutes"] = v
            if p["rest_minutes"] > 0:
                p["mode"] = "cycle"
            self.reload(tier)
            return f"{nm} — فعالیت: **{dur(v)}**\n{self.brief(tier)}"

        if field == "rest":
            if not arg:
                return (f"استراحت فعلی: {dur(p['rest_minutes'])}\n"
                        f"`{label('استراحت')} ۳۰`  |  `{label('استراحت')} ۰` برای ۲۴ساعته")
            try:
                v = num(arg)
            except ValueError:
                return f"عدد بده: `{label('استراحت')} ۳۰`"
            v = max(0, v)
            p["rest_minutes"] = v
            p["mode"] = "always" if v == 0 else "cycle"
            self.reload(tier)
            t = "بدون استراحت (۲۴ ساعته)" if v == 0 else dur(v)
            return f"{nm} — استراحت: **{t}**\n{self.brief(tier)}"

        if field == "limit":
            if not arg:
                cur = "نامحدود" if not p["max_per_hour"] else f"{fa(p['max_per_hour'])} در ساعت"
                return (f"سقف فعلی: {cur}\n"
                        f"`{label('سقف')} ۱۲`  |  `{label('سقف')} ۰` نامحدود")
            try:
                v = num(arg)
            except ValueError:
                return f"عدد بده: `{label('سقف')} ۱۲`"
            v = max(0, v)
            v, capped = self.lim.cap_int("max_per_hour", v)
            p["max_per_hour"] = v
            self.reload(tier)
            t = "نامحدود" if v == 0 else f"{fa(v)} پیام در ساعت"
            w = (f"\n⚠️ پلن تو تا {fa(self.lim['max_per_hour'])} در ساعت است — روی همان تنظیم شد."
                 if capped else "")
            return f"{nm} — سقف ساعتی: **{t}**{w}\n{self.brief(tier)}"

        if field == "gap":
            if not arg:
                return (f"فاصله فعلی: {fa(p['min_gap_sec'])}–{fa(p['max_gap_sec'])} ثانیه\n"
                        f"`{label('فاصله')} ۴۵ ۱۲۰`")
            try:
                ns = [num(x) for x in arg.split()]
                lo, hi = ns[0], (ns[1] if len(ns) > 1 else ns[0])
            except (ValueError, IndexError):
                return f"فرمت: `{label('فاصله')} ۴۵ ۱۲۰`"
            lo = max(1, lo)
            hi = max(1, hi)
            lo, capped = self.lim.cap_int("min_gap_sec", lo)
            hi = max(lo, hi)
            p["min_gap_sec"], p["max_gap_sec"] = lo, hi
            self.reload(tier)
            w = (f"\n⚠️ کف فاصله در پلن تو {fa(self.lim['min_gap_sec'])} ثانیه است."
                 if capped else "")
            return f"{nm} — فاصله: **{fa(lo)}–{fa(hi)} ثانیه**{w}\n{self.brief(tier)}"

        if field == "quiet":
            if not arg:
                cur = p.get("quiet_hours") or []
                q = "ندارد" if not cur else "، ".join(fa(h) for h in sorted(cur))
                return f"ساعت سکوت: {q}\n`{label('سکوت')} ۰ ۱ ۲ ۳`  |  `{label('سکوت')} خاموش`"
            if arg.lower() in ("off", "خاموش"):
                p["quiet_hours"] = []
            else:
                try:
                    p["quiet_hours"] = sorted({num(x) % 24 for x in arg.split()})
                except ValueError:
                    return f"فرمت: `{label('سکوت')} ۰ ۱ ۲ ۳`"
            self.reload(tier)
            cur = p["quiet_hours"]
            return (f"{nm} — ساعت سکوت: "
                    f"**{'حذف شد' if not cur else '، '.join(fa(h) for h in cur)}**")

    LINE_ = "━━━━━━━━━━━━━━━"

    # ---------- گزارش زنده برای پنل ----------
    def write_status(self, extra=None):
        try:
            c = self.db.counts()
            ec = self.db.ex_counts()
            now_t = int(time.time())
            d = {
                "ts": now_t,
                "pid": os.getpid(),
                "uptime": now_t - self.started,
                "account": self.me or "",
                "username": self.my_username,
                "user_id": self.my_id,
                "paused": bool(self.st["paused"]),
                "channels": {t: self.st.prof(t)["channel"] for t in
                             ("standard", "vip")},
                "queue": {"pending": self.db.pending_count()
                                     - self.db.held_count(),
                          "held": self.db.held_count(),
                          "sent": c.get("sent", 0),
                          "failed": c.get("failed", 0)},
                "sent_24h": self.db.sent_since(now_t - 86400),
                "sent_1h": self.db.sent_since(now_t - 3600),
                "phase": {t: self.cyc[t].phase()[0] for t in ("standard", "vip")},
                "exchange": {"on": bool(self.ex_cfg()["enabled"]),
                             "initiate": bool(self.ex_cfg()["initiate"]),
                             "joined": ec.get("joined", 0),
                             "pending": ec.get("pending", 0),
                             "left": ec.get("left", 0),
                             "today": self.db.ex_joins_today()},
                "ai": bool(self.ai.ready),
                "plan": self.lim["plan"],
                "last_error": self.last_error,
                "risk": self.risk_current()[0],
                "risk_on": bool(self.st["risk"].get("on", True)),
                "risk_trigger": self.st["risk"].get("trigger", 75),
                "risk_resume": self.st["risk"].get("resume", 55),
                "risk_auto_off": bool(self.st["risk"].get("_auto_off")),
                "hard_on": bool(self.st["risk"].get("hard_on", True)),
                "hard_trigger": self.st["risk"].get("hard_trigger", 80),
            }
            _hedge, _hparts, _hmeta = self.real_risk_edge()
            d.update({
                "hard_edge": bool(_hedge),
                "hard_score": _hmeta.get("score", 0),
            })
            if extra:
                d.update(extra)
            tmp = STATUS_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
            os.replace(tmp, STATUS_FILE)
        except Exception as e:
            print("write_status:", e)

    # ---------- تبادل ----------
    def ex_cfg(self):
        return self.st["exchange"]

    def hour_cap_wait(self, now=None):
        """سقف جوین/ساعت: اگر روشن باشد و در یک ساعتِ غلتان به سقف رسیده‌ایم،
        مدتِ مانده تا باز شدن پنجره را برمی‌گرداند؛ وگرنه ۰.
        (این محدودیت آهسته جدا از محافظ ریپورت است و فقط وقتی فعال باشد اجرا می‌شود.)"""
        x = self.ex_cfg()
        if not x.get("hour_cap_on"):
            return 0
        cap = max(1, int(x.get("hour_cap", 60) or 60))
        now = now or int(time.time())
        hour_ago = now - 3600
        n = self.db._x("SELECT COUNT(*) c FROM exchange "
                       "WHERE joined_at IS NOT NULL AND joined_at>=?", (hour_ago,), "one")["c"]
        if n < cap:
            return 0
        # قدیمی‌ترین جوینِ داخل پنجره؛ بعد از ۱ ساعت از آن، جا باز می‌شود.
        oldest = self.db._x("SELECT MIN(joined_at) m FROM exchange "
                            "WHERE joined_at IS NOT NULL AND joined_at>=?", (hour_ago,), "one")
        oldest = (oldest or {}).get("m") or now
        return max(1, int(oldest) + 3600 - now)
    def risk_current(self):
        """(درصد_ریسک, جزئیات_هرمورد, آمار_خام) — بر پایه بازه‌ی زمانی تنظیم‌شده.

        دو لایه:
          1) ریسکِ پایه (بلندمدت) — چقدر در ۲۴ ساعتِ اخیر فعالیت داشته.
          2) ریسکِ پرش (burst) — چقدر در «ساعتِ اخیر» ناگهانی عمل کرده.
        تلگرام به لینکِ نحوه‌ی حرکت (پرشِ ناگهانی) خیلی بیشتر از میانگین حساس است؛
        پس این دو لایه با هم جمع می‌شوند تا هم پیشگیریِ واقعی باشد و هم
        جوینِ عادیِ پخش‌شده در طول روز حساب نشود.
        """
        rc = self.st["risk"]
        window = max(1, int(rc.get("window_hours", 24) or 24)) * 3600
        since = int(time.time()) - window
        hour_ago = int(time.time()) - 3600

        def count(sql, args):
            return self.db._x(sql, args, "one")["c"]

        # ── شمارش بازه‌ی ۲۴ ساعته ──
        sent = count("SELECT COUNT(*) c FROM queue WHERE status='sent' AND sent_at>=?",
                     (since,))
        joins = count("SELECT COUNT(*) c FROM exchange "
                      "WHERE joined_at IS NOT NULL AND joined_at>=?", (since,))
        left = count("SELECT COUNT(*) c FROM events WHERE kind='ex_left' AND ts>=?",
                     (since,))
        failed = count("SELECT COUNT(*) c FROM events WHERE kind='ex_join_fail' AND ts>=?",
                       (since,))
        flood24 = count("SELECT COUNT(*) c FROM events "
                        "WHERE lower(kind) LIKE '%flood%' AND ts>=?", (since,))
        strikes = count("SELECT COUNT(*) c FROM events WHERE kind='ex_strike' AND ts>=?",
                        (since,))
        # ── شمارش بازه‌ی «ساعتِ اخیر» برای تشخیص پرش ──
        joins_h = count("SELECT COUNT(*) c FROM exchange "
                        "WHERE joined_at IS NOT NULL AND joined_at>=?", (hour_ago,))
        flood_h = count("SELECT COUNT(*) c FROM events "
                        "WHERE lower(kind) LIKE '%flood%' AND ts>=?", (hour_ago,))
        left_h = count("SELECT COUNT(*) c FROM events WHERE kind='ex_left' AND ts>=?",
                       (hour_ago,))

        # ── سهمِ پایه (بلندمدت) ──
        BASE = [  # (برچسب, ضریب, سقفِ نقش)
            ("ارسال",        0.02,  4),   # 200 ارسال/روز → 4
            ("جوین",         0.40, 38),   # 95 جوین/روز → 38؛ به‌تنهایی به سقف می‌رسد، نه توقف
            ("لفت",          1.50, 12),   # 8 لفت/روز → 12
            ("خطای جوین",    1.00,  4),   # 4 خطا/روز → 4
            ("فلاد",         7.00, 20),   # 3 فلاد/روز → 20؛ زمینه‌ی خطر
            ("برگشت‌نکردن",  0.30,  2),
        ]
        base_counts = {"ارسال": sent, "جوین": joins, "لفت": left,
                       "خطای جوین": failed, "فلاد": flood24, "برگشت‌نکردن": strikes}
        base = sum(min(cap, float(base_counts[n] or 0) * unit)
                   for n, unit, cap in BASE)

        # ── سهمِ پرش (کوتاه‌مدت) — عاملِ اصلیِ توقف ──
        BURST = [  # (برچسب, ضریب, سقفِ نقش)
            ("پرش جوین (۱ ساعت)",    1.40, 42),   # 30+ جوین/ساعت → 42؛ توقف با یک پرشِ واقعی
            ("پرش فلاد (۱ ساعت)",   30.0, 60),   # 2+ فلاد/ساعت → 60 (فوری)
            ("پرش لفت (۱ ساعت)",     1.5, 10),   # 7+ لفت/ساعت → 10
        ]
        burst_counts = {"پرش جوین (۱ ساعت)": joins_h, "پرش فلاد (۱ ساعت)": flood_h,
                        "پرش لفت (۱ ساعت)": left_h}
        burst = sum(min(cap, float(burst_counts[n] or 0) * unit)
                    for n, unit, cap in BURST)

        risk = round(min(100.0, max(0.0, base + burst)), 1)

        parts = {f"پایه·{n}": round(min(100.0, min(cap, float(base_counts[n] or 0) * unit) / cap * 100), 1)
                 for n, unit, cap in BASE}
        parts.update({f"پرش·{n}": round(min(100.0, min(cap, float(burst_counts[n] or 0) * unit) / cap * 100), 1)
                      for n, unit, cap in BURST})
        meta = {"sent": sent, "joins": joins, "left": left, "failed": failed,
                "flood": flood24, "strikes": strikes, "window": window,
                "joins_1h": joins_h, "flood_1h": flood_h, "left_1h": left_h}
        return risk, parts, meta

    def real_risk_edge(self, now=None):
        """پایشِ سیگنال‌های *واقعی* ریپ شدن اکانت — مستقل از امتیازِ انتزاعی.

        سیگنال‌های واقعی (یعنی تلگرام خودش واکنش نشان داده):
          • FloodWait واقعی (تلگرام خواسته صبر کنی) — قوی‌ترین نشانه‌ی محدود شدن
          • خطاهای پشت‌سرهمِ ورود (تحریمِ حساب از سمت تلگرام)
          • رسیدن به سقف کانال/محدودیتِ حسابی
        وقتی این‌ها در بازه‌ی کوچک تکرار شوند = «مرزِ ریپ» → توقف اجباری.

        برمی‌گرداند (در_مرز_هست, جزئیات, آمار_خام).
        """
        rc = self.st["risk"]
        now = now or int(time.time())
        win = max(5, int(rc.get("hard_window_min", 30) or 30)) * 60
        since = now - win
        since10 = now - 600

        def count(sql, args=()):
            return self.db._x(sql, args, "one")["c"]

        flood = count("SELECT COUNT(*) c FROM events WHERE lower(kind) LIKE '%flood%' AND ts>=?", (since,))
        flood10 = count("SELECT COUNT(*) c FROM events WHERE lower(kind) LIKE '%flood%' AND ts>=?", (since10,))
        # فقط خطاهایِ «محدودیتِ حسابیِ خودِ اکانت» سیگنالِ واقعیِ ریپ هستند؛
        # خطاهایِ خودِ لینکِ خریدار (منقضی/خصوصی/ناموجود) اینجا حساب نمی‌شوند
        # تا توقفِ اجباریِ کاذب رخ ندهد.
        fails = count("SELECT COUNT(*) c FROM events WHERE kind='ex_join_limit' AND ts>=?", (since,))
        fails10 = count("SELECT COUNT(*) c FROM events WHERE kind='ex_join_limit' AND ts>=?", (since10,))
        retries = count("SELECT COUNT(*) c FROM events WHERE kind='ex_join_retry' AND ts>=?", (since,))

        # ── امتیازِ واقعی (از نرخ حوادثِ واقعی، نه از شمارشِ کارِ عادی) ──
        score = 0.0
        score += min(45, flood * 22)          # 1 فلاد در بازه=22، 2=45
        score += min(35, flood10 * 35)        # پرشِ فلاد در ۱۰ دقیقه — محکم‌تر
        score += min(25, fails * 8)           # خطاهای ورود
        score += min(25, fails10 * 14)
        score += min(15, retries * 3)
        score = round(score, 1)

        # ── مرزِ ریپ: یا چند نشانه‌ی هم‌زمان، یا یک نشانه‌ی بسیار قوی ──
        trigger = float(rc.get("hard_trigger", 80))
        #  ۲ فلاد در ۱۰ دقیقه، یا (۱ فلاد + ۲ خطا در ۱۰ دقیقه)، یا ۴+ خطا در ۱۰ دقیقه
        critical = (flood10 >= 2) or (flood >= 1 and fails10 >= 2) or (fails10 >= 4)
        edge = critical or score >= trigger

        parts = {
            f"فلاد در {win // 60}د": flood,
            f"فلاد در ۱۰د": flood10,
            f"خطای ورود در {win // 60}د": fails,
            f"خطای ورود در ۱۰د": fails10,
            f"تلاش مجدد": retries,
        }
        meta = {"flood": flood, "flood_10": flood10, "fails": fails,
                "fails_10": fails10, "retries": retries, "win": win,
                "score": score, "critical": critical}
        return edge, parts, meta

    def risk_status_text(self):
        rc = self.st["risk"]
        risk, parts, meta = self.risk_current()
        x = self.ex_cfg()
        guard_on = bool(rc.get("on", True))
        hard_on = bool(rc.get("hard_on", True))
        edge, rparts, rmeta = self.real_risk_edge()
        ex_on = bool(x["enabled"])
        auto = ("🌑 خاموشِ خودکار توسط محافظ" if rc.get("_auto_off")
                else ("🙌 روشنِ دستی/بدون خاموشی خودکار" if ex_on else "—"))
        if edge and hard_on:
            edge_state = "🔴 **در مرز ریپ — توقف اجباری فعال**"
        elif edge:
            edge_state = "🟠 در مرز ریپ ولی پایش خاموش است — توقف اجباری نمی‌زند"
        else:
            edge_state = "🟢 عادی — در مرز ریپ نیست"
        rtbl = "   ".join(f"{k}: <b>{v}</b>" for k, v in rparts.items())
        o = [
            "🛡 محافظ ریپورت — دو چیزِ جدا",
            "━━━━━━━━━━━━",
            "🔴 **پایشِ واقعی** (همیشه فعال، نگهبانِ اصلی):",
            f"   وضعیت: {edge_state}",
            f"   امتیازِ واقعی: <b>{rmeta['score']}</b>  (مرز {rc.get('hard_trigger', 80)})",
            "   فقط نشانه‌ی واقعیِ محدودیتِ تلگرام را می‌شمارد:",
            "   " + rtbl,
            "   **جوینِ عادی اینجا هیچ نقشی ندارد.**",
            "   `ریسک پایش روشن/خاموش`",
            "━━━━━━━━━━━━",
        ]
        # ── لایه‌ی انتزاعی: اگر خاموش است فقط به‌عنوان «نمایش» بیاید، نه کنترل ──
        if guard_on:
            o += [
                "🟡 **توقف بر امتیاز** (فقط وقتی روشن باشد):",
                f"   امتیازِ انتزاعی: <b>{risk}%</b>  ·  آستانه‌ی خاموشی: "
                f"<b>{rc.get('trigger', 75)}%</b>  ·  بازگشت: <b>{rc.get('resume', 55)}%</b>",
                "   این مدل **علاوه بر فلاد، جوینِ عادی را هم می‌شمارد** "
                "و به آن «درصد» می‌دهد؛ با `ریسک خاموش` غیرفعال می‌شود.",
                f"   بازه‌ی {fa(meta['window'] // 3600)} ساعت · جوین: {fa(meta['joins'])} · "
                f"فلاد: {fa(meta['flood'])} · خطا: {fa(meta['failed'])}",
            ]
        else:
            o += [
                "⚪ **توقف بر امتیاز: خاموش** — فقط برای نمایش:",
                f"   امتیازِ انتزاعی: <b>{risk}%</b> (اگر روشن بود، آستانه‌ی "
                f"خاموشی {rc.get('trigger', 75)}% بود)",
                "   این مدل جوینِ عادی را هم می‌شمارد و به آن «درصد» می‌دهد؛ "
                "**الان هیچ کنترلی ندارد** و چیزی را خاموش نمی‌کند.",
                "   فقط `ریسک روشن` آن را فعال می‌کند.",
            ]
        o += [
            "━━━━━━━━━━━━",
            f"تبادل: {'🟢 روشن' if ex_on else '🔴 خاموش'}   ·   {auto}",
            "",
            "💡 فرقِ اصلی: پایشِ واقعی فقط به **واکنشِ خودِ تلگرام** نگاه می‌کند؛ "
            "توقف بر امتیاز به **مقدارِ کارِ ما** (حتی جوینِ سالم) امتیاز می‌دهد.",
            "",
            "`ریسک بررسی` الان · `ریسک ریست` پاک‌کردن وضعیت",
        ]
        return "\n".join(o)

    def risk_cmd(self, arg):
        rc = self.st["risk"]
        a = re.sub(r"\s+", " ", (arg or "").strip())
        low = a.lower()
        if low in ("on", "روشن", "فعال") or a in ("روشن", "فعال"):
            rc["on"] = True
            self.st.save()
            return "🛡 محافظ ریپورت **روشن** شد."
        if low in ("off", "خاموش", "غیرفعال") or a in ("خاموش", "غیرفعال"):
            rc["on"] = False
            self.st.save()
            return "🛡 محافظ ریپورت **خاموش** شد. (تبادل به‌صورت خودکار دیگر کنترل نمی‌شود)"
        if low.startswith(("trigger", "آستانه", "حد ")) or a.startswith("آستانه"):
            m = re.search(r"(\d+(?:\.\d+)?)", a)
            if not m:
                return "فرمت: `ریسک آستانه 75`"
            val = max(10.0, min(100.0, float(m.group(1))))
            rc["trigger"] = val
            # فاصله‌ی منطقی ۱۵ درصدی: همیشه آستانه‌ی بازگشت پایین‌تر می‌ماند
            resume = float(rc.get("resume", 55))
            if resume >= val - 5:
                rc["resume"] = max(1.0, val - 15)
            self.st.save()
            return (f"🛡 آستانه‌ی خاموشی: <b>{val:.0f}%</b>  ·  "
                    f"بازگشت زیر: <b>{rc['resume']:.0f}%</b>")
        if low.startswith(("resume", "بازگشت")):
            m = re.search(r"(\d+(?:\.\d+)?)", a)
            if not m:
                return "فرمت: `ریسک بازگشت 55`"
            val = max(1.0, min(100.0, float(m.group(1))))
            trigger = float(rc.get("trigger", 75))
            if val >= trigger - 5:
                return (f"❌ آستانه‌ی بازگشت باید دست‌کم ۵ درصد از "
                        f"آستانه‌ی خاموشی ({trigger:.0f}%) کمتر باشد.")
            rc["resume"] = val
            self.st.save()
            return f"🛡 بازگشایی زیر <b>{val:.0f}%</b> شد."
        if low.startswith(("reset", "ریست", "پاک", "بازنشانی")):
            rc["_auto_off"] = False
            rc["_last_off"] = 0
            self.st.save()
            return "🛡 وضعیت خاموشیِ خودکار پاک شد. تبادل با وضعیت فعلی‌اش می‌ماند."
        if low.startswith(("پایش", "hard", "واقعی")) or a.startswith("پایش"):
            # کلمه‌ی «روشن/خاموش» اگر باشد، جهت را تعیین می‌کند؛ وگرنه toggle.
            if "خاموش" in low or "off" in a.lower():
                new = False
            elif "روشن" in low or "on" in a.lower() or "فعال" in low:
                new = True
            else:
                new = not bool(rc.get("hard_on", True))
            rc["hard_on"] = new
            self.st.save()
            return ("🔴 پایشِ واقعیِ ریپ **خاموش** شد — دیگر هیچ‌وقت توقف اجباری نمی‌زند."
                    if not new else
                    "🟢 پایشِ واقعیِ ریپ **روشن** شد — در مرز ریپ توقف اجباری می‌زند.")
        if low in ("check", "now", "بررسی", "الان", "وضعیت"):
            return self.risk_status_text()
        # پیش‌فرض: وضعیت
        return self.risk_status_text()


    def exchange_cmd(self, arg):
        x = self.ex_cfg()
        raw = (arg or "").strip()
        # دستورهای چندکلمه‌ای فارسی باید قبل از split شدن تشخیص داده شوند.
        normalized = re.sub(r"\s+", " ", raw.replace("\u200c", " ")).strip()
        multi = (
            ("متن بدون لینک", "msgnolink"),
            ("متن ناموفق", "msgno"),
            ("متن انتظار", "msgwait"),
            ("متن موفق", "msgok"),
            ("پیام بدون لینک", "msgnolink"),
            ("پیام ناموفق", "msgno"),
            ("پیام انتظار", "msgwait"),
            ("پیام موفق", "msgok"),
            ("پیام بیا", "come"),
            ("پیام", "come"),
            ("زمان بیا", "cometime"),
            ("سقف روزانه", "maxday"),
            ("سقف ساعتی", "hourcap"),
            ("سقف هر ساعت", "hourcap"),
            ("سقف جوین ساعت", "hourcap"),
            ("زمان پاسخ", "response_delay"),
            ("تأخیر پاسخ", "response_delay"),
            ("تعداد یادآوری", "max_reminders"),
            ("حداکثر یادآوری", "max_reminders"),
            ("گزارش لحظه‌ای", "report_live"),
            ("گزارش لحظه ای", "report_live"),
            ("گزارش روشن", "report_live"),
            ("گزارش خلاصه همین الان", "report_now"),
            ("گزارش خلاصه الان", "report_now"),
            ("گزارش خلاصه", "report_now"),
            ("گزارش خاموش", "report_off"),
            ("گزارش الان", "report_now"),
            ("گزارش هر", "report_every"),
            ("گزارش", "report"),
            ("فاصله یادآوری", "reminder_gap"),
            ("نوسان یادآوری", "reminder_gap"),
            ("فاصله تبادل", "gap"),
            ("زمان تبادل", "gap"),
            ("عمق اسکن", "scanlimit"),
            ("سن لینک", "scan_age"),
            ("حداکثر سن لینک", "scan_age"),
            ("انتخاب پیام", "scan_pick"),
            ("اسکن هر", "scanevery"),
            ("بررسی هر", "every"),
            ("گروه‌ها", "groups"),
            ("گروه ها", "groups"),
            ("پیش قدم", "go"),
            ("پیشقدم", "go"),
        )
        sub = rest = ""
        for phrase, canonical in multi:
            if normalized == phrase or normalized.startswith(phrase + " "):
                sub = canonical
                # بخش بعد از فرمان را از متن اصلی بردار تا نیم‌فاصله‌های
                # متن پیام، مثل «می‌کنم»، از بین نرود.
                words = phrase.split()
                pattern = r"^\s*" + r"[\s\u200c]+".join(
                    re.escape(w) for w in words) + r"(?:\s+|\u200c+|$)"
                match = re.match(pattern, raw, flags=re.S)
                if match:
                    rest = raw[match.end():].strip()
                else:
                    rest = normalized[len(phrase):].strip()
                break
        if not sub:
            parts = normalized.split(None, 1)
            sub = parts[0].lower() if parts else ""
            rest = parts[1].strip() if len(parts) > 1 else ""
        ex_aliases = {
            "روشن": "on", "خاموش": "off", "خودکار": "auto",
            "جواب": "reply", "متن": "msg", "پیشقدم": "go",
            "پیش‌قدم": "go", "اسکن": "scan", "ارسال": "replynow",
            "فرستادن": "replynow", "گروهها": "groups",
            "گروه‌ها": "groups", "کلمات": "words", "فاصله": "gap",
            "سقفروزانه": "maxday", "سقف روزانه": "maxday",
            "سقفساعتی": "hourcap", "سقف ساعتی": "hourcap",
            "سقف هر ساعت": "hourcap", "سقف جوین ساعت": "hourcap",
            "بررسی": "check", "فهرست": "list", "منتظرها": "wait",
            "تأیید": "ok", "تایید": "ok", "رد": "no", "خروج": "out",
            "حذف": "del", "اول": "msgfirst", "موفق": "msgok",
            "ناموفق": "msgno", "انتظار": "msgwait", "بدون لینک": "msgnolink",
            "گروه": "groups", "گروه‌ها": "groups", "گروه ها": "groups",
            "افزودن": "add", "اضافه": "add",
            "اخطار": "strikes", "اسکن هر": "scanevery",
            "انتخاب": "scan_pick", "زمان پاسخ": "response_delay", "تأخیر پاسخ": "response_delay",
            "یادآوری": "reminder_gap", "فاصله یادآوری": "reminder_gap",
            "نوسان یادآوری": "reminder_gap", "تعداد یادآوری": "max_reminders",
            "حداکثر یادآوری": "max_reminders",
            "سن لینک": "scan_age", "حداکثر سن لینک": "scan_age",
            "گزارش": "report", "گزارش لحظه‌ای": "report_live",
            "گزارش لحظه ای": "report_live", "گزارش روشن": "report_live",
            "گزارش خلاصه الان": "report_now", "گزارش خلاصه همین الان": "report_now",
            "خلاصه": "report_now",
            "فاصله تبادل": "gap", "زمان تبادل": "gap",
            "بیا": "come", "پیام بیا": "come", "زمان بیا": "cometime",
        }
        sub = ex_aliases.get(sub, sub)
        if sub == "check":
            sub = "every"
        if sub == "scan" and rest:
            rnorm = rest.replace("\u200c", " ").strip()
            if rnorm.startswith("هر "):
                sub, rest = "scanevery", rnorm[3:].strip()
        if sub == "هر":
            sub = "gap"
            rest = re.sub(r"\s*(?:ثانیه|ثانیه‌ای)\s*$", "", rest).strip()

        if not sub:
            return self.exchange_text()

        if sub in ("on", "روشن"):
            if not self.lim.allowed("exchange"):
                return ("🔒 تبادل در پلن فعلی تو نیست.\n"
                        "برای فعال شدن، پلن را ارتقا بده.")
            x["enabled"] = True
            # تصمیم دستیِ کاربر، خاموشیِ خودکارِ محافظ را باطل می‌کند
            self.st["risk"]["_auto_off"] = False
            self.st.save()
            w = ""
            if not self.st.prof("standard")["channel"]:
                w += ("\n\n⚠️ کانال تعیین نشده — بدون آن نمی‌توانم چک کنم طرف "
                      "عضو شده یا نه.\n`کانال @channel`")
            if not any(x[k] for k in ("msg_ok", "msg_no", "msg_wait",
                                      "msg_nolink", "msg_first", "msg_come")):
                w += ("\n\n💬 هنوز متنی برای جواب تعیین نکرده‌ای، پس فعلاً به کسی "
                      "جواب نمی‌دهم (فقط چک و جوین می‌کنم).\n`متن‌های تبادل`")
            return f"🔁 تبادل **روشن** شد.{w}"

        if sub in ("off", "خاموش"):
            x["enabled"] = False
            # خاموشیِ دستی: محافظ نباید دوباره خودکار روشنش کند
            self.st["risk"]["_auto_off"] = False
            self.st.save()
            return "🔁 تبادل **خاموش** شد."

        if sub == "auto":
            x["auto_join"] = not x["auto_join"]
            self.st.save()
            return ("🔁 جوین **خودکار** — هرکه تأیید شد، بدون پرسیدن جوین می‌شوم."
                    if x["auto_join"] else
                    "🔁 **تأیید دستی** — اول به تو خبر می‌دهم، با `تبادل تأیید ۵` جوین می‌شوم.")

        if sub == "reply":
            x["reply"] = not x["reply"]
            self.st.save()
            return f"💬 جواب دادن به طرف: **{'روشن' if x['reply'] else 'خاموش'}**"

        if sub == "replynow":
            if not rest:
                return "برای ارسال دوباره، شماره را بده: `تبادل ارسال ۱`"
            rec = self.db.ex_find(rest)
            if not rec:
                return "تبادل پیدا نشد."
            if rec["status"] != "joined":
                return "این تبادل هنوز Join نشده است."
            x["_reply_now"] = rec["id"]
            self.st.save()
            return f"✅ پیام تبادل `#{fa(rec['id'])}` در نوبت ارسال قرار گرفت."

        if sub in ("msg", "msgs", "متن"):
            return self.ex_msgs_text()

        if sub in ("come", "msgcome"):
            if not rest:
                cur = x.get("msg_come") or x.get("msg_ok") or "— خاموش"
                return (f"متن بعد از Join موفق: {cur}\n"
                        "`تبادل پیام متن دلخواه` برای تغییر\n"
                        "مثال: `تبادل پیام جوین شدم جوین شو`\n"
                        "`تبادل پیام خاموش` برای خاموش‌کردن")
            if rest.lower() in ("off", "خاموش", "پاک", "حذف", "-"):
                x["msg_come"] = ""
                x["msg_first"] = ""
                x["msg_ok"] = ""
                self.st.save()
                return "🚫 پیام بعد از جوین خاموش شد."
            x["msg_come"] = rest
            x["msg_first"] = rest
            # این فرمان، متن موفقیت همه Joinها را یکسان می‌کند؛
            # چه Join آخرین لینک گروه باشد و چه تبادل عادی.
            x["msg_ok"] = rest
            x["reply"] = True
            self.st.save()
            return f"✅ متن بعد از Join ذخیره شد:\n\n{rest}"

        if sub in ("cometime", "come_time"):
            if not rest:
                return (f"تأخیر پیام بعد از جوین: {fa(x.get('come_delay_sec', 0))} ثانیه\n"
                        "`تبادل زمان بیا ۰` = فوری")
            try:
                v = max(0, min(3600, num(rest)))
            except ValueError:
                return "عدد بده: `تبادل زمان بیا ۰`"
            x["come_delay_sec"] = v
            self.st.save()
            return f"⏱ تأخیر پیام «بیا»: **{fa(v)} ثانیه**"

        if sub in ("msgok", "msgno", "msgwait", "msgnolink", "msgfirst"):
            key = {"msgok": "msg_ok", "msgno": "msg_no", "msgwait": "msg_wait",
                   "msgnolink": "msg_nolink", "msgfirst": "msg_first"}[sub]
            pretty = {"msgok": "پیام موفق", "msgno": "پیام ناموفق",
                      "msgwait": "پیام انتظار", "msgnolink": "پیام بدون لینک",
                      "msgfirst": "پیام بیا"}[sub]
            when = {"msgok": "عضو بود و جوین شدم",
                    "msgno": "عضو نبود — جوین نمی‌شوم",
                    "msgwait": "در حال بررسی‌ام",
                    "msgnolink": "کانالش را پیدا نکردم",
                    "msgfirst": "خودم پیش‌قدم شدم و جوین شدم"}[sub]
            command = f"تبادل {pretty}"
            if not rest:
                cur = x[key]
                if cur:
                    return (f"**متن فعلی** ({when}):\n\n{cur}\n\n"
                            f"عوض‌کردن: `{command} متن جدید`\n"
                            f"برداشتن: `{command} خاموش`")
                return (f"**{when}** — متنی تعیین نکرده‌ای، پس چیزی نمی‌فرستم.\n\n"
                        f"`{command} متن دلخواهت`\n\n"
                        "می‌توانی از این‌ها هم استفاده کنی:\n"
                        "`{name}` اسم طرف • `{channel}` کانال طرف • "
                        "`{mychannel}` کانال خودت")
            if rest.lower() in ("off", "خاموش", "پاک", "حذف", "-"):
                x[key] = ""
                if sub == "msgfirst":
                    x["msg_come"] = ""
                self.st.save()
                return f"🚫 برداشته شد — دیگر {when} چیزی نمی‌فرستم."
            x[key] = rest
            if sub == "msgfirst":
                x["msg_come"] = rest
            x["reply"] = True
            self.st.save()
            return f"✅ ذخیره شد ({when}):\n\n{rest}"

        if sub in ("go", "پیشقدم"):
            if not x["initiate"] and not self.lim.allowed("initiate"):
                return ("🔒 حالت پیش‌قدم در پلن فعلی تو نیست.\n"
                        "برای فعال شدن، پلن را ارتقا بده.")
            x["initiate"] = not x["initiate"]
            self.st.save()
            if not x["initiate"]:
                return "🚶 حالت پیش‌قدم **خاموش** شد — فقط منتظر ریپلای دیگران می‌مانم."
            w = ""
            if not x["groups"]:
                w += ("\n\n⚠️ گروهی تعیین نکرده‌ای — جایی برای اسکن ندارم."
                      "\n`افزودن گروه @tabadol`")
            if not (x.get("msg_come") or x.get("msg_first")):
                w += ("\n\n💬 متن بعد از جوین را تعیین نکرده‌ای، پس جوین می‌شوم "
                      "ولی چیزی نمی‌گویم.\n`تبادل پیام بیا`")
            return (f"🚶 حالت پیش‌قدم **روشن** شد.\n"
                    f"هر {secs(max(30, int(x.get('scan_every_sec', 30) or 30)))} گروه‌ها را نگاه می‌کنم، "
                    f"کانال‌ها را جوین می‌شوم و متنت را ریپلای می‌زنم.{w}")

        if sub in ("scanevery",):
            if not rest:
                sec = max(30, int(x.get("scan_every_sec", 30) or 30))
                return (f"هر {secs(sec)} اسکن می‌کنم\n"
                        "`تبادل اسکن هر 30 ثانیه`")
            raw_scan = rest.strip()
            is_seconds = "ثانیه" in raw_scan
            raw_scan = re.sub(r"\s*(?:ثانیه|ثانیه‌ای|دقیقه|دقیقه‌ای)\s*$", "", raw_scan).strip()
            try:
                v = max(1, num(raw_scan))
            except ValueError:
                return "فرمت: `تبادل اسکن هر 30 ثانیه` یا `تبادل اسکن هر 1 دقیقه`"
            sec = max(30, v if is_seconds else v * 60)
            x["scan_every_sec"] = sec
            x["scan_every_min"] = max(1, (sec + 59) // 60)
            self.st.save()
            return f"🔍 اسکن پیش‌قدم هر **{secs(sec)}**"

        if sub in ("scanlimit", "عمق", "عمق اسکن"):
            if not rest:
                return (f"هر بار {fa(x['scan_limit'])} پیام آخر را می‌بینم\n"
                        "`تبادل عمق اسکن ۵۰`")
            try:
                v = max(1, min(200, num(rest)))
            except ValueError:
                return "عدد بده: `تبادل عمق اسکن ۵۰`"
            x["scan_limit"] = v
            self.st.save()
            return f"🔍 عمق اسکن: **{fa(v)} پیام**"

        if sub == "scan_age":
            current_min = max(1, int(x.get("scan_max_age_sec", 300) or 300) // 60)
            if not rest:
                return (f"سن مجاز لینک: حداکثر {fa(current_min)} دقیقه\n"
                        "`تبادل سن لینک 5`")
            is_hours = "ساعت" in rest
            raw_age = re.sub(r"\s*(?:ساعت|ساعته|دقیقه|دقیقه‌ای)\s*$", "", rest).strip()
            try:
                value = max(1, min(168 if is_hours else 1440, num(raw_age)))
            except ValueError:
                return "عدد بده: `تبادل سن لینک 5`"
            seconds = value * (3600 if is_hours else 60)
            x["scan_max_age_sec"] = seconds
            x["scan_age_version"] = 1
            self.st.save()
            unit = "ساعت" if is_hours else "دقیقه"
            return f"🔍 فقط لینک‌های حداکثر **{fa(value)} {unit}** اخیر بررسی می‌شوند."

        if sub == "scan_pick":
            if not rest:
                return (f"انتخاب پیام: مورد {fa(x.get('scan_pick', 2) or 2)} از جدیدترین لینک‌ها\n"
                        "`تبادل انتخاب پیام 2` یعنی پیام یکی‌مانده‌به‌آخر")
            try:
                v = max(1, min(200, num(rest)))
            except ValueError:
                return "عدد بده: `تبادل انتخاب پیام 2`"
            x["scan_pick"] = v
            self.st.save()
            return f"✅ پیام شماره {fa(v)} از جدیدترین لینک‌ها انتخاب می‌شود."

        if sub == "scan":
            if not x["enabled"]:
                return "اول `تبادل روشن` را بفرست، بعد `تبادل اسکن` را بزن."
            x["_scan_now"] = True
            return "🔍 اسکن فوری در نوبت — نتیجه را همین‌جا می‌گویم."

        if sub in ("words", "کلمات"):
            if rest.lower().startswith("خاموش"):
                rest = "off"
            if not rest:
                w = x["words"]
                return ("🔤 **کلمات کلیدی**\n\n" +
                        ("فقط ریپلای‌هایی که یکی از این‌ها را دارند بررسی می‌شوند:\n"
                         + "، ".join(f"`{i}`" for i in w)
                         if w else "خالی — به **هر** ریپلایی روی پیام تو واکنش نشان می‌دهم.") +
                        "\n\n`تبادل کلمات جوین شدم | اومدم | عضو شدم`"
                        "\n`تبادل کلمات خاموش` برای برداشتن")
            if rest.lower() in ("off", "خاموش", "پاک", "-"):
                x["words"] = []
            else:
                sep = "|" if "|" in rest else ("،" if "،" in rest else ",")
                x["words"] = [w.strip() for w in rest.split(sep) if w.strip()]
            self.st.save()
            w = x["words"]
            return ("🔤 کلمات کلیدی: " +
                    ("، ".join(f"`{i}`" for i in w) if w
                     else "برداشته شد — هر ریپلایی بررسی می‌شود"))

        if sub == "removegroup":
            target = rest.strip().lower()
            before = self.ex_cfg().get("groups") or []
            kept = [g for g in before if g.strip().lstrip("@").lower() != target.lstrip("@")]
            self.ex_cfg()["groups"] = kept
            self.st.save()
            if len(kept) == len(before):
                return "این گروه در فهرست نبود."
            return f"✅ گروه حذف شد: {rest}"

        if sub == "groups":
            # گروه‌ها با «افزودن گروه» هم قابل ثبت هستند.
            if rest.lower().startswith("افزودن "):
                rest = rest[7:].strip()
            if not rest:
                g = x["groups"]
                return ("📡 گروه‌های رصدشده: " +
                        ("، ".join(f"`{i}`" for i in g) if g else "هیچ — فقط پیام خصوصی") +
                        "\n\n`افزودن گروه @g1 @g2`  |  `حذف همه گروه‌ها`")
            if rest.lower() in ("off", "خاموش", "none"):
                x["groups"] = []
            else:
                current = list(x.get("groups") or [])
                for group in (w.strip() for w in rest.split() if w.strip()):
                    if group.lower() not in {g.lower() for g in current}:
                        current.append(group)
                x["groups"] = current
            self.st.save()
            g = x["groups"]
            return ("📡 گروه‌ها: " + ("، ".join(f"`{i}`" for i in g) if g
                    else "پاک شد — فقط پیام خصوصی"))

        if sub == "gap":
            if not rest:
                return (f"فاصله جوین: {fa(x['min_join_gap_sec'])}–"
                        f"{fa(x['max_join_gap_sec'])} ثانیه\n"
                        f"`تبادل فاصله {fa(x['min_join_gap_sec'])} {fa(x['max_join_gap_sec'])}`\n"
                        "برای فاصله ثابت: `تبادل هر ۳۰ ثانیه`")
            rest = re.sub(r"\s*(?:ثانیه|ثانیه‌ای)\s*$", "", rest).strip()
            try:
                ns = [num(v) for v in rest.split()]
                lo = max(1, ns[0])
                hi = max(lo, ns[1] if len(ns) > 1 else ns[0])
            except (ValueError, IndexError):
                return "فرمت: `تبادل فاصله ۹۰ ۲۴۰` یا `تبادل هر ۱۲۰ ثانیه`"
            x["min_join_gap_sec"], x["max_join_gap_sec"] = lo, hi
            self.st.save()
            self.join_thr.apply({"min_gap_sec": lo, "max_gap_sec": hi, "max_per_hour": 0})
            return f"⏱ فاصله جوین: **{fa(lo)}–{fa(hi)} ثانیه**"

        if sub == "reminder_gap":
            if not rest:
                return (f"فاصله یادآوری: {fa(x.get('reminder_min_sec', 5))} تا "
                        f"{fa(x.get('reminder_max_sec', 15))} ثانیه\n"
                        "`تبادل فاصله یادآوری ۵ ۱۵`")
            rest = re.sub(r"\s*(?:ثانیه|ثانیه‌ای)\s*$", "", rest).strip()
            try:
                ns = [num(v) for v in rest.split()]
                lo = max(1, ns[0])
                hi = max(lo, ns[1] if len(ns) > 1 else ns[0])
            except (ValueError, IndexError):
                return "فرمت: `تبادل فاصله یادآوری ۵ ۱۵`"
            x["reminder_min_sec"], x["reminder_max_sec"] = lo, hi
            self.st.save()
            return f"🔔 فاصله یادآوری: **{fa(lo)}–{fa(hi)} ثانیه**"

        if sub == "response_delay":
            if not rest:
                return (f"تأخیر پاسخ بعد از Join: {fa(x.get('response_delay_sec', 15))} ثانیه\n"
                        "`تبادل زمان پاسخ 15`")
            rest = re.sub(r"\s*(?:ثانیه|ثانیه‌ای)\s*$", "", rest).strip()
            try:
                v = max(0, min(3600, num(rest)))
            except ValueError:
                return "عدد بده: `تبادل زمان پاسخ 15`"
            x["response_delay_sec"] = v
            self.st.save()
            return f"⏱ تأخیر پاسخ: **{fa(v)} ثانیه**"

        if sub == "maxday":
            x["max_joins_per_day"] = 0
            self.st.save()
            return "♾️ سقف روزانه Join حذف شده است — Join نامحدود است."

        if sub == "hourcap":
            on = bool(x.get("hour_cap_on", False))
            cap = int(x.get("hour_cap", 60) or 60)
            # اگر عددی آمده، اول مقدار را تنظیم کن و فعالش کن.
            rest_num = re.sub(r"\s*(?:جوین|جوین|بار)\s*$", "", (rest or "").strip())
            if rest_num and (rest_num.isdigit() or re.fullmatch(r"[۰-۹]+", rest_num)):
                try:
                    cap = max(1, min(5000, num(rest_num)))
                except ValueError:
                    pass
                x["hour_cap"] = cap
                x["hour_cap_on"] = False
                self.st.save()
                return (f"⚙️ سقف جوین/ساعت روی **{fa(cap)}** ست شد — هنوز **خاموش** است. "
                        f"برای فعال‌کردن: `تبادل سقف ساعتی روشن`")
            if rest_num.lower() in ("on", "روشن", "فعال"):
                x["hour_cap_on"] = True
                self.st.save()
                return (f"✅ سقف جوین/ساعت **روشن** شد. در یک ساعتِ غلتان بیشتر از "
                        f"**{fa(cap)}** جوین نمی‌زنم و تا باز شدن پنجره صبر می‌کنم.\n"
                        f"غیرفعال: `تبادل سقف ساعتی خاموش`")
            if rest_num.lower() in ("خاموش", "off"):
                x["hour_cap_on"] = False
                x["_hour_cap_blocked"] = 0
                self.st.save()
                return (f"🔓 سقف جوین/ساعت **خاموش** شد — دوباره آزادانه و بدون سقف ساعتی "
                        f"جوین می‌زنم (فقط محافظ ریپورت بالای سر است).")
            # بدون آرگومان: نمایش وضعیت
            if on:
                return (f"🟢 سقف جوین/ساعت **روشن**: حداکثر {fa(cap)} جوین در هر ساعت. "
                        f"`تبادل سقف ساعتی خاموش` برای برداشتن.")
            return (f"⚪ سقف جوین/ساعت **خاموش** (پیش‌فرض — فقط با دستور فعال می‌شود).\n"
                    f"عددِ امنِ پیشنهادی: **{fa(cap)}** جوین در ساعت.\n"
                    f"فعال‌کردن: `تبادل سقف ساعتی روشن`  ·  تغییر عدد: `تبادل سقف ساعتی 60`")

        if sub == "every":
            lo = max(1, int(x.get("check_min_sec", 15) or 15))
            hi = max(lo, int(x.get("check_max_sec", 30) or 30))
            if not rest:
                if lo == hi:
                    return (f"هر {fa(lo)} ثانیه چک می‌شود\n"
                            "`تبادل بررسی 15 30` برای حالت تصادفی")
                return (f"چک عضویت: تصادفی بین {fa(lo)} تا {fa(hi)} ثانیه\n"
                        "`تبادل بررسی 15 30`")
            rest = re.sub(r"\s*(?:ثانیه|ثانیه‌ای)\s*$", "", rest).strip()
            rest = re.sub(r"^(?:تصادفی|نوسانی|رندوم)\s+", "", rest).strip()
            try:
                ns = [num(v) for v in rest.split()]
                lo, hi = max(1, ns[0]), max(1, ns[1] if len(ns) > 1 else ns[0])
                hi = max(lo, hi)
            except (ValueError, IndexError):
                return "فرمت: `تبادل بررسی 15 30` یا `تبادل بررسی 20`"
            x["check_min_sec"], x["check_max_sec"] = lo, hi
            # برای سازگاری با نسخه‌های قدیمی نگه داشته می‌شود؛ موتور جدید
            # همیشه min/max را استفاده می‌کند.
            x["check_interval_sec"] = hi if lo == hi else 0
            # تغییر تنظیم، چک همه موارد انجام‌شده را از نو زمان‌بندی می‌کند.
            for r in self.db.ex_list("joined", 200):
                self.db.ex_set(r["id"], next_check=0)
            self.st.save()
            return (f"🔄 چک عضویت: "
                    f"{'هر ' + fa(lo) + ' ثانیه' if lo == hi else 'تصادفی بین ' + fa(lo) + ' تا ' + fa(hi) + ' ثانیه'}")

        if sub in ("max_reminders", "reminders"):
            if not rest:
                v = max(0, int(x.get("max_reminders", 1) or 0))
                return (f"حداکثر پیام «عضو نیست»: {fa(v)} بار\n"
                        "`تبادل تعداد یادآوری ۱` — `۰` یعنی بدون پیام")
            rest = re.sub(r"\s*(?:بار|پیام)\s*$", "", rest).strip()
            try:
                v = max(0, min(3, num(rest)))
            except ValueError:
                return "عدد بده: `تبادل تعداد یادآوری ۱`"
            x["max_reminders"] = v
            self.st.save()
            return (f"🔔 حداکثر یادآوری: **{fa(v)} بار**"
                    + (" — فقط بررسی بی‌صدا" if v == 0 else ""))

        if sub in ("report", "report_status"):
            mode = x.get("report_mode", "live")
            label = {"live": "لحظه‌ای در PV", "summary": "خلاصه خودکار در PV", "off": "خاموش"}.get(mode, mode)
            return (f"📊 گزارش خصوصی تبادل: **{label}**\n"
                    "مقصد: Saved Messages همین اکانت\n\n"
                    "`تبادل گزارش` — ورود به منو\n"
                    "`تنظیم گزارش روشن`\n"
                    "`تنظیم گزارش لحظه‌ای`\n"
                    "`تنظیم گزارش خلاصه`\n"
                    "`گزارش خلاصه` — ارسال همین حالا\n"
                    "`تنظیم گزارش خاموش`")

        if sub == "report_live":
            x["report_mode"] = "live"
            x["report_last_sent"] = int(time.time())
            self.st.save()
            return "📊 گزارش خصوصی روی حالت **لحظه‌ای** قرار گرفت."

        if sub == "report_summary":
            x["report_mode"] = "summary"
            x["report_last_sent"] = int(time.time())
            self.st.save()
            return ("📊 گزارش خصوصی روی حالت **خلاصه خودکار** قرار گرفت.\n"
                    f"فاصله فعلی: {secs(int(x.get('report_summary_interval_sec', 86400) or 86400))}")

        if sub == "report_off":
            x["report_mode"] = "off"
            self.st.save()
            return "🔕 گزارش خصوصی تبادل خاموش شد؛ پاسخ ثبت‌شده به طرف همچنان ارسال می‌شود."

        if sub == "report_now":
            x["_report_now"] = True
            return "📊 خلاصه گزارش در نوبت ارسال به PV قرار گرفت."

        if sub == "report_every":
            if not rest:
                return (f"فاصله خلاصه: {secs(int(x.get('report_summary_interval_sec', 86400) or 86400))}\n"
                        "`تبادل گزارش هر 24` یعنی هر ۲۴ ساعت")
            raw_hours = re.sub(r"\s*(?:ساعت|ساعته)\s*$", "", rest).strip()
            try:
                hours = max(1, min(168, num(raw_hours)))
            except ValueError:
                return "عدد بده: `تبادل گزارش هر 24`"
            x["report_summary_interval_sec"] = hours * 3600
            x["report_mode"] = "summary"
            x["report_last_sent"] = int(time.time())
            self.st.save()
            return f"📊 خلاصه گزارش هر **{fa(hours)} ساعت** ارسال می‌شود."

        if sub == "strikes":
            if not rest:
                return (f"بعد از {fa(x['max_strikes'])} بار نبودن لفت می‌دهم\n"
                        "`تبادل اخطار ۳`")
            try:
                v = max(1, num(rest))
            except ValueError:
                return "عدد بده: `تبادل اخطار ۳`"
            x["max_strikes"] = v
            self.st.save()
            return f"⚠️ بعد از **{fa(v)} بار** نبودن، لفت می‌دهم."

        if sub in ("list", "l", "فهرست"):
            return self.ex_list_text()
        if sub in ("wait", "pending", "منتظر"):
            return self.ex_list_text("pending")
        if sub == "joined":
            return self.ex_list_text("joined")
        if sub == "left":
            return self.ex_list_text("left")

        if sub == "add":
            if not rest:
                return "`تبادل افزودن @channel`"
            links = extract_links(rest)
            if not links:
                return "لینک معتبری پیدا نکردم."
            rec, new = self.db.ex_add(None, "دستی", links[0])
            if not new:
                return f"قبلاً ثبت شده: `#{fa(rec['id'])}` — {rec['status']}"
            self.db.ex_set(rec["id"], note="دستی")
            return (f"✅ ثبت شد `#{fa(rec['id'])}` → `{links[0]}`\n"
                    f"با `تبادل تأیید {fa(rec['id'])}` جوین می‌شوم.")

        if sub in ("ok", "no", "out", "del"):
            if not rest:
                return f"`تبادل {sub} ۵`"
            rec = self.db.ex_find(rest)
            if not rec:
                return "پیدا نشد."
            if sub == "no":
                self.db.ex_set(rec["id"], status="rejected")
                return f"🚫 `#{fa(rec['id'])}` رد شد."
            if sub == "del":
                self.db.ex_delete(rec["id"])
                return f"🗑 `#{fa(rec['id'])}` حذف شد."
            if sub == "ok":
                self.db.ex_set(rec["id"], status="approved", strikes=0)
                return f"✅ `#{fa(rec['id'])}` تأیید شد — تو نوبت جوین."
            self.db.ex_set(rec["id"], status="leaving")
            return f"👋 `#{fa(rec['id'])}` تو نوبت لفت."

        if sub == "check":
            n = 0
            for r in self.db.ex_list("joined", 200):
                self.db.ex_set(r["id"], last_check=0, next_check=0)
                n += 1
            return f"🔄 {fa(n)} تبادل برای چک فوری علامت خورد."

        return (f"زیر‌دستور ناشناخته: `{sub}`\n`تبادل` برای وضعیت • "
                "`راهنما` برای راهنما")

    def exchange_text(self):
        x = self.ex_cfg()
        c = self.db.ex_counts()
        ch = self.st.prof("standard")["channel"]
        today = self.db.ex_joins_today()
        # Join روزانه عمداً سقف ندارد.
        groups = x.get("groups") or []
        lines = [
            "🔁 تبادل",
            "━━━━━━━━━━━━━━",
            f"وضعیت: {'روشن' if x['enabled'] else 'خاموش'}",
            f"جوین خودکار: {'روشن' if x['auto_join'] else 'تأیید دستی'}",
            f"کانال من: {ch or 'تنظیم نشده'}",
            f"جوین امروز: {fa(today)} — بدون سقف",
            f"سقف جوین/ساعت: {'روشن' + (' · ' + fa(x.get('hour_cap', 60)) + ' در ساعت' if x.get('hour_cap_on') else '') if x.get('hour_cap_on') else 'خاموش (پیش‌فرض)'}   `تبادل سقف ساعتی`",
            f"فاصله Join: {fa(x['min_join_gap_sec'])} تا {fa(x['max_join_gap_sec'])} ثانیه",
            f"گزارش خصوصی: {'لحظه‌ای' if x.get('report_mode', 'live') == 'live' else ('خلاصه' if x.get('report_mode') == 'summary' else 'خاموش')} در PV",
            f"پیام عضو‌نشده: حداکثر {fa(max(0, int(x.get('max_reminders', 1) or 0)))} بار",
            f"فاصله یادآوری اضافه: {fa(x.get('reminder_min_sec', 5))} تا {fa(x.get('reminder_max_sec', 15))} ثانیه",
            f"بررسی عضویت: تصادفی {fa(x.get('check_min_sec', 15))} تا {fa(x.get('check_max_sec', 30))} ثانیه",
            f"پاسخ بعد از Join واقعی: {fa(x.get('response_delay_sec', 15))} ثانیه",
            f"انتخاب پیام: مورد {fa(x.get('scan_pick', 2) or 2)} از جدیدترین‌ها",
            f"اسکن گروه: هر {secs(max(30, int(x.get('scan_every_sec', 30) or 30)))}",
            f"سن مجاز لینک: حداکثر {fa(max(1, int(x.get('scan_max_age_sec', 300) or 300)) // 60)} دقیقه",
            f"گروه‌های ثبت‌شده: {fa(len(groups))}",
            f"تبادل‌های انجام‌شده: {fa(c.get('joined', 0))}",
            f"در صف Join: {fa(c.get('approved', 0))}",
            "",
            "🟢 حالت عادی:",
            "وقتی طرف روی پیام تو ریپلای می‌کند و جبران را اعلام می‌کند، عضویت بررسی می‌شود و سپس کانال او Join می‌شود.",
            "در حالت عادی، گروه‌ها خودکار اسکن نمی‌شوند.",
            "",
            "🚶 حالت پیش‌قدم:",
            "از هر گروه ثبت‌شده، آخرین پیام دارای لینک خوانده می‌شود و لینک در نوبت Join قرار می‌گیرد.",
            "",
            "📌 دستورهای اصلی:",
            "روشن: `تبادل روشن`",
            "خاموش: `تبادل خاموش`",
            "پیش‌قدم: `تبادل پیش‌قدم`",
            "جوین خودکار: `تبادل خودکار`",
            "گروه‌ها: `گروه‌ها`",
            "متن‌ها: `متن‌های تبادل`",
            "فهرست: `تبادل فهرست`",
            "ورود به منوی گزارش: `تبادل گزارش`",
            "گزارش لحظه‌ای: `تنظیم گزارش لحظه‌ای`",
            "گزارش خلاصه: `تنظیم گزارش خلاصه`",
            "گزارش خلاصه همین حالا: `گزارش خلاصه`",
            "فاصله Join: `تبادل فاصله`",
            "نوسان یادآوری: `تبادل فاصله یادآوری 5 15`",
            "اسکن فوری: `تبادل اسکن`",
            "ارسال دوباره پیام: `تبادل ارسال شماره`",
            "",
            "🧠 تشخیص هوشمند: " + ("روشن" if self.ai.ready else "خاموش"),
            "↩️ بازگشت: `عادی`",
        ]
        return "\n".join(lines)

    def ex_msgs_text(self):
        x = self.ex_cfg()
        sections = [
            ("🟢 وقتی ربات در پیش‌قدم با موفقیت Join شد چه بگوید؟",
             "تبادل پیام بیا جوین شدم", "msg_come"),
            ("✅ وقتی تبادل عادی موفق شد چه بگوید؟",
             "تبادل پیام موفق اومدم بیا", "msg_ok"),
            ("❌ وقتی طرف عضو کانال نبود چه بگوید؟",
             "تبادل پیام ناموفق اول عضو شو", "msg_no"),
            ("⏳ وقتی بررسی هنوز تمام نشده چه بگوید؟",
             "تبادل پیام انتظار دارم بررسی می‌کنم", "msg_wait"),
            ("🔗 وقتی لینک طرف پیدا نشد چه بگوید؟",
             "تبادل پیام بدون لینک لینک کانالت را بفرست", "msg_nolink"),
        ]
        lines = [
            "💬 تنظیم متن‌های تبادل",
            "━━━━━━━━━━━━━━",
            "توضیح هر مورد بالا نوشته شده است.",
            "دستور نمونه را کپی کن و متن آخر آن را هرطور خواستی تغییر بده.",
            "بین فرمان و متن فقط فاصله لازم است؛ ویرگول لازم نیست.",
        ]
        for title, command, key in sections:
            lines += ["", title, "دستور آماده برای کپی:", f"`{command}`",
                      f"متن فعلی: {x.get(key) or 'تنظیم نشده'}"]
        lines += ["", "فرمان عمومی «تبادل پیام» متن موفقیت هر دو نوع Join را تنظیم می‌کند.",
                  "خاموش‌کردن متن عمومی: `تبادل پیام خاموش`",
                  "متغیرها: `{name}` نام طرف  ·  `{channel}` کانال طرف  ·  `{mychannel}` کانال من",
                  f"پاسخ‌دادن: {'روشن' if x['reply'] else 'خاموش'}  ·  تغییر: `تبادل جواب`"]
        return "\n".join(lines)

    def _day_start(self):
        return int(time.mktime(datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0).timetuple()))

    def ex_report_text(self, since=None):
        """متن گزارش جمعی؛ مقصد نهایی در لایه تلگرام PV/Saved Messages است."""
        since = self._day_start() if since is None else int(since)
        c = self.db.ex_report_counts(since)
        interval_label = "امروز" if since == self._day_start() else "از گزارش قبلی"
        return "\n".join([
            "📊 گزارش کامل تبادل جفج",
            "━━━━━━━━━━━━━━━━",
            f"🕒 بازه گزارش: {interval_label}",
            "",
            f"✅ کانال‌های Join‌شده: {fa(c['joined'])}",
            f"🚶 پیش‌قدم موفق: {fa(c['out_joined'])}",
            f"👥 جذب موفق تبادل: {fa(c['in_joined'])} نفر",
            f"👋 کانال‌های لفت‌داده‌شده: {fa(c['left'])}",
            f"⏳ برگشت‌نداده‌های فعلی: {fa(c['not_returned'])}",
            f"⏳ در صف Join: {fa(c['approved'])}",
            f"⌛ منتظر بررسی: {fa(c['pending'])}",
            f"❌ Join ناموفق: {fa(c['failed'])}",
            "",
            f"📈 نتیجه: {fa(c['in_joined'])} تبادل موفق برای جذب",
            "━━━━━━━━━━━━━━━━",
            "📍 مقصد: PV / Saved Messages",
        ])

    def ex_live_join_text(self, rec, title="", reply_sent=False):
        c = self.db.ex_report_counts(self._day_start())
        direction = "پیش‌قدم انجام شد" if rec.get("direction") == "out" else "تبادل عادی انجام شد"
        icon = "🚶" if rec.get("direction") == "out" else "🤝"
        return "\n".join([
            f"{icon} {direction}",
            "",
            f"📡 کانال: {rec.get('link') or '—'}",
            "✅ وضعیت: Join شد",
            *( [f"🏷 عنوان: {title}"] if title else [] ),
            *( ["💬 متن تبادل ارسال شد"] if reply_sent else [] ),
            "",
            "📊 آمار امروز:",
            f"✅ Join شده: {fa(c['joined'])} کانال",
            f"👋 لفت داده‌شده: {fa(c['left'])} کانال",
            f"👥 جذب موفق تبادل: {fa(c['in_joined'])} نفر",
        ])

    def ex_live_leave_text(self, rec, err=""):
        return "\n".join([
            "👋 لفت انجام شد" if not err else "⚠️ لفت انجام نشد",
            "",
            f"📡 کانال: {rec.get('link') or '—'}",
            "✅ طرف از کانال من خارج شده بود",
            "✅ من هم از کانالش خارج شدم" if not err else f"⚠️ {err}",
        ])

    def ex_render(self, key, name="", channel=""):
        """متن کاربر را با مقادیر واقعی پر می‌کند. خالی = جوابی نده."""
        t = (self.ex_cfg().get(key) or "").strip()
        if not t:
            return ""
        try:
            return (t.replace("{name}", name or "")
                     .replace("{channel}", channel or "")
                     .replace("{mychannel}", self.st.prof("standard")["channel"] or ""))
        except Exception:
            return t

    def ex_list_text(self, status=None):
        rows = self.db.ex_list(status, 25)
        if not rows:
            return "چیزی در این لیست نیست."
        ic = {"pending": "⏳", "approved": "✅", "joined": "🤝", "left": "👋",
              "rejected": "🚫", "failed": "❌", "leaving": "🚪"}
        title = {"pending": "منتظر", "joined": "جوین‌شده",
                 "left": "لفت‌داده"}.get(status, "همه تبادل‌ها")
        o = [f"🔁 **{title}** ({fa(len(rows))})", ""]
        for r in rows:
            who = r["peer_name"] or (f"آیدی {fa(r['peer_id'])}" if r["peer_id"] else "—")
            d = "🚶" if r.get("direction") == "out" else "↩️"
            line = f"{ic.get(r['status'], '•')}{d} `#{fa(r['id'])}` `{r['link']}`"
            if r["strikes"]:
                line += f" ⚠️{fa(r['strikes'])}"
            if r.get("reminders"):
                line += f" 🔔{fa(r['reminders'])}/{fa(max(0, int(self.ex_cfg().get('max_reminders', 1) or 0)))}"
            o.append(line)
            o.append(f"     {who}" + (f" — {r['note']}" if r["note"] else ""))
        o += ["", "`تبادل تأیید ۵` تأیید • `تبادل خروج ۵` لفت • "
                  "`تبادل حذف ۵` حذف • `تبادل ارسال ۵` ارسال پیام"]
        return "\n".join(o)

    # ---------- هوش مصنوعی ----------
    def ai_settings_cmd(self, arg):
        """زیر‌دستورهای غیرشبکه‌ای. سوال‌ها در لایه async جواب داده می‌شوند."""
        a = self.ai
        parts = arg.split(None, 1)
        sub = parts[0].lower() if parts else ""
        rest = parts[1].strip() if len(parts) > 1 else ""
        sub = {
            "روشن": "on", "خاموش": "off", "کلید": "key", "آدرس": "url",
            "نشانی": "url", "مدل": "model", "تشخیص": "detect",
            "پاسخ": "pv", "لحن": "persona", "وضعیت": "status",
        }.get(sub, sub)

        if sub in ("on", "روشن"):
            a.cfg["enabled"] = True
            a.save()
            return "🧠 هوش مصنوعی **روشن** شد." + ("" if a.cfg["key"]
                    else "\n⚠️ کلید ندارد: `هوش کلید کلید`")
        if sub in ("off", "خاموش"):
            a.cfg["enabled"] = False
            a.save()
            return "🧠 هوش مصنوعی **خاموش** شد."
        if sub == "key":
            if not rest:
                k = a.cfg["key"]
                shown = (k[:6] + "…" + k[-4:]) if len(k) > 12 else ("—" if not k else "***")
                return (f"کلید فعلی: `{shown}`\n`هوش کلید sk-...`\n"
                        f"در فایل `{AI_FILE}` ذخیره می‌شود.")
            a.cfg["key"] = rest.split()[0]
            a.save()
            return (f"✅ کلید ذخیره شد در `{AI_FILE}`\n"
                    "با `هوش تست` امتحانش کن.")
        if sub in ("url", "base"):
            if not rest:
                return f"آدرس فعلی: `{a.cfg['base_url']}`\n`هوش آدرس https://…/v1`"
            a.cfg["base_url"] = rest.split()[0].rstrip("/")
            a.save()
            return f"✅ آدرس: `{a.cfg['base_url']}`"
        if sub == "model":
            if not rest:
                return f"مدل فعلی: `{a.cfg['model']}`\n`هوش مدل gpt-4o-mini`"
            a.cfg["model"] = rest.split()[0]
            a.save()
            return f"✅ مدل: `{a.cfg['model']}`"
        if sub in ("detect", "تشخیص"):
            a.cfg["smart_detect"] = not a.cfg["smart_detect"]
            a.save()
            return ("🔍 تشخیص هوشمند پیام و لینک: **" +
                    ("روشن" if a.cfg["smart_detect"] else "خاموش") + "**")
        if sub == "pv":
            a.cfg["pv_answer"] = not a.cfg["pv_answer"]
            a.save()
            return ("💬 جواب دادن به سوال‌های PV: **" +
                    ("روشن" if a.cfg["pv_answer"] else "خاموش") + "**")
        if sub in ("persona", "لحن"):
            if not rest:
                return (f"لحن فعلی: {a.cfg['persona'] or '—'}\n"
                        "`هوش لحن خودمونی و کوتاه`")
            a.cfg["persona"] = "" if rest.lower() in ("off", "-") else rest
            a.save()
            return f"✅ لحن: {a.cfg['persona'] or 'پیش‌فرض'}"
        if sub in ("", "status", "وضعیت"):
            return self.ai_status_text()
        return None   # یعنی این یک سوال است، نه تنظیم

    def ai_status_text(self):
        a = self.ai
        k = a.cfg["key"]
        shown = (k[:6] + "…" + k[-4:]) if len(k) > 12 else ("— ندارد" if not k else "***")
        return "\n".join([
            "🧠 **هوش مصنوعی**", "",
            f"وضعیت: {'🟢 روشن' if a.cfg['enabled'] else '🔴 خاموش'}   `هوش روشن/خاموش`",
            f"کلید: `{shown}`   `هوش کلید`",
            f"آدرس: `{a.cfg['base_url']}`   `هوش آدرس`",
            f"مدل: `{a.cfg['model']}`   `هوش مدل`",
            f"تشخیص هوشمند: {'روشن' if a.cfg['smart_detect'] else 'خاموش'}"
            "   `هوش تشخیص`",
            f"جواب به پیام خصوصی: {'روشن' if a.cfg['pv_answer'] else 'خاموش'}   `هوش پاسخ`",
            f"لحن: {a.cfg['persona'] or 'پیش‌فرض'}   `هوش لحن`",
            "",
            f"آخرین خطا: {a.last_error or '—'}",
            "",
            "سوال بپرس: `هوش چطور تبادل رو روشن کنم؟`",
            "تست اتصال: `هوش تست`",
        ])

    def ai_context(self):
        """بافتی که به AI داده می‌شود تا درباره ربات درست جواب بدهد."""
        x = self.ex_cfg()
        st, vp = self.st.prof("standard"), self.st.prof("vip")
        lines = [
            "== معرفی ==",
            "جفج یک سلف‌بات تلگرام است که با شماره وارد اکانت کاربر می‌شود و",
            "از داخل Saved Messages کنترل می‌شود. دستورها با . یا / شروع می‌شوند.",
            "",
            "== کارهایی که می‌کند ==",
            "۱) ارسال زمان‌بندی‌شده پست به کانال‌ها با صف، چرخه فعالیت/استراحت،",
            "   سقف ساعتی و فاصله بین ارسال‌ها. دو پروفایل مستقل: عادی و VIP.",
            "۲) تبادل دوطرفه: اگر کسی روی پیام کاربر ریپلای بزند و بگوید جوین شدم،",
            "   چک می‌کند واقعا عضو کانال شده یا نه؛ اگر شده بود کانالش را جوین",
            "   می‌شود و متن تعیین‌شده را ریپلای می‌کند؛ اگر نشده بود فقط متن",
            "   مربوطه را جواب می‌دهد و جوین نمی‌شود.",
            "۳) حالت پیش‌قدم: خودش گروه‌های تبادل را اسکن می‌کند، کانال‌های تازه را",
            "   جوین می‌شود و متن تعیین‌شده را ریپلای می‌زند.",
            "۴) رصد جبران: اگر طرف بعدا لفت بدهد، بعد از چند بار چک، از کانالش لفت می‌دهد.",
            "",
            "== دستورهای اصلی ==",
            ".panel داشبورد | .set تنظیمات | .help راهنما | .stats آمار | .log رویدادها",
            ".post متن (صف عادی) | .vip متن (صف VIP) | .now متن (ارسال فوری)",
            ".setch @ch کانال عادی | .setvip @ch کانال VIP | .chans نمایش",
            ".active دقیقه | .rest دقیقه | .limit تعداد در ساعت | .gap ثانیه ثانیه",
            ".quiet ساعت‌ها | .mode تعویض ۲۴ساعته و چرخه‌ای | همین‌ها با v برای VIP",
            ".pause .resume .reset .queue .del شماره .clear .retry",
            ".ex on/off روشن‌کردن تبادل | .ex go حالت پیش‌قدم | .ex scan اسکن فوری",
            ".ex list .ex wait .ex ok شماره .ex no شماره .ex out شماره .ex del شماره",
            ".ex groups @g | .ex words کلمات | .ex gap ثانیه | Join روزانه بدون سقف",
            ".ex بررسی ۱۵ ۳۰ (فاصله تصادفی چک عضویت) | .ex strikes تعداد | .ex تعداد یادآوری ۱",
            ".ex scanevery 30 ثانیه | .ex scanlimit تعداد | اسکن فوری: .ex scan",
            ".ex msgfirst / .ex msgok / .ex msgno / .ex msgwait / .ex msgnolink",
            ".ai on/off .ai key .ai url .ai model .ai detect .ai pv .ai persona .ai test",
            "",
            "== وضعیت فعلی کاربر ==",
            f"کانال عادی: {st['channel'] or 'تعیین نشده'} | کانال VIP: {vp['channel'] or 'تعیین نشده'}",
            f"عادی: {'۲۴ساعته' if st['mode'] == 'always' else str(st['active_minutes']) + 'د فعال/' + str(st['rest_minutes']) + 'د استراحت'}"
            f" | سقف {st['max_per_hour'] or 'نامحدود'} در ساعت | فاصله {st['min_gap_sec']}-{st['max_gap_sec']} ثانیه",
            f"VIP: {'۲۴ساعته' if vp['mode'] == 'always' else str(vp['active_minutes']) + 'د فعال/' + str(vp['rest_minutes']) + 'د استراحت'}"
            f" | سقف {vp['max_per_hour'] or 'نامحدود'} در ساعت",
            f"ارسال متوقف است؟ {'بله' if self.st['paused'] else 'خیر'}",
            f"در صف: {self.db.pending_count()} | ارسال‌شده: {self.db.counts().get('sent', 0)}",
            f"تبادل: {'روشن' if x['enabled'] else 'خاموش'} | پیش‌قدم: {'روشن' if x['initiate'] else 'خاموش'}"
            f" | جوین خودکار: {'بله' if x['auto_join'] else 'خیر'}",
            f"گروه‌های تبادل: {'، '.join(x['groups']) if x['groups'] else 'تعیین نشده'}",
            f"Join روزانه: بدون سقف | امروز: {self.db.ex_joins_today()}",
            f"تبادل‌ها: {self.db.ex_counts()}",
        ]
        return "\n".join(lines)

    # ---------- متن‌ها ----------
    def brief(self, tier):
        p = self.st.prof(tier)
        m = ("۲۴ ساعته" if p["mode"] == "always"
             else f"{dur(p['active_minutes'])} فعال / {dur(p['rest_minutes'])} استراحت")
        cap = "نامحدود" if not p["max_per_hour"] else f"{fa(p['max_per_hour'])}/ساعت"
        return f"__{m} • سقف {cap} • فاصله {fa(p['min_gap_sec'])}–{fa(p['max_gap_sec'])} ثانیه__"

    def _tier(self):
        t = self.st.data.get("_menu") or "standard"
        return "vip" if t == "vip" else "standard"

    SEP = "━━━━━━━━━━━━━━━━━━━━"

    def _item(self, label, cmd):
        return f"{label}\n\n`{cmd}`"

    def _back_cmd(self):
        return "ویژه" if self._tier() == "vip" else "عادی"

    def _page(self, title, intro, items):
        """صفحه‌های منو را خوانا و بدون فاصله‌های خالی اضافی می‌سازد."""
        o = [title, self.SEP]
        if intro:
            o += ["", intro]
        for label, cmd in items:
            o += ["", label, f"`{cmd}`"]
        return "\n".join(o).rstrip() + "\n"

    def submenu_channel(self):
        tier = self._tier()
        cur = (self.st.prof(tier)["channel"] or "").strip()
        nm = "ویژه" if tier == "vip" else "عادی"
        st = "🟢  متصل" if cur else "⚪️  تنظیم نشده"
        return self._page(
            f"📡  کانال {nm}",
            f"{st}\n📌  فعلی:  {cur or '—'}",
            [
                ("➕  افزودن", "افزودن کانال"),
                ("✏️  تغییر", "تغییر کانال"),
                ("🗑  حذف", "حذف کانال"),
                ("📋  لیست", "کانال‌ها"),
                ("↩️  بازگشت", self._back_cmd()),
            ],
        )

    def submenu_add_channel(self):
        tier = self._tier()
        cmd = "کانال ویژه @آیدی" if tier == "vip" else "کانال @آیدی"
        cur = (self.st.prof(tier)["channel"] or "").strip() or "—"
        return self._page(
            "✏️  افزودن / تغییر کانال",
            f"الان:  {cur}",
            [
                ("✅  ثبت", cmd),
                ("↩️  بازگشت", "کانال"),
            ],
        )

    def submenu_del_channel(self):
        tier = self._tier()
        cur = self.st.prof(tier)["channel"] or "ندارد"
        return self._page(
            "🗑  حذف کانال",
            f"الان:  {cur}",
            [
                ("🗑  پاک کردن", "پاک کردن کانال"),
                ("↩️  بازگشت", "کانال"),
            ],
        )

    def cmd_del_channel(self):
        tier = self._tier()
        self.st.prof(tier)["channel"] = ""
        self.st.save()
        return self._page(
            "✅  پاک شد",
            "این بخش کانال ندارد.",
            [("↩️  بازگشت", "کانال‌ها")],
        )

    def submenu_list_channel(self):
        s = self.st.prof("standard")["channel"] or "تنظیم نشده"
        v = self.st.prof("vip")["channel"] or "تنظیم نشده"
        return self._page(
            "📋  لیست کانال",
            f"🔹  عادی:  {s}\n👑  ویژه:  {v}",
            [("↩️  بازگشت", "کانال")],
        )

    def submenu_post(self):
        tier = self._tier()
        if tier == "vip":
            return self._page(
                "✍️  متن ویژه",
                "متن را بعد از فرمان بنویس.",
                [
                    ("📝  نمونه", "ویژه سلام دوستان"),
                    ("↩️  بازگشت", "ویژه"),
                ],
            )
        return self._page(
            "✍️  متن عادی",
            "متن را بعد از فرمان بنویس.",
            [
                ("📝  نمونه", "ارسال سلام دوستان"),
                ("↩️  بازگشت", "عادی"),
            ],
        )

    def submenu_groups(self):
        g = self.ex_cfg().get("groups") or []
        lst = "، ".join(g) if g else "هیچ — فقط پیام خصوصی"
        return self._page(
            "👥  گروه‌های تبادل",
            f"تعداد:  {fa(len(g))}\nفعلی:  {lst}",
            [
                ("➕  افزودن گروه", "گروه @گروه1 @گروه2"),
                ("🗑  حذف یک گروه", "حذف گروه @گروه1"),
                ("🧹  پاک کردن همه", "حذف همه گروه‌ها"),
                ("🔄  بروزرسانی", "گروه"),
                ("↩️  بازگشت", self._back_cmd()),
            ],
        )

    def submenu_add_group(self):
        return self._page(
            "➕  افزودن گروه تبادل",
            "یوزرنیم یک یا چند گروه را با فاصله بفرست.",
            [
                ("📝  نمونه", "گروه @exchange_group"),
                ("📝  چند گروه", "گروه @group1 @group2"),
                ("↩️  بازگشت", "گروه"),
            ],
        )

    def cmd_clear_groups(self):
        self.ex_cfg()["groups"] = []
        self.st.save()
        return self.submenu_groups()

    def submenu_limit(self):
        tier = self._tier()
        p = self.st.prof(tier)
        cap = "آزاد" if not p["max_per_hour"] else f"{fa(p['max_per_hour'])} در ساعت"
        sample = "سقف‌ویژه 30" if tier == "vip" else "سقف 12"
        return self._page(
            "🚦  سقف",
            f"الان:  {cap}",
            [
                ("✏️  نمونه", sample),
                ("↩️  بازگشت", self._back_cmd()),
            ],
        )

    def submenu_cycle(self):
        if self._tier() != "vip":
            return self._page("🔄  چرخه", "فقط در بخش ویژه.", [("👑  ویژه", "ویژه")])
        p = self.st.prof("vip")
        return self._page(
            "🔄  چرخه",
            f"کار:  {fa(p['active_minutes'])} دقیقه\nاستراحت:  {fa(p['rest_minutes'])} دقیقه",
            [
                ("▶️  کار", "فعالیت‌ویژه 60"),
                ("😴  استراحت", "استراحت‌ویژه 30"),
                ("↩️  بازگشت", "ویژه"),
            ],
        )

    def submenu_gap(self):
        if self._tier() != "vip":
            return self._page("⏱  نوسان", "فقط در بخش ویژه.", [("👑  ویژه", "ویژه")])
        p = self.st.prof("vip")
        return self._page(
            "⏱  نوسان",
            f"{fa(p['min_gap_sec'])} تا {fa(p['max_gap_sec'])} ثانیه",
            [
                ("🎲  نمونه ارسال", "نوسان‌ویژه ۲۰ ۴۵"),
                ("🔔  نوسان یادآوری تبادل", "تبادل فاصله یادآوری 5 15"),
                ("↩️  بازگشت", "ویژه"),
            ],
        )

    def submenu_ex_msgs(self):
        x = self.ex_cfg()
        def cur(k):
            v = (x.get(k) or "").strip()
            return v[:50] if v else "تنظیم نشده"
        return self._page(
            "💬  متن تبادل",
            f"💬 بعد از هر Join: {cur('msg_come')}\n✅  موفقیت تبادل: {cur('msg_ok')}\n❌  {cur('msg_no')}\n⏳  {cur('msg_wait')}\n🔗  {cur('msg_nolink')}",
            [
                ("🚶  پیام بعد از آخرین پیام", "تبادل پیام بیا"),
                ("⏱  زمان پیام «بیا»", "تبادل زمان بیا ۰"),
                ("✅  موفق", "تبادل پیام موفق جوین شدم"),
                ("❌  ناموفق", "تبادل پیام ناموفق اول عضو شو"),
                ("⏳  انتظار", "تبادل پیام انتظار دارم چک می‌کنم"),
                ("🔗  بدون لینک", "تبادل پیام بدون لینک لینک بده"),
                ("↩️  بازگشت", "تبادل"),
            ],
        )

    def profile_status(self, tier, detailed=True):
        """وضعیت واقعی همان بخش؛ «فعال» چرخه بدون کانال نشان داده نشود."""
        if not (self.st.prof(tier)["channel"] or "").strip():
            return "⚪ خاموش — کانال تنظیم نشده"
        if self.st["paused"]:
            return "⏸ متوقف"
        return self.cyc[tier].label() if detailed else "🟢 فعال"

    def section_text(self, tier):
        vip = tier == "vip"
        p = self.st.prof(tier)
        ch = (p["channel"] or "").strip()
        qn = self.db.pending_count(tier)
        x = self.ex_cfg()
        title = "👑 جفج  |  بخش VIP" if vip else "🔹 جفج  |  بخش عادی"
        channel_label = "کانال VIP" if vip else "کانال"
        items = [
            ("📡 کانال VIP" if vip else "📡 کانال",
             "کانال ویژه" if vip else "کانال"),
            ("✍️ متن ارسال", "متن"),
            ("👥 گروه‌های تبادل", "گروه"),
            ("🚦 سقف ارسال", "سقف ویژه" if vip else "سقف"),
        ]
        if vip:
            items += [("🔄 چرخه فعالیت", "چرخه"),
                      ("🎲 نوسان ارسال", "نوسان")]
        items += [("🔁 تنظیم تبادل", "تبادل"),
                  ("📮 صف پیام‌ها", "صف")]

        lines = [
            title,
            self.SEP,
            "",
            f"📡 {channel_label}: {ch or 'تنظیم نشده'}",
            f"📮 صف ارسال: {'خالی' if not qn else fa(qn)}",
            f"🔁 تبادل: {'روشن' if x['enabled'] else 'خاموش'}",
            f"📤 وضعیت ارسال: {self.profile_status(tier, detailed=False)}",
            "",
            "━━━━━━━━ مدیریت ━━━━━━━━",
        ]
        for label, cmd in items:
            # هر فرمان یک جفت backtick متوازن دارد؛ _to_html آن را به code تبدیل می‌کند.
            lines.append(f"{label} — `{cmd}`")
        lines += [
            "",
            "━━━━━━━━ ابزارها ━━━━━━━━",
            "🧠 بررسی هوشمند — `بررسی فعال`",
            "🔕 خاموش‌کردن بررسی — `بررسی خاموش`",
            "⏸ توقف ارسال — `توقف`",
            "▶️ ادامه ارسال — `ادامه`",
            "",
            "━━━━━━━━━━━━━━━━",
            "🏠 بازگشت به پنل اصلی — `پنل`",
        ]
        return "\n".join(lines) + "\n"

    def panel(self):
        try:
            self.lim.load()
        except Exception:
            pass

        name = (self.me or "—").split("(")[0].strip() or "—"
        standard = self.st.prof("standard")
        vip = self.st.prof("vip")
        counts = self.db.counts()
        ex_counts = self.db.ex_counts()
        exchange = self.ex_cfg()
        points = int(self.lim["points"] or 0)
        hours = int(self.lim["hours_left"] or 0)
        plan = (self.lim["plan"] or "").strip()
        points_mode = bool(self.lim["points_mode"] or points or plan == "امتیازی")

        lines = [
            "💎 جفج 3.0",
            "━━━━━━━━━━━━━━",
            "",
            f"👤 حساب: {name}",
        ]
        if self.my_username:
            lines.append(f"🔗 یوزرنیم: @{self.my_username.lstrip('@')}")
        lines += [
            f"🆔 آیدی: {fa(self.my_id) if self.my_id else '—'}",
            "",
            "━━━━━━━━━━━━━━",
        ]

        if points_mode:
            lines += [
                f"⭐ امتیاز: {fa(points)}",
                f"⏳ زمان تقریبی: {('تمام شده' if hours <= 0 and points <= 0 else fa(hours or points) + ' ساعت')}",
            ]
        elif plan:
            lines.append(f"💎 پلن: {plan}")
        else:
            lines.append("💎 پلن: ثبت نشده")

        if self.st["paused"]:
            state_icon, state_text = "⏸", "متوقف"
        elif points_mode and points <= 0:
            state_icon, state_text = "🔴", "امتیاز تمام شده"
        elif not plan and not points_mode:
            state_icon, state_text = "⚪", "اعتبار ثبت نشده"
        else:
            state_icon, state_text = "🟢", "در حال کار"

        lines += [
            f"{state_icon} وضعیت: {state_text}",
            f"📡 کانال عادی: {standard['channel'] or 'تنظیم نشده'}",
            f"👑 کانال ویژه: {vip['channel'] or 'تنظیم نشده'}",
            "",
            "━━━━━━━━━━━━━━",
            f"📮 صف: {fa(self.db.pending_count())} پیام"
            + (f"  ·  بی‌کانال: {fa(self.db.held_count())}" if self.db.held_count() else ""),
            f"📤 ارسال امروز: {fa(self.db.sent_since(int(time.time()) - 86400))}",
            f"✅ کل ارسال: {fa(counts.get('sent', 0))}",
            f"❌ ناموفق: {fa(counts.get('failed', 0))}",
            f"🔹 عادی: {self.profile_status("standard")}",
            f"👑 ویژه: {self.profile_status("vip")}",
        ]

        if exchange["enabled"]:
            lines += [
                "",
                "━━━━━━━━━━━━━━",
                f"🔁 تبادل: روشن  ·  گروه‌ها: {fa(len(exchange.get('groups') or []))}",
                f"⏱ فاصله جوین: {fa(exchange['min_join_gap_sec'])}–{fa(exchange['max_join_gap_sec'])} ثانیه",
                f"🔍 اسکن گروه: هر {secs(max(30, int(exchange.get('scan_every_sec', 30) or 30)))}",
                f"🤝 جوین امروز: {fa(ex_counts.get('joined', 0))}",
                f"⏳ در صف Join: {fa(ex_counts.get('approved', 0))}",
                f"⌛ منتظر بررسی: {fa(ex_counts.get('pending', 0))}",
            ]
        else:
            lines.append("🔁 تبادل: خاموش")

        lines.append(f"🧠 هوش مصنوعی: {'روشن' if self.ai.ready else 'خاموش'}")
        try:
            _rc = self.st["risk"]
            _edge, _rparts, _rmeta = self.real_risk_edge()
            _hard = bool(_rc.get("hard_on", True))
            _ex_state = "🟢" if exchange["enabled"] else "🔴"
            _reason = " (خاموشی خودکار)" if _rc.get("_auto_off") else ""
            # پایشِ واقعی را به‌عنوان نگهبانِ اصلی نمایش بده؛
            # امتیازِ انتزاعی را فقط وقتی روشن است بیاور.
            if _hard:
                _pl = ("🟢 در مرز ریپ نیست" if not _edge
                       else "🔴 در مرز ریپ — توقف اجباری")
                lines.append(f"🛡 پایشِ واقعی: {_pl}  ·  "
                             f"امتیازِ واقعی {_rmeta['score']}/{_rc.get('hard_trigger', 80)}  ·  "
                             f"تبادل {_ex_state}{_reason}")
            else:
                lines.append(f"🛡 پایشِ واقعی: 🔴 خاموش  ·  تبادل {_ex_state}{_reason}")
            if _rc.get("on", True):
                _risk, _parts, _meta = self.risk_current()
                lines.append(f"🎛 توقف بر امتیاز: 🟢 روشن  ·  "
                             f"ریسک {_risk}%  ·  آستانه {_rc.get('trigger', 75)}%")
        except Exception:
            pass
        if self.last_error:
            lines += [f"⚠️ آخرین خطا: {self.last_error[:100]}"]

        lines += [
            "",
            "━━━━━━━━━━━━━━",
            "📂 منوی اصلی:",
            "🔹 بخش عادی  →  `عادی`",
            "👑 بخش ویژه  →  `ویژه`",
            "🔁 تبادل  →  `تبادل`",
            "👥 گروه‌ها  →  `گروه`",
            "📮 صف ارسال  →  `صف`",
            "📊 آمار  →  `آمار`",
            "🎛 تنظیمات  →  `تنظیمات`",
            "📖 راهنما  →  `راهنما`",
        ]
        return "\n".join(lines) + "\n"

    def settings_text(self):
        o = [
            "════════════════════",
            "🎛   تنظیمات کامل",
            "════════════════════",
        ]
        for tier, nm, ic in (("standard", "عادی", "🔹"), ("vip", "VIP", "👑")):
            p = self.st.prof(tier)
            cap = "آزاد" if not p["max_per_hour"] else f"{fa(p['max_per_hour'])} پیام در ساعت"
            q = p.get("quiet_hours") or []
            qs = "ندارد" if not q else "، ".join(fa(h) for h in q)
            o += [
                f"{ic}  بخش {nm}",
                f"📡  کانال: {p['channel'] or 'تنظیم نشده'}",
                f"⚙️  حالت: {'۲۴ ساعته' if p['mode']=='always' else 'چرخه‌ای'}     {'حالت ویژه' if tier == 'vip' else 'حالت'}",
                f"▶️  فعالیت: {dur(p['active_minutes'])}     {'فعالیت ویژه' if tier == 'vip' else 'فعالیت'}",
                f"😴  استراحت: {dur(p['rest_minutes'])}     {'استراحت ویژه' if tier == 'vip' else 'استراحت'}",
                f"🚦  سقف: {cap}     {'سقف ویژه' if tier == 'vip' else 'سقف'}",
                f"⏳  فاصله: {fa(p['min_gap_sec'])} تا {fa(p['max_gap_sec'])} ثانیه     {'فاصله ویژه' if tier == 'vip' else 'فاصله'}",
                f"🌙  سکوت: {qs}     {'سکوت ویژه' if tier == 'vip' else 'سکوت'}",
                f"📍  الان: {self.profile_status(tier)}",
                "────────────────────",
            ]
        o += [
            "⏸  توقف ارسال: توقف",
            "▶️  ادامه: ادامه",
            "♻️  ریست چرخه: بازنشانی",
            "════════════════════",
        ]
        return "\n".join(o)

    def queue_text(self):
        items = self.db.list_pending(12)
        c = self.db.counts()
        o = [
            "════════════════════",
            "📮   صف ارسال",
            "════════════════════",
            f"⏳  در انتظار: {fa(self.db.pending_count())}",
            f"✅  ارسال‌شده: {fa(c.get('sent', 0))}",
            f"❌  ناموفق: {fa(c.get('failed', 0))}",
            f"📦  معلق (بی‌کانال): {fa(self.db.held_count())}",
            "────────────────────",
        ]
        if not items:
            o.append("🕳  صف خالی است.")
        else:
            for it in items:
                if not it["target"]:
                    mark = "📦 معلق"
                elif it["tier"] == "vip":
                    mark = "👑 VIP"
                else:
                    mark = "🔹 عادی"
                preview = (it["text"] or "").replace("\n", " ")[:40]
                o.append(f"{mark}  #{fa(it['id'])}")
                o.append(f"    {preview}")
            o += [
                "────────────────────",
                "🗑  حذف یکی:  حذف شماره",
                "🧹  خالی کردن:  پاکسازی",
                "♻️  تلاش دوباره:  تلاش دوباره",
            ]
        o.append("════════════════════")
        return "\n".join(o)

    def stats_text(self):
        now = int(time.time())
        c = self.db.counts()
        return "\n".join([
            "════════════════════",
            "📊   آمار ارسال",
            "════════════════════",
            f"🕐  ۱ ساعت اخیر: {fa(self.db.sent_since(now - 3600))}",
            f"📆  ۲۴ ساعت: {fa(self.db.sent_since(now - 86400))}",
            f"🗓  ۷ روز: {fa(self.db.sent_since(now - 604800))}",
            f"🏆  کل ارسال: {fa(c.get('sent', 0))}",
            f"❌  ناموفق: {fa(c.get('failed', 0))}",
            f"📮  الان در صف: {fa(self.db.pending_count())}",
            f"🕰  آپ‌تایم: {secs(now - self.started)}",
            "════════════════════",
        ])


# ─────────────────────────────────────────────
#  گرفتن خودکار api_id و api_hash از my.telegram.org
# ─────────────────────────────────────────────
MTG = "https://my.telegram.org"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")


class MyTelegram:
    """ورود به my.telegram.org و ساخت/خواندن اپلیکیشن."""

    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar))
        self.random_hash = ""

    def _post(self, path, data, timeout=30):
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(
            MTG + path, data=body, method="POST",
            headers={"User-Agent": UA,
                     "Referer": MTG + "/auth",
                     "Origin": MTG,
                     "X-Requested-With": "XMLHttpRequest",
                     "Content-Type": "application/x-www-form-urlencoded"})
        with self.opener.open(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore").strip()

    def _get(self, path, timeout=30):
        req = urllib.request.Request(
            MTG + path, headers={"User-Agent": UA, "Referer": MTG + "/auth"})
        with self.opener.open(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")

    # ---------- مرحله ۱: درخواست کد ----------
    def send_code(self, phone):
        """کد را به تلگرامِ همان شماره می‌فرستد. (موفق, پیام)"""
        phone = phone.strip().replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            phone = "+" + phone
        try:
            out = self._post("/auth/send_password", {"phone": phone})
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code} — سایت جواب نداد"
        except urllib.error.URLError as e:
            return False, f"دسترسی به my.telegram.org نشد ({e.reason})"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

        try:
            d = json.loads(out)
        except Exception:
            low = out.lower()
            if "banned" in low:
                return False, "این شماره از my.telegram.org مسدود شده"
            if "invalid" in low or "phone" in low:
                return False, "شماره پذیرفته نشد — با کد کشور بزن مثل +989121234567"
            return False, f"پاسخ نامفهوم: {out[:120]}"

        self.random_hash = d.get("random_hash", "")
        if not self.random_hash:
            return False, f"random_hash نیامد: {out[:120]}"
        return True, "کد در تلگرام فرستاده شد"

    # ---------- مرحله ۲: ورود با کد ----------
    def login(self, phone, code):
        phone = phone.strip().replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            phone = "+" + phone
        try:
            out = self._post("/auth/login", {
                "phone": phone,
                "random_hash": self.random_hash,
                "password": code.strip()})
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

        if out.lower().startswith("true"):
            return True, "وارد شدی"
        low = out.lower()
        if "invalid" in low or "false" in low:
            return False, "کد اشتباه بود"
        return False, f"ورود نشد: {out[:120]}"

    # ---------- مرحله ۳: خواندن یا ساختن اپ ----------
    @staticmethod
    def _parse(html):
        api_id = api_hash = ""
        mh = re.search(r"\b([0-9a-fA-F]{32})\b", html)
        if mh:
            api_hash = mh.group(1).lower()
        mi = re.search(r"App\s*api_id.*?>\s*(\d{4,12})\s*<", html, re.S | re.I)
        if not mi:
            mi = re.search(r'uneditable-input[^>]*>\s*(\d{4,12})\s*<', html)
        if mi:
            api_id = mi.group(1)
        return api_id, api_hash

    def get_or_create(self, title="jafj", shortname="jafj"):
        """(api_id, api_hash, پیام)"""
        try:
            html = self._get("/apps")
        except Exception as e:
            return "", "", f"صفحه apps باز نشد: {e}"

        api_id, api_hash = self._parse(html)
        if api_id and api_hash:
            return api_id, api_hash, "اپلیکیشن از قبل وجود داشت"

        mh = re.search(r'name="hash"\s+value="([^"]+)"', html)
        if not mh:
            if "log in" in html.lower() or "/auth" in html[:400].lower():
                return "", "", "نشست منقضی شد — دوباره تلاش کن"
            return "", "", "فرم ساخت اپ پیدا نشد"

        short = re.sub(r"[^a-z0-9]", "", shortname.lower())[:32]
        if len(short) < 5:
            short = (short + "jafjapp")[:8]
        try:
            self._post("/apps/create", {
                "hash": mh.group(1),
                "app_title": title[:32] or "jafj",
                "app_shortname": short,
                "app_url": "",
                "app_platform": "desktop",
                "app_desc": "personal channel manager"})
        except Exception as e:
            return "", "", f"ساخت اپ نشد: {e}"

        time.sleep(1.5)
        try:
            html = self._get("/apps")
        except Exception as e:
            return "", "", f"بعد از ساخت، صفحه باز نشد: {e}"
        api_id, api_hash = self._parse(html)
        if api_id and api_hash:
            return api_id, api_hash, "اپلیکیشن ساخته شد"
        return "", "", "ساخته شد ولی مقادیر خوانده نشد — چند دقیقه بعد دوباره اجرا کن"


def auto_get_api(phone_hint=""):
    """گفتگوی ترمینالی برای گرفتن خودکار. برمی‌گرداند dict یا None."""
    print("\n" + "─" * 52)
    print("  گرفتن خودکار api_id و api_hash")
    print("  کدی که می‌آید، داخل خودِ تلگرام است (چت Telegram)")
    print("─" * 52)

    mt = MyTelegram()

    phone = phone_hint
    for _ in range(3):
        if not phone:
            phone = ask("📱 شماره با کد کشور (+989121234567): ") or ""
        if not phone:
            return None
        ok, msg = mt.send_code(phone)
        print(("✅ " if ok else "❌ ") + msg)
        if ok:
            break
        phone = ""
    else:
        return None

    for _ in range(3):
        code = ask("🔑 کدی که در تلگرام آمد: ")
        if code is None:
            return None
        if not code:
            continue
        ok, msg = mt.login(phone, code)
        print(("✅ " if ok else "❌ ") + msg)
        if ok:
            break
    else:
        return None

    print("⏳ در حال ساخت اپلیکیشن…")
    api_id, api_hash, msg = mt.get_or_create()
    print(("✅ " if api_id else "❌ ") + msg)
    if not (api_id and api_hash):
        return None

    print(f"\n   api_id:   {api_id}")
    print(f"   api_hash: {api_hash[:8]}…{api_hash[-4:]}\n")
    try:
        return {"api_id": int(api_id), "api_hash": api_hash, "phone": phone}
    except ValueError:
        return None


# ─────────────────────────────────────────────
#  اطلاعات ورود — اگر نبود، می‌پرسد و ذخیره می‌کند
# ─────────────────────────────────────────────
def load_creds():
    c = {"api_id": API_ID, "api_hash": API_HASH, "phone": PHONE}
    if os.path.exists(CREDS_FILE):
        try:
            with open(CREDS_FILE, encoding="utf-8") as f:
                saved = json.load(f)
            # فایل کنار سلف (از پنل مدیر) اولویت دارد
            for k in c:
                if saved.get(k):
                    c[k] = saved[k]
        except Exception:
            pass
    return c


def save_creds(c):
    try:
        with open(CREDS_FILE, "w", encoding="utf-8") as f:
            json.dump(c, f, ensure_ascii=False, indent=2)
        if hasattr(os, "chmod"):
            try:
                os.chmod(CREDS_FILE, 0o600)
            except Exception:
                pass
    except Exception as e:
        print(f"⚠️ ذخیره اطلاعات ورود ناموفق: {e}")


def ask(prompt):
    """ورودی امن — اگر ترمینال تعاملی نبود None برمی‌گرداند."""
    try:
        print(prompt, end="", flush=True)
        sys.stdout.flush()
        sys.stderr.flush()
        line = sys.stdin.readline()
        if line == "":
            return None
        return line.strip()
    except (EOFError, KeyboardInterrupt, OSError):
        return None


def ensure_creds():
    """تا وقتی api_id و api_hash درست نگرفته، می‌پرسد. خاموش نمی‌شود."""
    c = load_creds()
    if c["api_id"] and c["api_hash"]:
        return c

    print("\n" + "─" * 52)
    print("  یک بار باید api_id و api_hash داشته باشی.")
    print("─" * 52)
    print("  ۱) خودکار بگیرم  (فقط شماره و یک کد از تلگرام)")
    print("  ۲) خودم دستی وارد می‌کنم")
    print("─" * 52)

    pick = ask("انتخاب [۱]: ")
    if pick is None:
        print("\n⚠️ ترمینال تعاملی نیست. api_id و api_hash را بالای فایل بگذار.")
        return None

    if pick.strip() in ("", "1", "۱"):
        got = auto_get_api(c.get("phone") or "")
        if got:
            c.update(got)
            save_creds(c)
            print("✅ ذخیره شد — دفعه بعد نمی‌پرسد.\n")
            return c
        print("\n⚠️ خودکار نشد. دستی وارد کن.")
        print("   my.telegram.org → API development tools\n")

    while not c["api_id"]:
        v = ask("🔑 api_id (فقط عدد): ")
        if v is None:
            print("\n⚠️ ترمینال تعاملی نیست. api_id و api_hash را بالای فایل بگذار.")
            return None
        try:
            c["api_id"] = num(v)
        except ValueError:
            print("   عدد نبود، دوباره بزن.")

    while not c["api_hash"]:
        v = ask("🔑 api_hash: ")
        if v is None:
            return None
        if len(v) >= 8:
            c["api_hash"] = v
        else:
            print("   کوتاه بود، دوباره بزن.")

    save_creds(c)
    print("✅ ذخیره شد — دفعه بعد نمی‌پرسد.\n")
    return c


# ─────────────────────────────────────────────
#  لایه تلگرام (Telethon)
# ─────────────────────────────────────────────
def need_telethon():
    try:
        import telethon  # noqa
        return False
    except ImportError:
        return True


async def connect_and_run(eng, creds):
    """یک بار وصل می‌شود و کار می‌کند. برمی‌گرداند: 'retry' یا 'stop'"""
    from telethon import TelegramClient, events
    from telethon.errors import (FloodWaitError, SlowModeWaitError,
                                 ChatWriteForbiddenError, ChannelPrivateError,
                                 UsernameNotOccupiedError, RPCError,
                                 UserNotParticipantError, UserAlreadyParticipantError,
                                 InviteHashExpiredError, InviteHashInvalidError,
                                 ChannelsTooMuchError, InviteRequestSentError)
    from telethon.tl.functions.channels import (JoinChannelRequest, LeaveChannelRequest,
                                                GetParticipantRequest)
    from telethon.tl.functions.messages import ImportChatInviteRequest

    client = TelegramClient(SESSION, creds["api_id"], creds["api_hash"])

    async def phone_cb():
        if creds.get("phone"):
            return creds["phone"]
        while True:
            v = ask("📱 شماره (مثال +989123456789): ")
            if v is None:
                raise RuntimeError("no-tty")
            if len(v) >= 7:
                creds["phone"] = v
                save_creds(creds)
                return v
            print("   شماره کوتاه بود، دوباره بزن.")

    try:
        await client.start(phone=phone_cb)
    except RuntimeError:
        print("\n⚠️ ترمینال تعاملی نیست — PHONE را بالای فایل بگذار.")
        return "stop"
    except FloodWaitError as e:
        w = getattr(e, "seconds", 60)
        print(f"\n⏳ تلگرام برای ورود {secs(w)} صبر خواسته. منتظر می‌مانم…")
        await asyncio.sleep(w + 5)
        return "retry"
    except Exception as e:
        print(f"\n⚠️ ورود ناموفق: {type(e).__name__}: {e}")
        print("   ۳۰ ثانیه دیگر دوباره تلاش می‌کنم… (Ctrl+C برای خروج)")
        await asyncio.sleep(30)
        return "retry"

    me = await client.get_me()
    eng.me = (f"{me.first_name or ''} (@{me.username})" if me.username
              else (me.first_name or str(me.id)))
    eng.my_username = me.username or ""
    eng.my_id = me.id
    eng.write_status()
    eng.log("ok", "login", f"{eng.me} | id={me.id}")

    for tier in ("standard", "vip"):
        p = eng.st.prof(tier)
        mode = ("۲۴ساعته" if p["mode"] == "always"
                else f"{p['active_minutes']}د فعال/{p['rest_minutes']}د استراحت")
        print(f"  {tier:9} | {mode} | سقف {p['max_per_hour'] or '∞'}/ساعت "
              f"| فاصله {p['min_gap_sec']}-{p['max_gap_sec']}s "
              f"| {p['channel'] or 'کانال تعیین نشده'}")
    held = eng.db.held_count()
    if held:
        print(f"  📦 {held} پیام معلق — منتظر تعیین کانال")
    _x = eng.ex_cfg()
    if _x["enabled"]:
        _ec = eng.db.ex_counts()
        print(f"  🔁 تبادل روشن | {_ec.get('joined', 0)} جوین‌شده | "
              f"{'خودکار' if _x['auto_join'] else 'تأیید دستی'} | "
              "بدون سقف روزانه")
    print("═" * 50)
    print("  ✅ آماده — در Saved Messages بفرست: پنل\n")

    async def note(text):
        try:
            await client.send_message("me", text, link_preview=False)
        except Exception:
            pass

    # ---------- هوش مصنوعی ----------
    async def handle_ai(event, arg, reply_text=None):
        a = eng.ai

        # تست اتصال
        if arg.strip().lower() in ("test", "تست"):
            if not a.cfg["key"]:
                return "⚠️ کلیدی ثبت نشده.\n`هوش کلید sk-...`"
            try:
                await event.reply("⏳ در حال تست…")
            except Exception:
                pass
            out, err = await a.achat(
                [{"role": "user", "content": "فقط بنویس: سلام"}],
                temperature=0, max_tokens=20, timeout=45)
            if err:
                return (f"❌ اتصال برقرار نشد.\n\n`{err}`\n\n"
                        f"سرویس: `{a.cfg['base_url']}`\nمدل: `{a.cfg['model']}`\n\n"
                        "کلید تازه: `هوش کلید sk-...`\n"
                        "سرویس دیگر: `هوش آدرس https://…/v1`")
            return (f"✅ وصل شد!\n\nسرویس: `{a.cfg['base_url']}`\n"
                    f"مدل: `{a.cfg['model']}`\nجواب: {out}")

        # تنظیمات (بدون شبکه)
        res = eng.ai_settings_cmd(arg)
        if res is not None:
            return res

        # سوال
        if not a.ready:
            return (f"🧠 AI آماده نیست.\n"
                    f"{'کلید ثبت نشده' if not a.cfg['key'] else 'خاموش است'}.\n"
                    "`هوش کلید sk-...` سپس `هوش تست`")

        q = arg if not reply_text else f"{arg}\n\n--- متن ریپلای‌شده ---\n{reply_text}"
        try:
            await event.reply("🧠 …")
        except Exception:
            pass
        out, err = await a.ask(q, eng.ai_context())
        if err:
            return f"❌ {err}"
        return out or "جوابی نیامد."

    # ---------- پنل — incoming و outgoing هر دو (پیام از گوشی دیگر هم برسد)
    pattern = re.compile(r"^[./]([^\s]+)(?:\s+([\s\S]*))?$")

    def _norm_cmd(s):
        # نیم‌فاصله متن کاربر حفظ شود؛ برای تشخیص دستور از low استفاده می‌کنیم.
        s = (s or "").replace("\u200b", "").replace("\ufeff", "")
        s = s.replace("ي", "ی").replace("ك", "ک").strip()
        return s

    def _to_html(txt):
        import html as _html
        parts = re.split(r"`([^`]+)`", txt or "")
        o = []
        for i, p in enumerate(parts):
            if i % 2:
                o.append("<code>" + _html.escape(p) + "</code>")
            else:
                q = _html.escape(p)
                q = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", q, flags=re.S)
                q = re.sub(r"__(.+?)__", r"<i>\1</i>", q, flags=re.S)
                o.append(q)
        return "".join(o)

    async def _say(txt, event=None):
        if not txt:
            return
        h = _to_html(txt)
        # همیشه به Saved Messages (me) برمی‌گردد تا پاسخ، مستقل از محلِ پیام،
        # حتماً در جایی که ربات کنترلِ آن را دارد دیده شود.
        try:
            await client.send_message("me", h, parse_mode="html", link_preview=False)
            return
        except Exception as e:
            eng.log("warn", "say_html", f"{type(e).__name__}: {str(e)[:120]}")
        # اگر HTML رد شد، با متنِ خام تلاش کن.
        try:
            await client.send_message("me", txt, link_preview=False)
            return
        except Exception as e:
            eng.log("error", "say", f"{type(e).__name__}: {str(e)[:120]}")

    async def _send_panel():
        try:
            txt = eng.panel()
        except Exception as e:
            txt = f"⚠️ پنل خطا داد: {type(e).__name__}: {e}"
            traceback.print_exc()
            eng.log("error", "panel", str(e))
        await _say(txt)

    @client.on(events.NewMessage(chats="me", incoming=True))
    async def on_saved(event):
        # فقط پیام‌های دریافتی (که تو می‌فرستی) را پردازش کن؛ پاسخ‌های خودِ
        # ربات (out) دوباره پردازش نشوند تا حلقه/جمجور پیش نیاید.
        if getattr(event, "out", False):
            return
        # فرمان پنل قبل از هر مسیر AI/تبادل بررسی می‌شود.
        raw = _norm_cmd(event.raw_text or "")
        low = _soft_clean(raw).lower()
        panel_words = {
            "panel", ".panel", "/panel", "پنل", ".پنل", "/پنل",
            "p", ".p", "/p", "داشبورد", ".داشبورد", "خانه",
        }
        # «پنل» را حتی با نیم‌فاصله/فاصله‌ی تایپی (پن‌ل / پن ل) هم تشخیص بده.
        if low.startswith(("پن ", "پن‌")) or low in ("پن ل",):
            low = "پنل"
        if low in panel_words or low.startswith(".panel") or low.startswith("/panel"):
            await _send_panel()
            return
        if low == "هوش" or low.startswith("هوش ") or low.startswith("هوش مصنوعی"):
            ai_arg = raw[3:].strip() if low.startswith("هوش ") else ""
            if low.startswith("هوش مصنوعی"):
                ai_arg = raw[len("هوش مصنوعی"):].strip()
            out = await handle_ai(event, ai_arg)
            await _say(out, event)
            return
        bare = {
            "عادی": ("عادی", ""),
            "ویژه": ("ویژه", ""),
            "تبادل": ("ex", ""),
            "گزارش": ("ex", "report"),
            "گزارش خلاصه": ("ex", "report_now"),
            "گزارش خلاصه الان": ("ex", "report_now"),
            "گزارش خلاصه همین الان": ("ex", "report_now"),
            "صف": ("queue", ""),
            "آمار": ("stats", ""),
            "راهنما": ("help", ""),
            "تنظیمات": ("set", ""),
            "گروه": ("گروه", ""),
            "گروه‌ها": ("گروه", ""),
            "گروه ها": ("گروه", ""),
            "افزودن گروه": ("افزودن گروه", ""),
            "ثبت گروه": ("افزودن گروه", ""),
            "حذف گروه": ("حذف گروه", ""),
            "حذف همه گروه‌ها": ("حذف همه گروه‌ها", ""),
            "حذف همه گروه ها": ("حذف همه گروه‌ها", ""),
            "پاک کردن گروه": ("حذف گروه", ""),
            "پاکسازی": ("clear", ""),
            "تلاش دوباره": ("retry", ""),
            "بازنشانی": ("reset", ""),
            "زنده": ("ping", ""),
            "فعالیت": ("active", ""),
            "استراحت": ("rest", ""),
            "فاصله": ("gap", ""),
            "سکوت": ("quiet", ""),
            "حالت": ("mode", ""),
            "فعالیت ویژه": ("vactive", ""),
            "استراحت ویژه": ("vrest", ""),
            "سقف ویژه": ("vlimit", ""),
            "فاصله ویژه": ("vgap", ""),
            "سکوت ویژه": ("vquiet", ""),
            "حالت ویژه": ("vmode", ""),
            "بررسی فعال": ("بررسی", "فعال"),
            "بررسی خاموش": ("بررسی", "خاموش"),
            "هوش مصنوعی بررسی فعال": ("بررسی", "فعال"),
            "هوش مصنوعی بررسی خاموش": ("بررسی", "خاموش"),
            "تبادل روشن": ("ex", "on"),
            "تبادل خاموش": ("ex", "off"),
            "لیست تبادل": ("ex", "list"),
            "توقف": ("pause", ""),
            "ادامه": ("resume", ""),
            "کانال": ("کانال", ""),
            "تنظیم کانال": ("تنظیم‌کانال", ""),
            "افزودن": ("افزودن", ""),
            "تغییر": ("تغییر", ""),
            "حذف": ("حذف", "کانال"),
            "افزودن کانال": ("افزودن‌کانال", ""),
            "تغییر کانال": ("تغییر کانال", ""),
            "حذف کانال": ("حذف", "کانال"),
            "پاک کردن کانال": ("پاک کردن کانال", ""),
            "لیست کانال": ("لیست‌کانال", ""),
            "متن": ("متن", ""),
            "تنظیم متن": ("تنظیم‌متن", ""),
            "سقف ارسال": ("سقف‌ارسال", ""),
            "چرخه": ("چرخه", ""),
            "نوسان": ("نوسان", ""),
            "متن تبادل": ("متن‌تبادل", ""),
            "متن‌های تبادل": ("متن تبادل", ""),
            "متن های تبادل": ("متن تبادل", ""),
            "کانال‌ها": ("کانال‌ها", ""),
            "کانال ها": ("کانال‌ها", ""),
            "کانال ویژه": ("کانال ویژه", ""),
            "تبادل متن": ("ex", "msg"),
            "تبادل پیام": ("ex", "come"),
            "تبادل متن موفق": ("متن‌موفق", ""),
            "تبادل متن ناموفق": ("متن‌ناموفق", ""),
            "تبادل متن انتظار": ("متن‌انتظار", ""),
            "تبادل متن بدون لینک": ("متن‌بدون‌لینک", ""),
            "تبادل پیام موفق": ("متن‌موفق", ""),
            "تبادل پیام ناموفق": ("متن‌ناموفق", ""),
            "تبادل پیام انتظار": ("متن‌انتظار", ""),
            "تبادل پیام بدون لینک": ("متن‌بدون‌لینک", ""),
            "تبادل پیام بیا": ("ex", "come"),
            "تبادل زمان بیا": ("ex", "cometime"),
            "تبادل گروه‌ها": ("ex", "groups"),
            "تبادل گروه ها": ("ex", "groups"),
            "هوش": ("ai", ""),
            "ریسک": ("risk", ""),
            "امنیت": ("risk", ""),
            "محافظ": ("risk", ""),
            "حفاظت": ("risk", ""),
        }
        if low in bare:
            cmd, arg = bare[low]
            try:
                out = eng.cmd(cmd, arg, None)
            except Exception as e:
                out = f"⚠️ {type(e).__name__}: {e}"
            await _say(out, event)
            return
        # جمله‌های فارسی بدون نقطه
        for pref, cmap in (
            ("متن موفق ", ("متن‌موفق",)),
            ("متن ناموفق ", ("متن‌ناموفق",)),
            ("متن انتظار ", ("متن‌انتظار",)),
            ("متن بدون لینک ", ("متن‌بدون‌لینک",)),
            ("متن‌موفق ", ("متن‌موفق",)),
            ("متن‌ناموفق ", ("متن‌ناموفق",)),
            ("متن‌انتظار ", ("متن‌انتظار",)),
            ("متن‌بدون‌لینک ", ("متن‌بدون‌لینک",)),
            ("کانال ویژه ", ("setvip",)),
            ("کانال‌ویژه ", ("setvip",)),
            ("کانال ", ("setch",)),
            ("ارسال فوری ", ("now",)),
            ("ارسال ", ("post",)),
            ("ویژه ", ("vip",)),
            ("سقف ویژه ", ("vlimit",)),
            ("سقف‌ویژه ", ("vlimit",)),
            ("سقف ", ("limit",)),
            ("فعالیت ویژه ", ("vactive",)),
            ("فعالیت‌ویژه ", ("vactive",)),
            ("فعالیت ", ("active",)),
            ("استراحت ویژه ", ("vrest",)),
            ("استراحت‌ویژه ", ("vrest",)),
            ("استراحت ", ("rest",)),
            ("فاصله ویژه ", ("vgap",)),
            ("نوسان‌ویژه ", ("vgap",)),
            ("فاصله ", ("gap",)),
            ("سکوت ویژه ", ("vquiet",)),
            ("سکوت ", ("quiet",)),
            ("تنظیم تبادل گزارش ", ("ex",)),
            ("تنظیم‌تبادل گزارش ", ("ex",)),
            ("تنظیم گزارش ", ("ex",)),
            ("تنظیم‌گزارش ", ("ex",)),
            ("گروه ", ("گروه",)),
            ("گروه‌ها ", ("گروه",)),
            ("گروه ها ", ("گروه",)),
            ("افزودن گروه ", ("گروه",)),
            ("حذف گروه ", ("حذف گروه",)),
            ("حذف ", ("del",)),
            ("تبادل ", ("ex",)),
            ("ریسک ", ("risk",)),
            ("امنیت ", ("risk",)),
            ("محافظ ", ("risk",)),
        ):
            if raw.startswith(pref) or low.startswith(pref):
                cmd = cmap[0]
                arg = raw[len(pref):].strip()
                if pref in ("تنظیم تبادل گزارش ", "تنظیم‌تبادل گزارش ",
                             "تنظیم گزارش ", "تنظیم‌گزارش "):
                    # تنظیم‌ها با فرم کوتاه به یک زیر‌دستور قطعی تبدیل شوند.
                    action = re.sub(r"\s+", " ", arg.replace("\u200c", " ")).strip()
                    if action in ("روشن", "لحظه‌ای", "لحظه ای"):
                        arg = "report_live"
                    elif action == "خلاصه":
                        arg = "report_summary"
                    elif action in ("خاموش", "off"):
                        arg = "report_off"
                    elif action.startswith("هر "):
                        arg = "report_every " + action[4:].strip()
                    elif action.startswith(("خلاصه الان", "خلاصه همین الان")):
                        arg = "report_now"
                    else:
                        arg = "report"
                try:
                    out = eng.cmd(cmd, arg, None)
                except Exception as e:
                    out = f"⚠️ {type(e).__name__}: {e}"
                await _say(out, event)
                return
        m = pattern.match(raw)
        if not m:
            return
        cmd, arg = m.group(1), (m.group(2) or "").strip()
        reply_text = None
        try:
            r = await event.get_reply_message()
            if r and r.raw_text:
                reply_text = r.raw_text
        except Exception:
            pass

        # ---- هوش مصنوعی ----
        if cmd.lower() in ("id", "آیدی"):
            try:
                chat = await event.get_chat()
                cid = getattr(chat, "id", None)
                await event.reply(f"🆔 آیدی این چت: `{cid}`")
            except Exception as e:
                await event.reply(f"خطا: {type(e).__name__}")
            return

        if cmd.lower() in ("ai", "هوش"):
            out = await handle_ai(event, arg, reply_text)
            await _say(out, event)
            return

        try:
            out = eng.cmd(cmd, arg, reply_text)
        except Exception as e:
            out = f"⚠️ {type(e).__name__}: {e}"
            traceback.print_exc()
        await _say(out, event)

    async def deliver(item):
        tgt, text, qid = item["target"], item["text"], item["id"]
        tier = item.get("tier") or "standard"
        if DRY_RUN:
            eng.db.mark_sent(qid, None)
            eng.thr[tier].record()
            eng.log("info", "dry_run_send", f"#{qid} → {tgt}")
            return
        try:
            sent = await client.send_message(tgt, text, link_preview=False)
            mid = getattr(sent, "id", None)
            eng.db.mark_sent(qid, mid)
            eng.thr[tier].record()
            eng.log("ok", "sent", f"#{qid} → {tgt}")
        except FloodWaitError as e:
            w = getattr(e, "seconds", 60)
            eng.thr[tier].penalize(w)
            eng.db.mark_failed(qid, f"FloodWait {w}s", retry_at=time.time() + w + 2)
            eng.log("warn", "flood", f"#{qid}: {w}s")
        except (ChatWriteForbiddenError, ChannelPrivateError,
                UsernameNotOccupiedError) as e:
            eng.db.mark_failed(qid, type(e).__name__)
            eng.log("error", "send", f"#{qid}: {type(e).__name__}")
            await note(f"❌ ارسال #{qid} نشد: {type(e).__name__}")
        except SlowModeWaitError as e:
            w = getattr(e, "seconds", 30)
            eng.db.mark_failed(qid, f"SlowMode {w}s", retry_at=time.time() + w + 1)
        except Exception as e:
            eng.db.mark_failed(qid, f"{type(e).__name__}: {e}",
                               retry_at=time.time() + 60)
            eng.log("error", "send", f"#{qid}: {e}")

    # ══════════════════════════════════════════════════
    #  تبادل دوطرفه
    # ══════════════════════════════════════════════════
    async def peer_in_my_channel(user_id):
        """عضو کانال عادی یا VIP هست؟ True / False / None(نامشخص)"""
        if not user_id:
            return None
        chans = []
        for t in ("standard", "vip"):
            ch = (eng.st.prof(t)["channel"] or "").strip()
            if ch and ch not in chans:
                chans.append(ch)
        if not chans:
            return None
        saw_false = False
        for ch in chans:
            try:
                await client(GetParticipantRequest(ch, user_id))
                return True
            except UserNotParticipantError:
                saw_false = True
            except FloodWaitError as e:
                eng.thr["standard"].penalize(getattr(e, "seconds", 60))
                return None
            except Exception as e:
                eng.log("warn", "ex_check", f"{ch}: {type(e).__name__}: {e}")
                return None
        return False if saw_false else None

    async def confirm_peer_membership(user_id):
        """عضویت را حداقل دوبار تأیید می‌کند تا منفی کاذب ندهد.
        اگر درخواست اول False باشد، یک بار دیگر بعد از فاصله تصادفی
        تنظیم‌شده بررسی می‌شود؛ هیچ پیام اضافه‌ای در این فاصله ارسال نمی‌شود.
        """
        first = await peer_in_my_channel(user_id)
        if first is not False:
            return first
        # گاهی انتشار عضویت در API تلگرام چند ثانیه طول می‌کشد.
        await asyncio.sleep(membership_check_delay())
        return await peer_in_my_channel(user_id)

    async def join_link(link):
        """جوین به کانال. برمی‌گرداند (موفق, پیام, عنوان)"""
        if DRY_RUN:
            return True, "joined", "DRY_RUN"
        try:
            if is_invite(link):
                upd = await client(ImportChatInviteRequest(invite_hash(link)))
                title = ""
                chats = getattr(upd, "chats", None)
                if chats:
                    title = getattr(chats[0], "title", "")
                return True, "joined", title
            ent = await client.get_entity(link)
            await client(JoinChannelRequest(ent))
            return True, "joined", getattr(ent, "title", "")

        except UserAlreadyParticipantError:
            return True, "already", ""
        except InviteRequestSentError:
            return False, "درخواست عضویت فرستاده شد — منتظر تأیید ادمین", ""
        except (InviteHashExpiredError, InviteHashInvalidError):
            return False, "لینک منقضی یا نامعتبر است", ""
        except UsernameNotOccupiedError:
            return False, "این یوزرنیم وجود ندارد", ""
        except ChannelPrivateError:
            return False, "کانال خصوصی است یا بن شده‌ای", ""
        except ChannelsTooMuchError:
            return False, "تو حداکثر تعداد کانال ممکن هستی — چندتا لفت بده", ""
        except FloodWaitError as e:
            w = getattr(e, "seconds", 60)
            eng.join_thr.penalize(w)
            eng.db.log("warn", "ex_flood", f"join {link}: {w}s")
            return False, f"FloodWait {w}s", ""
        except Exception as e:
            return False, f"{type(e).__name__}: {e}", ""

    async def leave_link(link):
        if DRY_RUN:
            return True, ""
        try:
            ent = await client.get_entity(link)
            await client(LeaveChannelRequest(ent))
            return True, ""
        except FloodWaitError as e:
            w = getattr(e, "seconds", 60)
            eng.join_thr.penalize(w)
            eng.db.log("warn", "ex_flood", f"leave {link}: {w}s")
            return False, f"FloodWait {w}s"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

    async def reply_joined(rec):
        """متن «جوین شدم» کاربر را روی پیام خود طرف ریپلای می‌کند.
        بدون لینک، بدون آیدی، بدون منشن — فقط همان متنی که تعیین کرده."""
        x = eng.ex_cfg()
        if not x["reply"] or not rec:
            return False
        if rec.get("replied"):
            return False
        outgoing = rec.get("direction") == "out"
        key = "msg_come" if outgoing else "msg_ok"
        body = eng.ex_render(key, rec.get("peer_name") or "", rec["link"])
        if not body and outgoing:
            # سازگاری با تنظیمات قدیمی که فقط msgfirst داشتند.
            body = eng.ex_render("msg_first", rec.get("peer_name") or "", rec["link"])
        if not body and outgoing:
            # اگر فقط «پیام موفق» ثبت شده باشد، پیش‌قدم هم همان متن را می‌گوید.
            body = eng.ex_render("msg_ok", rec.get("peer_name") or "", rec["link"])
        if not body:
            return False
        chat, mid = rec.get("src_chat"), rec.get("src_msg")
        if not chat or not mid:
            return False
        if outgoing:
            delay = max(0, min(3600, int(eng.ex_cfg().get("come_delay_sec", 0) or 0)))
        else:
            delay = response_delay_seconds()
        if delay:
            await asyncio.sleep(delay)
        try:
            if not DRY_RUN:
                await client.send_message(chat, body, reply_to=mid, link_preview=False)
            eng.db.ex_set(rec["id"], replied=1)
            eng.log("ok", "ex_reply" if not DRY_RUN else "dry_run_reply",
                    f"#{rec['id']}")
            return True
        except Exception as e:
            eng.log("warn", "ex_reply", f"#{rec['id']}: {type(e).__name__}: {e}")
            return False

    def joins_left_today():
        # عمداً هیچ سقف روزانه‌ای برای Join وجود ندارد.
        return 999999999

    def reminder_delay():
        x = eng.ex_cfg()
        lo = max(1, int(x.get("reminder_min_sec", 5) or 5))
        hi = max(lo, int(x.get("reminder_max_sec", 15) or 15))
        return random.randint(lo, hi)

    def membership_check_delay():
        """فاصله بی‌صدای بررسی عضویت؛ هر بار دوباره تصادفی انتخاب می‌شود."""
        x = eng.ex_cfg()
        lo = max(1, int(x.get("check_min_sec", 15) or 15))
        hi = max(lo, int(x.get("check_max_sec", 30) or 30))
        return random.randint(lo, hi)

    def response_delay_seconds():
        """تأخیر پاسخ موفق؛ صفر باید واقعاً صفر بماند."""
        v = eng.ex_cfg().get("response_delay_sec")
        try:
            return max(0, min(3600, int(15 if v is None else v)))
        except (TypeError, ValueError):
            return 15

    async def send_not_joined_reminder(rec):
        """متن msg_no را فقط در سقف تنظیم‌شده روی پیام اصلی می‌فرستد؛
        بعد از رسیدن به سقف، بررسی عضویت بی‌صدا ادامه پیدا می‌کند.
        """
        x = eng.ex_cfg()
        if not x["reply"] or not rec:
            return False
        body = eng.ex_render("msg_no", rec.get("peer_name") or "", rec.get("link") or "")
        chat, mid = rec.get("src_chat"), rec.get("src_msg")
        if not body or not chat or not mid:
            return False
        try:
            if not DRY_RUN:
                await client.send_message(chat, body, reply_to=mid, link_preview=False)
            return True
        except Exception as e:
            eng.log("warn", "ex_reminder", f"#{rec['id']}: {type(e).__name__}: {e}")
            return False

    # ---------- پیدا کردن کانال طرف ----------
    async def find_their_channel(event, sender, chat_id):
        """کانال طرف را پیدا می‌کند. اولویت:
           ۱) لینک داخل همین ریپلای
           ۲) لینک در پیام‌های قبلی خودش در همین گروه
           ۳) کانال شخصی روی پروفایلش
        """
        mine = {(eng.st.prof(t)["channel"] or "").lstrip("@").lower()
                for t in ("standard", "vip")}
        mine.discard("")
        if eng.my_username:
            mine.add(eng.my_username.lower())

        def pick(links):
            for l in links:
                if l.lstrip("@").lower() not in mine:
                    return l
            return None

        # ۱) فقط لینک واقعی داخل همان پیام؛ AI اجازه انتخاب لینک ندارد.
        got = pick(extract_links(event.raw_text))
        if got:
            return got, "از پیام خودش"

        # ۲) پیام‌های قبلی همین شخص در همین گروه
        try:
            async for msg in client.iter_messages(chat_id, from_user=sender.id,
                                                  limit=40):
                if msg.id == event.id or not msg.raw_text:
                    continue
                got = pick(extract_links(msg.raw_text))
                if got:
                    return got, "از پیام‌های قبلی‌اش"
        except Exception as e:
            eng.log("warn", "ex_scan", f"{type(e).__name__}: {e}")

        # ۳) کانال شخصی روی پروفایل
        try:
            from telethon.tl.functions.users import GetFullUserRequest
            full = await client(GetFullUserRequest(sender.id))
            pcid = getattr(full.full_user, "personal_channel_id", None)
            if pcid:
                ent = await client.get_entity(pcid)
                u = getattr(ent, "username", None)
                if u and u.lower() not in mine:
                    return "@" + u, "از پروفایلش"
        except Exception:
            pass

        return None, ""

    # ---------- دریافت درخواست تبادل ----------
    @client.on(events.NewMessage(incoming=True))
    async def on_exchange_request(event):
        x = eng.ex_cfg()
        if not x["enabled"]:
            return

        replied_to_me = False
        try:
            r = await event.get_reply_message()
            replied_to_me = bool(
                r and (getattr(r, "out", False)
                       or getattr(r, "sender_id", None) == eng.my_id))
        except Exception:
            pass

        sender = await event.get_sender()
        if not sender or getattr(sender, "bot", False):
            return
        body_text = event.raw_text or ""
        # دستورهای «جوین شو/عضو شو» هرگز ادعای Join نیستند. این منفیِ قطعی
        # قبل از تماس با AI اجرا می‌شود تا حتی پاسخ اشتباه مدل هم اثر نگذارد.
        join_request = eng.ai.looks_like_join_request(body_text)
        local_claim = bool(
            not join_request and
            (eng.ai.looks_like_join(body_text)
             or (x["words"] and any(w.lower() in body_text.lower() for w in x["words"]))
             )
        )
        ai_sniff = None
        # عبارت‌های رایج بدون انتظار شبکه فوراً پردازش می‌شوند؛ AI فقط برای
        # جمله‌های مبهمِ مرتبط، آن هم فقط برای تشخیص claim، استفاده می‌شود.
        relevant = (replied_to_me
                    or getattr(event, "mentioned", False)
                    or local_claim or bool(extract_links(body_text)))
        if event.is_private and not relevant:
            return
        if (not join_request and not local_claim and relevant and eng.ai.ready
                and eng.ai.cfg.get("smart_detect") and body_text.strip()):
            ai_sniff = await eng.ai.sniff(body_text)

        ai_intent = str((ai_sniff or {}).get("intent") or "").strip().lower()
        ai_join_request = ai_intent in ("join_request", "request", "imperative")
        # فقط نتیجه «آیا ادعای Join شده یا نه» از AI استفاده می‌شود؛ درخواست
        # Join و هر عبارت دستوری همیشه false است.
        claim = bool(not join_request and not ai_join_request
                     and (local_claim or (ai_sniff and ai_sniff.get("joined"))))

        if join_request or ai_join_request:
            eng.log("info", "ex_join_request", body_text[:160])
            return

        # کجاها گوش بده
        if event.is_private:
            pass
        else:
            chat = await event.get_chat()
            uname = (getattr(chat, "username", "") or "").lower()
            cid = str(getattr(chat, "id", ""))
            allowed = any(g.strip().lstrip("@").lower() in (uname, cid)
                          for g in x["groups"])
            # ریپلای به پیام خود جفج همیشه درخواست تبادل محسوب می‌شود؛
            # حتی اگر آن گروه قبلاً در فهرست ثبت نشده باشد.
            if not replied_to_me and not (allowed and
                                          (getattr(event, "mentioned", False) or claim
                                           or bool(extract_links(body_text)))):
                return

        # ریپلای خالی/نامرتبط به پیام جفج را هم پردازش نکن؛ فقط ادعای Join
        # یا لینک واقعی کانال، درخواست تبادل محسوب می‌شود.
        if replied_to_me and not claim and not extract_links(body_text):
            return

        if x["words"] and not claim and not replied_to_me:
            return
        sender_name = (f"@{sender.username}" if getattr(sender, "username", None)
                       else (getattr(sender, "first_name", "") or str(sender.id)))

        # پیام‌های عادی PV فقط برای تحلیل/تشخیص هستند؛ AI هیچ پاسخ خودکاری نمی‌فرستد.
        if event.is_private and not extract_links(body_text) and not claim:
            return

        # ── آیا عضو کانال من هست؟ ──
        # یک False منفرد را نتیجه قطعی نگیر؛ قبل از پیام ناموفق دوباره تأیید کن.
        member = await confirm_peer_membership(sender.id)

        async def say(key, channel="", fallbacks=()):
            if not x["reply"]:
                return False
            keys = (key,) + tuple(fallbacks or ())
            t = ""
            used = ""
            for k in keys:
                t = eng.ex_render(k, sender_name, channel)
                if t:
                    used = k
                    break
            # اگر کاربر متنی ثبت نکرد، هیچ پیام خودکاری ارسال نشود.
            if not t:
                return False
            try:
                await event.reply(t)
                eng.log("info", "ex_reply_attempt", f"{sender_name} [{used}]")
                return True
            except Exception as e:
                eng.log("warn", "ex_reply", f"{sender_name}: {type(e).__name__}: {e}")
                return False

        # ── عضو نیست → یک پیام پیش‌فرض؛ بعد فقط بررسی بی‌صدا ──
        if member is False:
            link, _src = await find_their_channel(event, sender, event.chat_id)
            max_rem = max(0, min(3, int(x.get("max_reminders", 1) or 0)))
            send_now = False
            no_link_notice_key = (int(getattr(sender, "id", 0) or 0),
                                  int(getattr(event, "chat_id", 0) or 0))
            if link:
                rec, _ = eng.db.ex_add(sender.id, sender_name, link)
                old_count = max(0, int(rec.get("reminders") or 0)) if rec else 0
                body = eng.ex_render("msg_no", sender_name, link)
                now0 = int(time.time())
                if rec and rec["status"] == "joined":
                    # رکورد پیش‌قدم را خراب نکن؛ فقط در صورت نیاز یک‌بار
                    # به طرف می‌گوییم عضو کانال ما نیست و رابطه Join او حفظ می‌شود.
                    if old_count < max_rem and x["reply"] and body:
                        old_count += 1
                        send_now = True
                        eng.db.ex_set(rec["id"], reminders=old_count,
                                      src_chat=event.chat_id, src_msg=event.id,
                                      note="پیش‌قدم انجام شده؛ طرف هنوز عضو کانال من نیست")
                elif rec and rec["status"] != "rejected":
                    if old_count < max_rem and x["reply"] and body:
                        # فقط اولین پیام را همان لحظه بفرست؛ دفعات بعدی بی‌صدا چک می‌شوند.
                        old_count += 1
                        send_now = True
                        next_reminder = int(
                            now0 + (membership_check_delay()
                                    if old_count >= max_rem else reminder_delay()))
                    else:
                        # حتی وقتی متن پاسخ خاموش است یا سقف یادآوری صفر است،
                        # بررسی عضویت متوقف نمی‌شود.
                        next_reminder = int(now0 + membership_check_delay())
                    note_text = ("یک یادآوری ارسال شد — بررسی عضویت بی‌صدا ادامه دارد"
                                 if old_count >= max_rem and old_count else
                                 "عضو نیست — بررسی بعدی زمان‌بندی شد")
                    eng.db.ex_set(rec["id"], status="pending",
                                  strikes=rec["strikes"] + 1,
                                  src_chat=event.chat_id, src_msg=event.id,
                                  replied=0, reminders=old_count,
                                  next_reminder=next_reminder,
                                  note=note_text)
            else:
                # نبودن لینک نباید باعث سکوت کامل شود؛ متن ناموفقِ ثبت‌شده
                # یک‌بار روی همین پیام ارسال می‌شود، بدون اینکه لینک حدس بزنیم.
                now0 = time.time()
                last_notice = getattr(on_exchange_request, "_no_link_notice", {})
                if not isinstance(last_notice, dict):
                    last_notice = {}
                if (max_rem > 0 and x["reply"]
                        and now0 >= float(last_notice.get(no_link_notice_key, 0) or 0)):
                    send_now = True
                    last_notice[no_link_notice_key] = now0 + 600
                    try:
                        setattr(on_exchange_request, "_no_link_notice", last_notice)
                    except Exception:
                        pass
            eng.log("info", "ex_notmember", sender_name)
            if send_now:
                await say("msg_no")
            # ── رفع باگ: جوینِ طرف مقابل را هم در صف بگذار ──
            # حتی اگر هنوز عضوِ کانالِ من نیست، تبادل انجام شود (مانند پیش‌قدم).
            # رکورد بعد از جوین، توسط چکِ دوره‌ای بررسی می‌شود تا «دروغ‌گوها»
            # (آن‌هایی که ادعا می‌کنند جوین شده‌اند ولی واقعاً نشده‌اند) ثبت و حذف شوند.
            if link:
                rec0, _n = eng.db.ex_add(sender.id, sender_name, link)
                if rec0 and rec0["status"] not in ("joined", "rejected",
                                                    "left", "failed"):
                    eng.db.ex_set(rec0["id"], status="approved", direction="in",
                                  peer_id=sender.id, peer_name=sender_name,
                                  src_chat=event.chat_id, src_msg=event.id,
                                  replied=0, strikes=0)
                    eng.log("info", "ex_reciprocal",
                            f"{sender_name} → {link} (جوینِ طرف در صف)")
                    # اگر متن موفق ثبت‌شده، همین حالا بگو «جوین شدم» را هم می‌زنیم.
                    if x["reply"]:
                        await say("msg_ok", link, ("msg_come", "msg_first"))
            return

        # ── نامشخص ──
        if member is None:
            eng.log("warn", "ex_unknown", f"{sender_name} — عضویت قابل بررسی نبود")
            # حتی وقتی عضویت نامشخص است، جوینِ طرف را متوقف نکن (رفع باگ).
            link, _src = await find_their_channel(event, sender, event.chat_id)
            queued = False
            if link:
                rec0, _n = eng.db.ex_add(sender.id, sender_name, link)
                if rec0 and rec0["status"] not in ("joined", "rejected",
                                                    "left", "failed"):
                    eng.db.ex_set(rec0["id"], status="approved", direction="in",
                                  peer_id=sender.id, peer_name=sender_name,
                                  src_chat=event.chat_id, src_msg=event.id,
                                  replied=0, strikes=0)
                    eng.log("info", "ex_reciprocal",
                            f"{sender_name} → {link} (عضویت نامشخص − در صف)")
                    queued = True
            if queued and x["reply"]:
                await say("msg_ok", link, ("msg_come", "msg_first"))
            else:
                await say("msg_wait")
            if not eng.st.prof("standard")["channel"]:
                await note(f"⚠️ کانال تعیین نشده — نمی‌توانم عضویت را چک کنم.\n"
                           "`کانال عادی @channel`")
            return

        # ── عضو هست → کانالش را پیدا کن ──
        link, src = await find_their_channel(event, sender, event.chat_id)

        if not link:
            eng.log("info", "ex_nolink", sender_name)
            await say("msg_nolink")
            await note(f"🔎 یکی ریپلای زد و **عضو هم هست**، ولی کانالش را پیدا نکردم.\n"
                       f"از: {sender_name}\n"
                       "دستی اضافه کن: `تبادل افزودن @channel`")
            return

        rec, is_new = eng.db.ex_add(sender.id, sender_name, link)
        if not rec:
            return
        if rec["status"] == "joined":
            delay = response_delay_seconds()
            if delay:
                await asyncio.sleep(delay)
            await say("msg_ok", rec.get("link") or "", ("msg_come", "msg_first"))
            return
        if rec["status"] == "rejected":
            return

        eng.db.ex_set(rec["id"], src_chat=event.chat_id, src_msg=event.id,
                      replied=0, peer_id=sender.id, peer_name=sender_name)

        if x["auto_join"]:
            eng.db.ex_set(rec["id"], status="approved", strikes=0,
                          note=f"عضو است ({src})")
            eng.log("info", "ex_approved", f"{sender_name} → {link} ({src})")
            # متن «جوین شدم» بعد از جوینِ واقعی ریپلای می‌شود
        else:
            eng.db.ex_set(rec["id"], status="pending",
                          note=f"✅ عضو است — منتظر تأیید تو ({src})")
            await say("msg_wait")
            await note(f"🔁 **درخواست تبادل**\n\nاز: {sender_name}\n"
                       f"کانال: `{link}` ({src})\nوضعیت: ✅ عضو کانال من هست\n\n"
                       f"`تبادل تأیید {rec['id']}` جوین • "
                       f"`تبادل رد {rec['id']}` رد")

    # ---------- اسکن گروه‌ها: خودت پیش‌قدم شو ----------
    async def scan_groups(manual=False):
        """از هر گروه ثبت‌شده فقط پیام‌های جدیدِ دارای لینک را بررسی می‌کند.
        پیش‌فرض تازه‌ترین لینک جدید است.
        زمان واقعی Join با min_join_gap_sec/max_join_gap_sec کنترل می‌شود."""
        x = eng.ex_cfg()
        if not x["groups"]:
            return 0, "گروهی تعیین نشده"

        mine = {(eng.st.prof(t)["channel"] or "").lstrip("@").lower()
                for t in ("standard", "vip")}
        mine.discard("")
        if eng.my_username:
            mine.add(eng.my_username.lower())

        last = x.get("scan_last") or {}
        found = 0
        max_age = max(30, int(x.get("scan_max_age_sec", 300) or 300))
        scan_now = time.time()

        for g in x["groups"]:
            key = str(g)
            previous = int(last.get(key, 0) or 0)
            newest = previous
            candidates = []
            try:
                # Telegram پیام‌ها را از جدیدترین به قدیمی‌ترین می‌دهد.
                # پیش‌فرض مورد ۱ یعنی تازه‌ترین لینک؛ اگر وجود نداشت،
                # آخرین پیام معتبر انتخاب می‌شود.
                pick = max(1, int(x.get("scan_pick", 1) or 1))
                async for msg in client.iter_messages(g, limit=x["scan_limit"]):
                    if not msg:
                        continue
                    msg_id = int(getattr(msg, "id", 0) or 0)
                    newest = max(newest, msg_id)
                    # پیام‌هایی که قبلاً تا این شناسه دیده شده‌اند، دوباره
                    # کاندید Join نشوند؛ فقط پیام جدید را بررسی کن.
                    if msg_id <= previous:
                        continue
                    if msg.out:
                        continue
                    msg_date = getattr(msg, "date", None)
                    if msg_date is not None:
                        try:
                            age = scan_now - msg_date.timestamp()
                            if age > max_age:
                                continue
                        except Exception:
                            pass

                    sender = None
                    try:
                        sender = await msg.get_sender()
                    except Exception:
                        pass
                    if not sender or getattr(sender, "bot", False):
                        continue
                    if getattr(sender, "id", 0) == eng.my_id:
                        continue

                    links = [l for l in extract_links(msg.raw_text or "")
                             if l.lstrip("@").lower() not in mine]
                    if not links:
                        continue
                    candidates.append((msg, sender, links[0]))
                    if len(candidates) >= pick:
                        break

                if candidates:
                    selected_index = min(pick, len(candidates))
                    msg, sender, link = candidates[selected_index - 1]
                    existing = eng.db.ex_by_link(link)
                    sender_name = (f"@{sender.username}"
                                   if getattr(sender, "username", None)
                                   else (getattr(sender, "first_name", "")
                                         or str(sender.id)))
                    if not existing:
                        rec, is_new = eng.db.ex_add(sender.id, sender_name, link)
                        if rec and is_new:
                            # رفع باگ: peer_id حتماً ست شود تا رکوردِ پیش‌قدمِ جدید
                            # هم در ex_due چک شود (طرف «نیامد» → strike/لفت/نیومدی).
                            eng.db.ex_set(rec["id"], status="approved",
                                          direction="out", src_chat=msg.chat_id,
                                          src_msg=msg.id, replied=0,
                                          peer_id=sender.id, peer_name=sender_name,
                                          note=f"پیش‌قدم — پیام شماره {selected_index} از جدیدترین‌ها")
                            found += 1
                    elif existing.get("status") in ("failed", "left"):
                        # پیام جدیدی از همان کانال آمده؛ دوباره در صف Join قرار بده.
                        eng.db.ex_set(existing["id"], status="approved",
                                      peer_id=sender.id, peer_name=sender_name,
                                      direction="out", src_chat=msg.chat_id,
                                      src_msg=msg.id, replied=0,
                                      strikes=0, note="پیام جدید — دوباره در صف Join")
                        found += 1

            except FloodWaitError as e:
                w = getattr(e, "seconds", 60)
                eng.log("warn", "scan_flood", f"{g}: {w}s")
                await asyncio.sleep(min(w, 60))
                continue
            except Exception as e:
                eng.log("warn", "scan", f"{g}: {type(e).__name__}: {e}")
                continue

            if newest:
                last[key] = newest
            # کوتاه نگه‌دار تا فرمان پنل معطل اسکن چند گروه نشود.
            await asyncio.sleep(0.5)

        x["scan_last"] = last
        eng.st.save()
        if found:
            eng.log("info", "scan", f"{found} آخرین پیام دارای لینک ثبت شد")
        return found, ""

    # ---------- اسکن مستقل پیش‌قدم ----------
    async def scan_loop():
        # اسکن مستقل است تا بررسی‌های طولانی عضویت، فرصت هر ۳۰ ثانیه
        # برای پیدا کردن کانال جدید را عقب نیندازد.
        last_scan = [0.0]
        while True:
            try:
                x = eng.ex_cfg()
                if not x["enabled"]:
                    await asyncio.sleep(2)
                    continue
                # ۰) اسکن گروه‌ها (حالت پیش‌قدم)
                now_t = time.time()
                manual = bool(x.pop("_scan_now", False))
                scan_seconds = max(30, int(x.get("scan_every_sec", 30) or 30))
                if manual or (x["initiate"] and
                              now_t - last_scan[0] >= scan_seconds):
                    last_scan[0] = now_t
                    n, err = await scan_groups(manual)
                    if manual:
                        if err:
                            await note(f"🔍 اسکن انجام نشد — {err}")
                        else:
                            wait = eng.join_thr.wait_time()
                            left = joins_left_today()
                            if left <= 0:
                                state = "به‌دلیل خطای داخلی امکان Join نیست"
                            elif wait > 0:
                                state = f"در صف است؛ حدود {secs(int(wait))} دیگر امتحان می‌کنم"
                            else:
                                state = "همین حالا برای Join امتحان می‌کنم"
                            await note(f"🔍 اسکن تمام شد — {fa(n)} کانال تازه پیدا شد؛ {state}.")
                    elif n:
                        wait = eng.join_thr.wait_time()
                        left = joins_left_today()
                        if left <= 0:
                            state = "به‌دلیل خطای داخلی امکان Join نیست"
                        elif wait > 0:
                            state = f"در صف Join؛ حدود {secs(int(wait))} دیگر"
                        else:
                            state = "برای Join همین نوبت"
                        await note(f"🔍 {fa(n)} کانال تازه پیدا شد — {state}.")

                # زمان‌بندی دقیق‌تر از حلقه‌ی اصلی تبادل.
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                eng.log("error", "scan_loop", f"{type(e).__name__}: {e}")
                await asyncio.sleep(5)

    # ---------- کارگر بررسی عضویت ----------
    async def membership_loop():
        # بررسی‌های ۱۵ تا ۳۰ ثانیه‌ای نباید صف Join را متوقف کنند.
        while True:
            try:
                x = eng.ex_cfg()
                if not x["enabled"]:
                    await asyncio.sleep(20)
                    continue
                # برای ضداسپم، پیام عضو‌نشده فقط تا سقف تنظیم‌شده فرستاده می‌شود؛
                # پس از آن فقط بررسی عضویت انجام می‌گیرد.
                now_rem = int(time.time())
                for rec in eng.db.ex_reminder_due(now_rem, 20):
                    if not rec.get("peer_id"):
                        continue
                    still = await confirm_peer_membership(rec["peer_id"])
                    now2 = int(time.time())
                    max_rem = max(0, min(3, int(x.get("max_reminders", 1) or 0)))
                    if still is True:
                        eng.db.ex_set(rec["id"], status="approved",
                                      reminders=max_rem, next_reminder=0,
                                      strikes=0, note="عضو شد — آماده Join")
                    elif still is False:
                        count = int(rec.get("reminders") or 0)
                        if count < max_rem:
                            sent = await send_not_joined_reminder(rec)
                            if sent:
                                count += 1
                            nxt = (int(now2 + reminder_delay())
                                   if count < max_rem else
                                   int(now2 + membership_check_delay()))
                            rem_note = ("یادآوری ارسال شد"
                                        if count < max_rem
                                        else "سقف یادآوری رسید — فقط عضویت را چک می‌کنم")
                        else:
                            # بعد از رسیدن به سقف پیام، پیام دیگری نفرست؛ اما اگر طرف
                            # بعداً عضو شد، همچنان بتوانیم عضویتش را بفهمیم.
                            nxt = int(now2 + membership_check_delay())
                            rem_note = "سقف یادآوری رسید — فقط عضویت را چک می‌کنم"
                        eng.db.ex_set(rec["id"], reminders=count,
                                      next_reminder=nxt, note=rem_note)
                    else:
                        eng.db.ex_set(rec["id"],
                                      next_reminder=int(now2 + membership_check_delay()),
                                      note="بررسی عضویت نامشخص است")

                # ۳) چک دوره‌ای: طرف هنوز عضو کانال من هست؟
                # زمان هر بررسی از نو و تصادفی بین ۱۵ تا ۳۰ ثانیه انتخاب می‌شود.
                for rec in eng.db.ex_due(int(time.time()), 5):
                    if not rec["peer_id"]:
                        now_no_peer = int(time.time())
                        eng.db.ex_set(rec["id"], last_check=now_no_peer,
                                      next_check=now_no_peer + membership_check_delay())
                        continue
                    still = await confirm_peer_membership(rec["peer_id"])
                    now = int(time.time())
                    if still is True:
                        eng.db.ex_set(rec["id"], last_check=now,
                                      next_check=now + membership_check_delay(),
                                      strikes=0, note="عضو است")
                    elif still is False:
                        st = rec["strikes"] + 1
                        if st >= x["max_strikes"]:
                            ok, err = await leave_link(rec["link"])
                            eng.db.ex_set(rec["id"],
                                          status="left" if ok else "failed",
                                          last_check=now, next_check=0,
                                          strikes=st,
                                          note="لفت داد → لفت دادم" if ok else err)
                            eng.log("info", "ex_left", f"#{rec['id']} {rec['link']}")
                            if ok and rec.get("direction") == "out":
                                # بعد از لفت، نوبت بعدی را از گروه بررسی کن.
                                x["_scan_now"] = True
                            # رفع باگ: به کسی که جوین کرده ولی واقعاً عضو نشده
                            # (دروغگو) همین‌جا «نیومدی» بگو — نه فقط پیش‌قدم‌ها.
                            if x["reply"] and rec.get("peer_id") and ok:
                                rec2 = eng.db.ex_get(rec["id"])
                                await send_not_joined_reminder(rec2)
                            if eng.ex_cfg().get("report_mode", "live") == "live":
                                await note(eng.ex_live_leave_text(rec, "" if ok else err))
                        else:
                            # در مرز، فقط یک‌بار یادآوری «نیومدی» بفرست؛ سپس بی‌صدا.
                            reminded = int(rec.get("reminders") or 0)
                            if x["reply"] and rec.get("peer_id") and st == 1 \
                                    and reminded < max(1, int(x.get("max_reminders", 1) or 1)):
                                sent = await send_not_joined_reminder(eng.db.ex_get(rec["id"]))
                                if sent:
                                    reminded += 1
                            eng.db.ex_set(rec["id"], last_check=now,
                                          next_check=now + membership_check_delay(),
                                          strikes=st, reminders=reminded,
                                          note=f"عضو نیست ({st}/{x['max_strikes']})")
                            eng.log("info", "ex_strike",
                                    f"#{rec['id']} {st}/{x['max_strikes']}")
                    else:
                        eng.db.ex_set(rec["id"], last_check=now,
                                      next_check=now + membership_check_delay())
                    await asyncio.sleep(2)

                # برای دقت فاصله‌ی یادآوری، بیشتر از دو ثانیه در صف نمان.
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                eng.log("error", "membership_loop", f"{type(e).__name__}: {e}")
                await asyncio.sleep(5)

    # ---------- کارگر صف Join ----------
    async def exchange_worker():
        while True:
            try:
                x = eng.ex_cfg()

                # ارسال دوباره‌ی پیام برای Joinهایی که قبلاً انجام شده‌اند.
                # این عملیات حتی اگر تبادل خاموش باشد هم انجام می‌شود.
                reply_now = x.pop("_reply_now", None)
                if reply_now:
                    rec = eng.db.ex_get(int(reply_now))
                    if rec and rec.get("status") == "joined":
                        eng.db.ex_set(rec["id"], replied=0)
                        sent_reply = await reply_joined(eng.db.ex_get(rec["id"]))
                        await note(f"💬 پیام تبادل #{fa(rec['id'])} "
                                   + ("ارسال شد." if sent_reply else "ارسال نشد."))
                    eng.st.save()

                if not x["enabled"]:
                    await asyncio.sleep(20)
                    continue

                # ۱) لفت‌های دستی
                for rec in eng.db.ex_list("leaving", 5):
                    ok, err = await leave_link(rec["link"])
                    eng.db.ex_set(rec["id"], status="left" if ok else "failed",
                                  note="لفت دستی" if ok else err)
                    eng.log("info" if ok else "warn", "ex_leave",
                            f"#{rec['id']} {rec['link']} {err}")
                    await asyncio.sleep(3)

                # ۲) جوین تأییدشده‌ها
                if eng.join_thr.wait_time() <= 0 and joins_left_today() > 0:
                    # ── سقف جوین/ساعت (محدودیت آهسته، خاموش پیش‌فرض) ──
                    hw = eng.hour_cap_wait()
                    if hw > 0:
                        # هر ۲ دقیقه یک‌بار نوتیف بده (ضد اسپم).
                        last_blocked = int(x.get("_hour_cap_blocked", 0) or 0)
                        if int(time.time()) - last_blocked > 120:
                            await note(f"⏸ سقف جوین/ساعت: در این ساعت به حد "
                                       f"{fa(int(x.get('hour_cap', 60) or 60))} رسیدی. "
                                       f"حدود {secs(hw)} دیگر ادامه می‌دهم.")
                        x["_hour_cap_blocked"] = int(time.time())
                        eng.st.save()
                        await asyncio.sleep(min(hw, 20))
                        continue
                    rec = None
                    for r in eng.db.ex_list("approved", 5):
                        rec = r
                        break
                    if rec:
                        max_age = max(30, int(eng.ex_cfg().get("scan_max_age_sec", 300) or 300))
                        queued_age = time.time() - float(rec.get("created_at") or time.time())
                        if rec.get("direction") == "out" and queued_age > max_age:
                            stale_note = f"لینک بیش از {secs(max_age)} قدیمی است؛ Join نشد"
                            eng.db.ex_set(rec["id"], status="failed", note=stale_note)
                            eng.log("info", "ex_stale", f"#{rec['id']} {rec['link']}")
                            await note(f"🕒 کانال قدیمی رد شد: `{rec['link']}`\n{stale_note}")
                            await asyncio.sleep(1)
                            continue
                        eng.log("info", "ex_join_try", f"#{rec['id']} {rec['link']}")
                        try:
                            ok, msg, title = await asyncio.wait_for(
                                join_link(rec["link"]), timeout=60)
                        except asyncio.TimeoutError:
                            ok, msg, title = False, "TimeoutError: درخواست Join بیشتر از ۶۰ ثانیه طول کشید", ""
                        if ok:
                            eng.join_thr.record()
                            joined_now = int(time.time())
                            eng.db.ex_set(rec["id"], status="joined",
                                          joined_at=joined_now,
                                          last_check=joined_now,
                                          next_check=joined_now + membership_check_delay(),
                                          channel_title=title or None,
                                          strikes=0,
                                          note="جوین شدم" if msg == "joined"
                                               else "از قبل عضو بودم")
                            eng.log("ok", "ex_join", f"#{rec['id']} {rec['link']}")

                            # ریپلای «جوین شدم» روی پیام خود طرف
                            sent_reply = await reply_joined(eng.db.ex_get(rec["id"]))

                            if eng.ex_cfg().get("report_mode", "live") == "live":
                                await note(eng.ex_live_join_text(rec, title, sent_reply))
                        else:
                            if msg.startswith("FloodWait"):
                                eng.db.ex_set(rec["id"], note=msg)
                                await note(f"⏳ تبادل — {msg}\nصبر می‌کنم و ادامه می‌دهم.")
                            elif msg.startswith("درخواست عضویت"):
                                # درخواست عضویت با تأیید مدیر تمام نشده؛ شکست قطعی نیست.
                                eng.db.ex_set(rec["id"], status="pending", note=msg)
                                eng.log("info", "ex_join_pending", f"#{rec['id']} {msg}")
                                await note(f"⏳ درخواست عضویت برای `{rec['link']}` فرستاده شد.\n"
                                           "بعد از تأیید مدیر، `تبادل تأیید شماره` را بفرست.")
                            else:
                                transient = msg.startswith((
                                    "TimeoutError", "RPCError", "ConnectionError",
                                    "OSError", "NetworkError", "ServerError"))
                                if transient:
                                    eng.join_thr.penalize(15)
                                    eng.db.ex_set(rec["id"], status="approved",
                                                  note=f"تلاش دوباره بعد از خطای موقت: {msg}")
                                    eng.log("warn", "ex_join_retry", f"#{rec['id']} {msg}")
                                    await note(f"⏳ Join موقتاً نشد: `{rec['link']}` — {msg}؛ "
                                               "۱۵ ثانیه دیگر دوباره امتحان می‌کنم.")
                                else:
                                    eng.db.ex_set(rec["id"], status="failed", note=msg)
                                    # مهم: فقط خطاهایِ «محدودیتِ حسابیِ خودِ اکانت» در پایشِ
                                    # واقعیِ ریپ حساب می‌شوند. خطاهایی که از مشکلِ خودِ
                                    # لینکِ خریدار است (منقضی/خصوصی/یوزرنیم ناموجود) را
                                    # جدا ثبت می‌کنیم تا باعث توقفِ اجباریِ کاذب نشوند.
                                    account_limit = any(
                                        h in msg for h in ("حداکثر تعداد کانال",
                                                           "ChannelsTooMuch"))
                                    kind = "ex_join_limit" if account_limit else "ex_join_fail"
                                    eng.log("warn", kind, f"#{rec['id']} {msg}")
                                    await note(f"❌ جوین نشد: `{rec['link']}` — {msg}")


                # صف Join مستقل و سریع می‌چرخد.
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                eng.log("error", "ex_worker", f"{type(e).__name__}: {e}")
                traceback.print_exc()
                await asyncio.sleep(15)

    async def sender_loop():
        while True:
            try:
                if eng.st["paused"]:
                    await asyncio.sleep(5)
                    continue
                did, nap = False, 5.0
                for tier in ("vip", "standard"):
                    ph, rem = eng.cyc[tier].phase()
                    if ph != "active":
                        nap = min(nap, max(2.0, min(30.0, rem)))
                        continue
                    w = eng.thr[tier].wait_time()
                    if w > 0:
                        nap = min(nap, min(w, 10.0))
                        continue
                    item = eng.db.next_pending(tier)
                    if item:
                        await deliver(item)
                        did = True
                if not did:
                    await asyncio.sleep(max(1.0, nap))
            except asyncio.CancelledError:
                raise
            except Exception as e:
                eng.log("error", "sender", f"{type(e).__name__}: {e}")
                traceback.print_exc()
                await asyncio.sleep(5)

    async def status_loop():
        while True:
            try:
                eng.write_status()
            except Exception:
                pass
            await asyncio.sleep(60)

    async def report_loop():
        """گزارش خلاصه را فقط در حالت summary و فقط در PV ارسال می‌کند."""
        while True:
            try:
                x = eng.ex_cfg()
                manual = bool(x.pop("_report_now", False))
                if manual:
                    await note(eng.ex_report_text())
                    await asyncio.sleep(1)
                    continue
                elif x.get("report_mode", "live") == "summary":
                    interval = max(3600, int(x.get("report_summary_interval_sec", 86400) or 86400))
                    now_r = int(time.time())
                    last = int(x.get("report_last_sent", 0) or 0)
                    if not last:
                        x["report_last_sent"] = now_r
                        eng.st.save()
                    elif now_r - last >= interval:
                        counts = eng.db.ex_report_counts(last)
                        if any(counts[k] for k in ("joined", "left", "failed")):
                            await note(eng.ex_report_text(last))
                        x["report_last_sent"] = now_r
                        eng.st.save()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                eng.log("error", "report_loop", f"{type(e).__name__}: {e}")
                await asyncio.sleep(30)

    async def risk_loop():
        """محافظ ریپورت، دو لایه:
          ۱) پایشِ «واقعی» (همیشه فعال): فقط وقتی اکانت واقعاً در مرز ریپ است
             (FloodWait/خطاهای واقعی) تبادل را اجباراً خاموش می‌کند. در حالت
             پیش‌فرض روشن می‌ماند حتی اگر «توقف بر امتیاز» خاموش باشد.
          ۲) توقف بر «امتیازِ انتزاعی» (خاموش در حالت پیش‌فرض): فقط وقتی
             روی=True باشد.
        هر لایه خاموشیِ «خودش» را برمی‌گرداند و یک قفلِ موقت (`_off_until`)
        و دلیل (`_off_reason`) دارد تا وقتی هر دو فعال‌اند، خاموشیِ یکی توسط
        دیگری فوراً باطل نشود. ضد اسپمِ نوتیف نیز دارد."""
        while True:
            try:
                rc = eng.st["risk"]
                x = eng.ex_cfg()
                now_t = int(time.time())
                auto_off = bool(rc.get("_auto_off"))
                off_until = int(rc.get("_off_until", 0) or 0)
                off_reason = str(rc.get("_off_reason", "") or "")

                # ── تصمیم‌های خاموشیِ هر لایه ──
                stop_hard = False
                hard_meta = {}
                if rc.get("hard_on", True):
                    edge, rparts, hard_meta = eng.real_risk_edge(now_t)
                    stop_hard = bool(edge)
                stop_score = False
                risk = None
                if rc.get("on", True):
                    risk, _p, _m = eng.risk_current()
                    stop_score = bool(risk >= float(rc.get("trigger", 75)))

                # ── خاموشی (اجباری) ──
                if x["enabled"] and (stop_hard or stop_score):
                    x["enabled"] = False
                    rc["_auto_off"] = True
                    rc["_last_off"] = now_t
                    rc["_off_reason"] = "hard" if stop_hard else "score"
                    rc["_off_until"] = now_t + (600 if stop_hard else 120)
                    rc["_auto_off"] = True
                    rc["_last_alert"] = now_t
                    eng.st.save()
                    if stop_hard:
                        eng.log("warn", "risk_hard_off",
                                f"مرز ریپ (امتیاز واقعی {hard_meta.get('score')}) → تبادل خاموش")
                        await note(f"🛡 **محافظ ریپورت — توقف اجباری**: اکانت در مرز ریپ است "
                                   f"(امتیازِ واقعی {hard_meta.get('score')}، فلاد "
                                   f"{hard_meta.get('flood')}/{hard_meta.get('fails_10')} خطا در ۱۰د). "
                                   "تبادل را **خاموش** کردم تا اکانت در امان بماند.\n"
                                   f"`ریسک بررسی` برای جزئیات")
                    else:
                        eng.log("warn", "risk_off",
                                f"ریسک {risk}% >= {float(rc.get('trigger', 75)):.0f}% → تبادل خاموش")
                        await note(f"🛡 **محافظ ریپورت**: ریسک به {risk}% رسید "
                                   f"(آستانه {float(rc.get('trigger', 75)):.0f}%)، تبادل را "
                                   "**خاموش** کردم. اکانت در امان است.\n"
                                   f"`ریسک بررسی` برای جزئیات")
                # ── بازگشایی (فقط خاموشیِ همان لایه، بعد از قفلِ موقت) ──
                elif (auto_off and not x["enabled"]
                      and now_t >= off_until
                      and ((off_reason == "hard" and not (rc.get("hard_on", True) and stop_hard))
                           or (off_reason == "score"
                               and (risk is not None)
                               and risk < float(rc.get("resume", 55))))):
                    x["enabled"] = True
                    rc["_auto_off"] = False
                    rc["_off_until"] = 0
                    rc["_off_reason"] = ""
                    rc["_last_alert"] = now_t
                    eng.st.save()
                    eng.log("info", "risk_on",
                            f"{off_reason} رفع شد → تبادل روشن")
                    await note(f"🛡 خطرِ ریپ برطرف شد (دلیل: {off_reason}). "
                               "تبادل را دوباره **روشن** کردم.")
                # ── هشدار پیشگیرانه نزدیک‌بودن به آستانه‌ی امتیاز ──
                elif (not auto_off and x["enabled"] and rc.get("on", True)
                      and 0.9 * float(rc.get("trigger", 75)) <= risk < float(rc.get("trigger", 75))
                      and now_t - int(rc.get("_last_alert", 0) or 0) > 3600):
                    rc["_last_alert"] = now_t
                    eng.st.save()
                    await note(f"⚠️ ریسک ریپورت به {risk}% رسید "
                               f"(آستانه {float(rc.get('trigger', 75)):.0f}%). "
                               "به‌زودی تبادل خاموش می‌شود.")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                eng.log("error", "risk_loop", f"{type(e).__name__}: {e}")
            await asyncio.sleep(max(10, int(eng.st["risk"].get("check_interval_sec", 60) or 60)))

    task = asyncio.create_task(sender_loop())
    ex_task = asyncio.create_task(exchange_worker())
    scan_task = asyncio.create_task(scan_loop())
    member_task = asyncio.create_task(membership_loop())
    report_task = asyncio.create_task(report_loop())
    risk_task = asyncio.create_task(risk_loop())
    st_task = asyncio.create_task(status_loop())

    hint = ""
    if not eng.st.prof("standard")["channel"]:
        hint = "\n\n📡 کانال هنوز تعیین نشده: `کانال @channel`"
    await note(f"🟢 جفج {VERSION} آنلاین شد — پنل جدید\n\n"
               f"`پنل` داشبورد • `راهنما` راهنما{hint}")

    try:
        await client.run_until_disconnected()
    finally:
        for t in (task, ex_task, scan_task, member_task, report_task, risk_task, st_task):
            t.cancel()
            try:
                await t
            except (asyncio.CancelledError, Exception):
                pass

    eng.log("warn", "disconnected", "اتصال قطع شد")
    return "retry"


async def run_bot():
    print(f"\n{BUILD_TAG}", flush=True)
    if need_telethon():
        print("\n📦 Telethon نصب نیست — نصبش می‌کنم…")
        os.system(f'"{sys.executable}" -m pip install telethon')
        if need_telethon():
            print("\n❌ نصب خودکار نشد. دستی بزن:\n\n   pip install telethon\n")
            return 1

    creds = ensure_creds()
    if not creds:
        return 1

    eng = Engine()
    print(f"\n{'═' * 50}\n  جفج {VERSION} — سلف‌بات تلگرام\n{'═' * 50}", flush=True)
    print(f"  شماره: {creds.get('phone') or 'هنوز نیست — پایین ازت می‌پرسد'}", flush=True)
    if os.path.exists(SESSION + ".session"):
        print("  سشن از قبل هست؛ اگر وصل شود دیگر شماره نمی‌پرسد.", flush=True)

    backoff = 10
    while True:
        try:
            r = await connect_and_run(eng, creds)
            if r == "stop":
                return 1
            backoff = 10
        except KeyboardInterrupt:
            raise
        except Exception as e:
            eng.log("error", "fatal", f"{type(e).__name__}: {e}")
            traceback.print_exc()
        print(f"\n🔄 اتصال قطع شد — {backoff} ثانیه دیگر دوباره وصل می‌شوم…")
        print("   (پیام‌های صف حفظ شده‌اند. Ctrl+C برای خروج)")
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 300)


def main():
    try:
        return asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n\nخاموش شد. صف و تنظیمات ذخیره شدند.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

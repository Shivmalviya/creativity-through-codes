import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = "YOUR_BOT_TOKEN"

# ---------- DB ----------
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    run_time TEXT,
    message TEXT
)
""")
conn.commit()

# ---------- JOB ----------
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"⏰ Task Reminder:\n{job.data}"
    )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (job.name,))
    conn.commit()

# ---------- COMMANDS ----------
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date, time = context.args[0], context.args[1]
        message = " ".join(context.args[2:])
        run_time = datetime.fromisoformat(f"{date} {time}")

        cursor.execute(
            "INSERT INTO tasks (chat_id, run_time, message) VALUES (?, ?, ?)",
            (update.effective_chat.id, run_time.isoformat(), message)
        )
        task_id = cursor.lastrowid
        conn.commit()

        context.job_queue.run_once(
            send_reminder,
            run_time,
            chat_id=update.effective_chat.id,
            data=message,
            name=str(task_id)
        )

        await update.message.reply_text("✅ Task reminder added!")

    except Exception:
        await update.message.reply_text(
            "❌ Usage:\n/add YYYY-MM-DD HH:MM Task description"
        )

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT id, run_time, message FROM tasks WHERE chat_id = ?",
        (update.effective_chat.id,)
    )
    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("📭 No upcoming tasks.")
        return

    text = "📋 Your Tasks:\n"
    for i, (task_id, run_time, msg) in enumerate(rows, start=1):
        text += f"{i}. [{task_id}] {run_time} — {msg}\n"

    await update.message.reply_text(text)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_id = context.args[0]
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

        for job in context.job_queue.jobs():
            if job.name == task_id:
                job.schedule_removal()

        await update.message.reply_text("🗑 Task deleted.")
    except Exception:
        await update.message.reply_text("❌ Usage: /delete TASK_ID")

# ---------- STARTUP ----------
async def restore_jobs(app):
    cursor.execute("SELECT id, chat_id, run_time, message FROM tasks")
    for task_id, chat_id, run_time, msg in cursor.fetchall():
        app.job_queue.run_once(
            send_reminder,
            datetime.fromisoformat(run_time),
            chat_id=chat_id,
            data=msg,
            name=str(task_id)
        )

app = ApplicationBuilder().token(BOT_TOKEN).post_init(restore_jobs).build()
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("delete", delete))

app.run_polling()
import time
import sys
import os

# =========================
# COLORS
# =========================

PINK = "\033[38;5;213m"
PURPLE = "\033[38;5;141m"
GOLD = "\033[38;5;220m"
CYAN = "\033[38;5;117m"
WHITE = "\033[97m"
GREEN = "\033[38;5;120m"

BOLD = "\033[1m"
RESET = "\033[0m"


# =========================
# TYPING EFFECT
# =========================

def type_text(text, color=WHITE, speed=0.06):
    for char in text:
        sys.stdout.write(f"{BOLD}{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    print()


def pause(seconds):
    time.sleep(seconds)


# =========================
# CLEAR TERMINAL
# =========================

os.system("cls" if os.name == "nt" else "clear")


# =========================
# INTRO
# =========================

type_text("✨ Searching through lifetimes...", PURPLE, 0.045)
pause(0.8)

type_text('💗 Connection Found: "HER"', PINK, 0.055)
pause(1.2)



print()


# =========================
# MAIN LINES
# =========================

type_text("🫂 Some people enter your life...", GOLD, 0.065)
pause(0.8)

type_text("   and somehow become a part of it.", PINK, 0.065)
pause(1)

type_text("🌙 I never searched for perfection.", PURPLE, 0.065)
pause(0.8)

type_text("   I just found something that felt like home.", GOLD, 0.065)
pause(1.2)

print()


# =========================
# FINAL
# =========================

type_text("💫 Connection status:", CYAN, 0.06)
pause(0.5)

type_text("████████████████ 100%", GREEN, 0.07)
pause(0.8)

type_text("❤️ FOREVER", PINK, 0.10)

pause(2)

print()
type_text("_", WHITE, 0.2)

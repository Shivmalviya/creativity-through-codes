import sys
import time

def type_lyrics(text, delay=0.04):
    """Har character ko smooth type karne ke liye"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)

def play_reel_lyrics():
    print("\n--- Starting Lyric Video --- \n")
    time.sleep(1) # Initial startup pause
    
    # 1. Pehli Line
    type_lyrics("aaj phir")
    time.sleep(0.4)       # Word ke beech ka pause
    type_lyrics(" tum pe")
    time.sleep(0.5)       # Word ke beech ka pause
    type_lyrics(" pyaar aayaa hai\n")
    time.sleep(1.2)       # Line khatam hone ke baad ka pause

    # 2. Dusri Line
    type_lyrics("aaj phir")
    time.sleep(0.4)
    type_lyrics(" tum pe")
    time.sleep(0.5)
    type_lyrics(" pyaar aayaa hai\n")
    time.sleep(2.2)       # Bada pause / Transition beat drop gap

    # 3. Teesri Line
    type_lyrics("behad aur beshumaar aayaa hai\n")
    time.sleep(1.5)

    # 4. Chauthi Line
    type_lyrics("aaj phir")
    time.sleep(0.4)
    type_lyrics(" tum pe")
    time.sleep(0.5)
    type_lyrics(" pyaar aayaa hai\n")
    time.sleep(1.2)

    # 5. Paanchvi Line
    type_lyrics("aaj phir")
    time.sleep(0.4)
    type_lyrics(" tum pe")
    time.sleep(0.5)
    type_lyrics(" pyaar aayaa hai\n")
    time.sleep(2.2)

    # 6. Chhatthi Line
    type_lyrics("behad aur beshumaar aayaa hai\n")
    
    print("\n\n--- Reel Ended ---")

# Script ko run karne ke liye function call
if __name__ == "__main__":
    play_reel_lyrics()
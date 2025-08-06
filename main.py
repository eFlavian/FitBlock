import tkinter as tk
from datetime import datetime, timedelta
import sys
import os
import Quartz
import subprocess
import threading
import time
# pip install pyobjc pynput
# pip install --upgrade pyobjc pyobjc-framework-AppKit pyobjc-framework-Quartz
# brew install terminal-notifier

# Go to System Settings > Privacy & Security > Accessibility.
# Add and enable Terminal.app (/Applications/Utilities/Terminal.app) or your IDE (e.g., PyCharm).
# If prompted, restart Terminal or your IDE after granting permissions.
# brew install python-tk
# sudo python3 block_mac.py

BLOCK_DURATION = 120  #seconds

def send_macos_notification(title, message):
    subprocess.run([
        "terminal-notifier",
        "-title", title,
        "-message", message,
        "-activate", "com.apple.Terminal"
    ])


def create_blocking_window(root):
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    root.attributes('-topmost', True)
    root.overrideredirect(True)

    label = tk.Label(root, text="", font=("Helvetica", 48), fg="white", bg="black")
    label.pack(expand=True)

    last_notified = {'time': None}  # mutable holder for last notify time

    def update_countdown(end_time):
        remaining = max(0, int((end_time - datetime.now()).total_seconds()))
        minutes, seconds = divmod(remaining, 60)
        label.config(text=f"Time remaining: {minutes:02d}:{seconds:02d}")

        # Send notification every 30 seconds
        # Only send if last notification was more than 29 seconds ago to avoid spamming in the same second
        if remaining > 0:
            now = datetime.now()
            if (last_notified['time'] is None or (now - last_notified['time']).total_seconds() >= 29):
                send_macos_notification("🧠 Training... ", f"Time remaining: {minutes:02d}:{seconds:02d}")
                last_notified['time'] = now

            root.after(1000, update_countdown, end_time)
        else:
            root.quit()

    end_time = datetime.now() + timedelta(seconds=BLOCK_DURATION)
    update_countdown(end_time)
    print("Fullscreen window created successfully")



def create_event_tap():
    def event_tap_callback(proxy, event_type, event, refcon):
        # Block all events
        return None

    mask = (
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
        Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged) |
        Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown) |
        Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseDown) |
        Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved) |
        Quartz.CGEventMaskBit(Quartz.kCGEventScrollWheel)
    )

    event_tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        0,
        mask,
        event_tap_callback,
        None
    )

    if not event_tap:
        print("Failed to create event tap. Make sure Accessibility permissions are granted.")
        sys.exit(1)

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, event_tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(event_tap, True)
    print("Event tap created for blocking all input")
    return event_tap


def disable_system_shortcuts():
    try:
        subprocess.run([
            "defaults", "write", "com.apple.symbolichotkeys",
            "AppleSymbolicHotKeys", "-dict-add", "52", "{\"enabled\" = 0;}"
        ], check=True)
        subprocess.run(["killall", "Finder"], check=True)
        print("System shortcuts disabled (defaults command)")
    except subprocess.CalledProcessError as e:
        print(f"Error disabling system shortcuts: {e}")


def enable_system_shortcuts():
    try:
        subprocess.run([
            "defaults", "write", "com.apple.symbolichotkeys",
            "AppleSymbolicHotKeys", "-dict-add", "52", "{\"enabled\" = 1;}"
        ], check=True)
        subprocess.run(["killall", "Finder"], check=True)
        print("System shortcuts re-enabled")
    except subprocess.CalledProcessError as e:
        print(f"Error re-enabling system shortcuts: {e}")


def cleanup(root, event_tap):
    try:
        if event_tap:
            Quartz.CGEventTapEnable(event_tap, False)

        root.destroy()
        enable_system_shortcuts()
        print("Cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def run_event_tap_loop():
    Quartz.CFRunLoopRun()


def run_blocker():
    disable_system_shortcuts()
    event_tap = create_event_tap()

    send_macos_notification("⚡ Training Blocker Active", f"Input blocked for {BLOCK_DURATION} seconds.")

    t = threading.Thread(target=run_event_tap_loop, daemon=True)
    t.start()

    root = tk.Tk()
    create_blocking_window(root)
    root.mainloop()

    cleanup(root, event_tap)

    send_macos_notification("🥇Based", "Get back to work now 🎉")


def wait_until_next_hour():
    now = datetime.now()
    next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    wait_seconds = (next_hour - now).total_seconds()
    print(f"Waiting {int(wait_seconds)} seconds until next full hour {next_hour.strftime('%H:%M:%S')}")
    time.sleep(wait_seconds)


def main():
    if os.geteuid() != 0:
        print("This script requires sudo privileges. Run with 'sudo python3 main.py'.")
        sys.exit(1)

    os.environ["TK_SILENCE_DEPRECATION"] = "1"
    print("Ensure Accessibility permissions are granted for Terminal or your IDE in System Settings > Privacy & Security > Accessibility.")

    while True:
        wait_until_next_hour()
        run_blocker()


if __name__ == "__main__":
    main()

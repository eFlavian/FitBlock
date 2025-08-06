import sys
import os
import threading
import time
import json
from datetime import datetime, timedelta
import tkinter as tk
import subprocess
import signal

try:
    import Quartz
    from Foundation import NSObject, NSLog
    from AppKit import (
        NSApplication, NSStatusBar, NSMenu, NSMenuItem,
        NSImage, NSVariableStatusItemLength
    )

    PYOBJC_AVAILABLE = True
except ImportError as e:
    print(f"PyObjC not available: {e}")
    print("Install with: pip install pyobjc-framework-Quartz pyobjc-framework-Cocoa")
    PYOBJC_AVAILABLE = False

BLOCK_DURATION = 120  # seconds
STATE_FILE = os.path.expanduser("~/.fitblock_state.json")

app_state = {
    'start_time': None,
    'sessions_completed': 0,
    'current_session_start': None,
    'paused': False,
    'pause_start_time': None
}


def load_state():
    """Load application state from file."""
    global app_state
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                saved_state = json.load(f)
                app_state.update(saved_state)
                if app_state['start_time']:
                    app_state['start_time'] = datetime.fromisoformat(app_state['start_time'])
                if app_state['current_session_start']:
                    app_state['current_session_start'] = datetime.fromisoformat(app_state['current_session_start'])
                if app_state['pause_start_time']:
                    app_state['pause_start_time'] = datetime.fromisoformat(app_state['pause_start_time'])
                print(
                    f"Loaded state: {app_state['sessions_completed']} sessions completed since {app_state['start_time']}")
        else:
            app_state['start_time'] = datetime.now()
            app_state['sessions_completed'] = 0
            app_state['current_session_start'] = None
            app_state['paused'] = False
            app_state['pause_start_time'] = None
            save_state()
            print("First run - initialized state")
    except Exception as e:
        print(f"Error loading state: {e}")
        app_state['start_time'] = datetime.now()
        app_state['sessions_completed'] = 0
        app_state['current_session_start'] = None
        app_state['paused'] = False
        app_state['pause_start_time'] = None


def save_state():
    """Save application state to file."""
    try:
        state_to_save = app_state.copy()
        if state_to_save['start_time']:
            state_to_save['start_time'] = state_to_save['start_time'].isoformat()
        if state_to_save['current_session_start']:
            state_to_save['current_session_start'] = state_to_save['current_session_start'].isoformat()
        if state_to_save['pause_start_time']:
            state_to_save['pause_start_time'] = state_to_save['pause_start_time'].isoformat()

        with open(STATE_FILE, 'w') as f:
            json.dump(state_to_save, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")


def get_hours_since_start():
    """Calculate total hours since app first started."""
    if app_state['start_time']:
        elapsed = datetime.now() - app_state['start_time']
        return int(elapsed.total_seconds() // 3600)
    return 0


def format_duration_since_start():
    """Format time elapsed since app first started."""
    if not app_state['start_time']:
        return "Unknown"

    elapsed = datetime.now() - app_state['start_time']
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)

    if days > 0:
        return f"{days}d {hours}h ago"
    elif hours > 0:
        return f"{hours}h ago"
    else:
        minutes = remainder // 60
        return f"{minutes}m ago"


def require_root():
    """Check if running as root and request elevation if needed."""
    if os.geteuid() != 0:
        try:
            if getattr(sys, 'frozen', False):
                # Running as bundled app
                app_path = sys.executable
                script = f'''
                do shell script "{app_path}" with administrator privileges
                '''
            else:
                # Running as Python script
                script = f'''
                do shell script "python3 '{os.path.abspath(sys.argv[0])}'" with administrator privileges
                '''

            subprocess.check_call(['osascript', '-e', script])
        except subprocess.CalledProcessError:
            print("User cancelled or failed to authenticate.")
        sys.exit(0)


def send_macos_notification(title, message):
    """Send a macOS notification."""
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            icon_path = os.path.join(base_path, "icon.icns")
        else:
            icon_path = "icon.icns"

        cmd = [
            "terminal-notifier",
            "-title", title,
            "-message", message,
            "-activate", "com.apple.Terminal"
        ]

        if os.path.exists(icon_path):
            cmd.extend(["-appIcon", icon_path])

        subprocess.run(cmd, check=False, capture_output=True)
    except FileNotFoundError:
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=False)
        except Exception as e:
            print(f"Could not send notification: {e}")


def create_blocking_window():
    """Create a fullscreen blocking window with countdown."""
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    root.attributes('-topmost', True)
    root.overrideredirect(True)

    root.focus_force()
    root.grab_set()

    label = tk.Label(root, text="", font=("Helvetica", 48), fg="white", bg="black")
    label.pack(expand=True)

    info_label = tk.Label(root, text="", font=("Helvetica", 16), fg="#888888", bg="black")
    info_label.pack(side='bottom', pady=20)

    last_notified = {'time': None}

    def update_countdown(end_time):
        remaining = max(0, int((end_time - datetime.now()).total_seconds()))
        minutes, seconds = divmod(remaining, 60)
        label.config(text=f"Training Session\nTime remaining: {minutes:02d}:{seconds:02d}")

        session_num = app_state['sessions_completed'] + 1
        started_text = format_duration_since_start()
        total_hours = get_hours_since_start()
        info_text = f"Session #{session_num} • Started {started_text} • {total_hours} total hours"
        info_label.config(text=info_text)

        if remaining > 0:
            now = datetime.now()
            if (last_notified['time'] is None or
                    (now - last_notified['time']).total_seconds() >= 30):
                send_macos_notification("🧠 Training Session",
                                        f"Time remaining: {minutes:02d}:{seconds:02d}")
                last_notified['time'] = now

            root.after(1000, update_countdown, end_time)
        else:
            root.quit()

    end_time = datetime.now() + timedelta(seconds=BLOCK_DURATION)
    update_countdown(end_time)
    print("Fullscreen blocking window created")

    def on_closing():
        pass

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


def create_event_tap():
    """Create a Quartz event tap to block input events."""
    if not PYOBJC_AVAILABLE:
        print("PyObjC not available - input blocking disabled")
        return None

    def event_tap_callback(proxy, event_type, event, refcon):
        return None

    mask = (
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged) |
            Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved) |
            Quartz.CGEventMaskBit(Quartz.kCGEventScrollWheel) |
            Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDragged) |
            Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseDragged)
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
        print("Failed to create event tap.")
        print("Make sure:")
        print("1. App has Accessibility permissions (System Preferences > Security & Privacy > Accessibility)")
        print("2. Running with administrator privileges")
        return None

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, event_tap, 0)
    Quartz.CFRunLoopAddSource(
        Quartz.CFRunLoopGetCurrent(),
        run_loop_source,
        Quartz.kCFRunLoopCommonModes
    )
    Quartz.CGEventTapEnable(event_tap, True)
    print("Event tap created - input blocking active")
    return event_tap


def disable_system_shortcuts():
    """Disable system keyboard shortcuts that could bypass blocking."""
    shortcuts_to_disable = [
        "52",  # Spotlight
        "60",  # Spotlight menu
        "61",  # Spotlight window
        "64",  # Spotlight
        "65",  # Spotlight
        "98",  # Mission Control
        "32",  # Mission Control F3
        "34",  # Application windows F10
        "162",  # Move focus to menu bar
        "163",  # Move focus to dock
    ]

    try:
        for shortcut in shortcuts_to_disable:
            subprocess.run([
                "defaults", "write", "com.apple.symbolichotkeys",
                "AppleSymbolicHotKeys", "-dict-add", shortcut,
                '{"enabled" = 0; "value" = { "parameters" = (); "type" = "standard"; };}'
            ], check=True, capture_output=True)

        subprocess.run(["killall", "SystemUIServer"], check=True, capture_output=True)
        print("System shortcuts disabled")
    except subprocess.CalledProcessError as e:
        print(f"Error disabling system shortcuts: {e}")


def enable_system_shortcuts():
    """Re-enable system keyboard shortcuts."""
    shortcuts_to_enable = [
        "52", "60", "61", "64", "65", "98", "32", "34", "162", "163"
    ]

    try:
        for shortcut in shortcuts_to_enable:
            subprocess.run([
                "defaults", "write", "com.apple.symbolichotkeys",
                "AppleSymbolicHotKeys", "-dict-add", shortcut,
                '{"enabled" = 1; "value" = { "parameters" = (); "type" = "standard"; };}'
            ], check=True, capture_output=True)

        subprocess.run(["killall", "SystemUIServer"], check=True, capture_output=True)
        print("System shortcuts re-enabled")
    except subprocess.CalledProcessError as e:
        print(f"Error re-enabling system shortcuts: {e}")


def cleanup(event_tap):
    """Clean up resources and restore system state."""
    try:
        if event_tap and PYOBJC_AVAILABLE:
            Quartz.CGEventTapEnable(event_tap, False)
            print("Event tap disabled")

        enable_system_shortcuts()
        print("Cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def run_event_tap_loop():
    """Run the Core Foundation run loop for event tapping."""
    if PYOBJC_AVAILABLE:
        Quartz.CFRunLoopRun()


def run_blocker():
    """Main blocking function."""
    if app_state['paused']:
        print("App is paused - not starting blocking session")
        return

    print(f"Starting {BLOCK_DURATION} second blocking session...")

    app_state['current_session_start'] = datetime.now()
    save_state()

    event_tap = None

    def signal_handler(signum, frame):
        print("\nReceived interrupt signal, cleaning up...")
        cleanup(event_tap)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        disable_system_shortcuts()

        event_tap = create_event_tap()

        session_num = app_state['sessions_completed'] + 1
        send_macos_notification("⚡ FitBlock Active",
                                f"Session #{session_num} - {BLOCK_DURATION} seconds")

        if event_tap:
            event_tap_thread = threading.Thread(target=run_event_tap_loop, daemon=True)
            event_tap_thread.start()

        create_blocking_window()

    finally:
        cleanup(event_tap)

        app_state['sessions_completed'] += 1
        app_state['current_session_start'] = None
        save_state()

        print(f"Session completed! Total sessions: {app_state['sessions_completed']}")
        send_macos_notification("🥇 Training Complete",
                                f"Session #{app_state['sessions_completed']} finished! 🎉")


if PYOBJC_AVAILABLE:
    class AppDelegate(NSObject):
        def __init__(self):
            super().__init__()
            self.menu_update_timer = None

        def applicationDidFinishLaunching_(self, notification):
            """Set up the menu bar item."""
            print("Setting up menu bar item...")
            status_bar = NSStatusBar.systemStatusBar()
            self.status_item = status_bar.statusItemWithLength_(NSVariableStatusItemLength)

            icon_loaded = False

            icon_paths = []

            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
                icon_paths.extend([
                    os.path.join(base_path, "icon.icns"),
                    os.path.join(base_path, "..", "Resources", "icon.icns"),
                    os.path.join(base_path, "..", "..", "Resources", "icon.icns"),
                ])
            else:
                icon_paths.append("icon.icns")

            print(f"Looking for icon in paths: {icon_paths}")

            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    print(f"Trying icon path: {icon_path}")
                    icon = NSImage.alloc().initByReferencingFile_(icon_path)
                    if icon and icon.isValid():
                        icon.setSize_((18, 18))  # Resize for menu bar
                        self.status_item.button().setImage_(icon)
                        print(f"✓ Icon loaded successfully from: {icon_path}")
                        icon_loaded = True
                        break
                    else:
                        print(f"✗ Icon file exists but failed to load: {icon_path}")
                else:
                    print(f"✗ Icon file not found: {icon_path}")

            if not icon_loaded:
                self.status_item.button().setTitle_("⏱")
                print("⚠️  Using text icon (⏱) - no valid icon found")

            self.update_menu()

            self.start_menu_update_timer()
            print("Menu bar app initialized successfully")

        def update_menu(self):
            """Update the menu with current stats."""
            menu = NSMenu.alloc().init()

            if app_state['paused']:
                status_text = "Training Session Paused"
            elif app_state['current_session_start']:
                elapsed = datetime.now() - app_state['current_session_start']
                minutes = int(elapsed.total_seconds() // 60)
                seconds = int(elapsed.total_seconds() % 60)
                elapsed_str = f"{minutes}m {seconds:02d}s"
                status_text = f"Training Session Active ({elapsed_str})"
            else:
                status_text = "Training Session Ready"

            status_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                status_text, None, "")
            status_item.setEnabled_(False)
            menu.addItem_(status_item)

            if app_state['start_time']:
                started_text = format_duration_since_start()
                start_info = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    f"First Started: {started_text}", None, "")
                start_info.setEnabled_(False)
                menu.addItem_(start_info)

            sessions_text = f"Sessions completed: {app_state['sessions_completed']}"
            sessions_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                sessions_text, None, "")
            sessions_item.setEnabled_(False)
            menu.addItem_(sessions_item)

            total_hours = get_hours_since_start()
            hours_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Total hours tracked: {total_hours}", None, "")
            hours_item.setEnabled_(False)
            menu.addItem_(hours_item)

            menu.addItem_(NSMenuItem.separatorItem())

            if app_state['paused']:
                pause_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "Resume Training", "resumeTraining:", "")
                pause_item.setTarget_(self)
                menu.addItem_(pause_item)
            else:
                pause_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "Pause Training", "pauseTraining:", "")
                pause_item.setTarget_(self)
                menu.addItem_(pause_item)

            reset_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "Reset Statistics", "resetStats:", "r")
            reset_item.setTarget_(self)
            menu.addItem_(reset_item)

            menu.addItem_(NSMenuItem.separatorItem())

            quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "Quit FitBlock", "quitApp:", "q")
            quit_item.setTarget_(self)
            menu.addItem_(quit_item)

            self.status_item.setMenu_(menu)

        def start_menu_update_timer(self):
            """Start a timer to periodically update the menu."""
            from Foundation import NSTimer
            self.menu_update_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                1.0, self, "updateMenuTimer:", None, True)

        def updateMenuTimer_(self, timer):
            """Timer callback to update menu."""
            self.update_menu()

        def resetStats_(self, sender):
            """Reset application statistics."""
            global app_state
            app_state['start_time'] = datetime.now()
            app_state['sessions_completed'] = 0
            app_state['current_session_start'] = None
            app_state['paused'] = False
            app_state['pause_start_time'] = None
            save_state()
            self.update_menu()
            print("Statistics reset")

        def pauseTraining_(self, sender):
            """Pause the training session."""
            global app_state
            app_state['paused'] = True
            app_state['pause_start_time'] = datetime.now()
            save_state()
            self.update_menu()
            print("Training paused")

        def resumeTraining_(self, sender):
            """Resume the training session."""
            global app_state
            app_state['paused'] = False
            app_state['pause_start_time'] = None
            save_state()
            self.update_menu()
            print("Training resumed")

        def quitApp_(self, sender):
            """Handle quit menu item."""
            if self.menu_update_timer:
                self.menu_update_timer.invalidate()
            NSLog("Quitting FitBlock")
            NSApplication.sharedApplication().terminate_(self)


def run_menu_bar_app():
    """Run the menu bar application."""
    if not PYOBJC_AVAILABLE:
        print("PyObjC not available - menu bar app disabled")
        return

    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


def main():
    """Main entry point."""
    print("FitBlock - macOS Focus Application")
    print(f"Block duration: {BLOCK_DURATION} seconds")
    print(f"PyObjC available: {PYOBJC_AVAILABLE}")

    load_state()

    require_root()

    if PYOBJC_AVAILABLE:
        print("Starting menu bar app...")
        blocker_thread = threading.Thread(target=run_blocker, daemon=True)
        blocker_thread.start()

        run_menu_bar_app()
    else:
        print("Running without menu bar (PyObjC not available)")
        run_blocker()


if __name__ == "__main__":
    main()
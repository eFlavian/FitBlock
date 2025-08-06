# 🏋️‍♂️ FitBlock - The Ultimate Mac Productivity Breaker

> *"Because sometimes you need to be forced to take a fucking piss"* 💪

## What the Hell is This?

FitBlock is a **brutal productivity tool** that completely freezes your Mac at every full hour (12:00, 13:00, 14:00, etc.) for 2 minutes straight. No mouse, no keyboard, no escape - just you and your thoughts (or your push-ups).

Think of it as a digital drill sergeant that forces you to:
- 🚰 **Hydrate** (drink some damn water)
- 💪 **Exercise** (do some push-ups, you weakling)
- 🚽 **Take a piss** (because holding it in is bad for your health)
- 🧘 **Stretch** (your back is probably killing you from sitting all day)
- ☕ **Make coffee** (or tea, we don't judge)

## ⚠️ WARNING: This is NOT for the Faint of Heart

This script will **completely lock down your Mac** for 2 minutes at every full hour. There's no escape key, no force quit, no nothing. You're stuck until the timer runs out. 

**Don't run this if you're in the middle of something important or if you have a meeting in 5 minutes.**

## 🛠️ Installation & Setup

### Fastest way
If you just want to use it fast with no other edits, you can just:
1. Clone/download **FitBlock** repo.
2. Double click on **FitBlock.app**.
3. Insert your MacOS password (needed for admin privileges)
4. Enjoy breaks🎉

### Prerequisites
- macOS (duh, this is a Mac-only tool)
- Python 3.x
- Homebrew (for installing dependencies)
- A sense of humor and the ability to take a joke

### Step 1: Install Dependencies

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install python-tk terminal-notifier

# Install Python packages
pip3 install pyobjc pynput
pip3 install --upgrade pyobjc pyobjc-framework-AppKit pyobjc-framework-Quartz
```

### Step 2: Grant Accessibility Permissions

This is the most important step. Without this, the script won't work:

1. Go to **System Settings** > **Privacy & Security** > **Accessibility**
2. Click the **+** button
3. Add **Terminal.app** (`/Applications/Utilities/Terminal.app`) or your IDE (PyCharm, VS Code, etc.)
4. **Enable** the permission for the app you added
5. Restart Terminal or your IDE after granting permissions

### Step 3: Clone and Run

```bash
# Clone this repository (if you haven't already)
git clone <your-repo-url>
cd fitblock

# Run the script with sudo (required for system-level input blocking)
sudo python3 main.py
```

## 🎯 How It Works

1. **Waits for the next full hour** (e.g., if it's 13:47, it waits until 14:00)
2. **Completely blocks all input** - mouse, keyboard, everything
3. **Shows a fullscreen countdown** with time remaining
4. **Sends notifications** every 30 seconds to remind you what you're supposed to be doing
5. **Releases control** after 2 minutes
6. **Repeats** every hour, 24/7

## 🔧 Customization

Want to change the block duration? Edit line 15 in `main.py`:

```python
BLOCK_DURATION = 120  # Change this to your preferred duration in seconds
```

## 🚨 Troubleshooting

### "Failed to create event tap"
- Make sure you've granted Accessibility permissions
- Restart Terminal/IDE after granting permissions
- Run with `sudo`

### "This script requires sudo privileges"
- Run the script with `sudo python3 main.py`

### Notifications not working
- Make sure `terminal-notifier` is installed: `brew install terminal-notifier`

### Script won't start
- Check that all dependencies are installed
- Ensure Python 3.x is being used
- Verify Accessibility permissions are granted

## 🎭 What to Do During the Block

When your Mac is frozen, here are some productive activities:

- **Push-ups**: Start with 5, work your way up
- **Squats**: Your legs need love too
- **Stretching**: Touch your toes (if you can)
- **Hydration**: Drink a glass of water
- **Bathroom break**: Seriously, just go
- **Deep breathing**: Inhale, exhale, repeat
- **Quick meditation**: Clear your mind for 2 minutes

## 🤔 Why Would Anyone Do This?

Great question! Here's why this might actually be good for you:

- **Forces breaks**: Prevents you from getting sucked into the "just one more thing" trap
- **Improves health**: Regular movement and hydration are good for you
- **Reduces eye strain**: Looking away from the screen every hour
- **Increases productivity**: Short breaks actually make you more productive
- **Builds discipline**: If you can't handle 2 minutes without your computer, you have bigger problems

## ⚡ Pro Tips

- **Start small**: Maybe don't run this during your first week at a new job
- **Warn your colleagues**: "Hey, my computer will be unusable for 2 minutes every hour"
- **Use it as a conversation starter**: "Oh, I'm doing push-ups because my computer is forcing me to"
- **Track your progress**: Count how many push-ups you can do in 2 minutes
- **Make it a game**: Try to beat your previous record

## 🐛 Known Issues

- Works only on macOS (sorry Windows/Linux users)
- Requires sudo privileges (because it's doing system-level stuff)
- May interfere with screen recording software
- Not recommended for shared computers

## 📝 License

This project is open source. Do whatever you want with it, but don't blame us if you get fired for doing push-ups during a meeting.

## 🤝 Contributing

Found a bug? Want to add features? Feel free to contribute! Just remember:
- Keep it funny
- Keep it functional
- Keep it safe

## ⚠️ Disclaimer

This tool is provided "as is" without any warranties. Use at your own risk. The authors are not responsible for:
- Lost productivity
- Embarrassing situations during video calls
- Your boss wondering why you're doing push-ups
- Any other consequences of using this tool

---

**Remember: Life is short, but your health is shorter. Take breaks, stay hydrated, and don't forget to take a piss.** 🚰💪 
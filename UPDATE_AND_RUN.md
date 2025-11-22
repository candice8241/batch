# How to Update and Run the Latest Code

## Step 1: Pull the Latest Code (on your local machine)

Open Git Bash or Command Prompt in your local repository folder and run:

```bash
git fetch origin
git checkout claude/batch-auto-fit-peaks-013fd6g4uGQpfLSWozFSHrjC
git pull origin claude/batch-auto-fit-peaks-013fd6g4uGQpfLSWozFSHrjC
```

## Step 2: Clear Python Cache (optional but recommended)

```bash
# On Windows PowerShell or Command Prompt:
del /s /q __pycache__
del /s /q *.pyc

# Or on Git Bash:
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Step 3: Run the Program

```bash
python half_auto_fitting.py
```

## Verify the Fix

When you run the program, you should see:
- ✅ Console message in **English**: "Icon loaded successfully" (not Chinese)
- ✅ Only **ONE main window** appears
- ✅ **NO extra popup windows** when you click buttons

## What Was Fixed

1. **Duplicate Tk window bug**: Removed the extra `tk.Tk()` that was causing popup windows
2. **Comments**: All converted to English
3. **Index out of bounds error**: Fixed array access issues
4. **Batch pause feature**: Added option to pause and review auto-detection results

## Troubleshooting

If you still see Chinese messages in console:
- You're running an old version of the code
- Make sure you're in the correct branch: `claude/batch-auto-fit-peaks-013fd6g4uGQpfLSWozFSHrjC`
- Check with: `git branch` (should show * next to the branch name)

If the GUI still doesn't appear:
- Make sure you have tkinter installed: `python -m tkinter`
- Check Python version: `python --version` (should be 3.x)

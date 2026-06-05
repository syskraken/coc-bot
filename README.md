============================================================
  COC FARMING BOT — THE KRAKEN
  Automated Clash of Clans Farming Bot
============================================================

REQUIREMENTS
─────────────────────────────────────────────────────────
  - Windows 10 or 11 (64-bit)
  - LDPlayer emulator installed and running
  - Clash of Clans installed inside LDPlayer
  - Internet connection (for first-time setup only)

FIRST TIME SETUP
─────────────────────────────────────────────────────────
  1. Run setup.bat
       - Installs Python, all packages, Tesseract OCR, and ADB
       - Creates run.bat and reconfigure.bat shortcuts
       - Only needs internet on first run

  2. Connect LDPlayer ADB
       Open LDPlayer → Settings → Other settings
       Enable ADB debugging → set port to 5555

  3. Run run.bat
       - First run: answers a few questions (troops, heroes, spells)
       - Then opens a visual planner to pin your troop bar slots
       - Then opens a visual planner to pin where troops deploy
       - Then farms automatically forever

FOLDER STRUCTURE
─────────────────────────────────────────────────────────
  coc-bot/
    app.py                  ← main bot
    deploy_overlay.py       ← visual coordinate planner
    setup.bat               ← installer (run once)
    run.bat                 ← start the bot (created by setup)
    reconfigure.bat         ← change settings (created by setup)
    requirements.txt        ← Python package list
    templates/              ← button/UI image templates
      attack_btn.png
      find_match_btn.png
      attack_confirm_btn.png
      next_btn.png
      return_home_btn.png
      claim_reward_btn.png
      end_battle_btn.png
      okay_btn.png
      close_btn.png
      yes_btn.png
      blacksmith_chest.png
      continue_btn.png
      skip_btn.png
      attack_btn_5star.png
      air_defense/          ← air defense template images
        ad_lv1.png
        ad_lv2.png
        ...

GENERATED FILES (auto-created, do not edit manually)
─────────────────────────────────────────────────────────
  config.json           ← your troop/spell/loot settings
  troop_slots.json      ← pinned troop bar coordinates
  deploy_points.json    ← pinned deploy coordinates
  debug_*.png           ← debug screenshots (safe to delete)

COMMAND LINE OPTIONS
─────────────────────────────────────────────────────────
  python app.py                   normal start
  python app.py --reconfigure     wipe settings, start fresh
  python app.py --setup-only      re-pin coordinates only
  python app.py --farm-only       skip setup, farm immediately

  Or use the .bat shortcuts instead.

CHANGING SETTINGS
─────────────────────────────────────────────────────────
  Run reconfigure.bat to change:
    - Number of troops / heroes / spells
    - Minimum gold threshold
    - Re-pin troop slot positions
    - Re-pin deploy positions

TROUBLESHOOTING
─────────────────────────────────────────────────────────
  Bot cannot find attack button
    → Make sure COC is on the MAIN VILLAGE screen
    → Check templates/ folder has all .png files

  Screenshot fails / ADB error
    → Open LDPlayer → Settings → ADB debugging ON, port 5555
    → Run: adb connect 127.0.0.1:5555  in a command prompt

  Gold OCR reads wrong values
    → Check debug_gold_roi.png to see what the bot sees
    → Adjust MIN_GOLD in config.json if needed

  Air defenses not detected
    → Add cleaner template images to templates/air_defense/
    → Lower AIR_DEF_THRESHOLD in app.py (try 0.65)

  Tesseract not found error
    → Reinstall Tesseract to: C:\Program Files\Tesseract-OCR\
    → Do NOT change the install path

============================================================
  Created by THE KRAKEN
============================================================
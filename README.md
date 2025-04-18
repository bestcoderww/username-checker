# username availability checker

check usernames across the most popular platforms:

twitter (via socialscan)

instagram (via socialscan)

reddit (via socialscan)

github (custom check)

youtube (custom check)

telegram (custom check)

snapchat (custom check)

⚠️ note: this tool detects if a profile is publicly visible.
suspended or banned usernames may appear as "available" but are not claimable.

—

## how to run

you’ll need python 3+ installed

1. clone the repo in your terminal or command prompt
```bash
git clone https://github.com/icocz/username-checker.git
cd username-checker
```
2. install dependencies
```bash
pip install socialscan requests
```
3. run the script
```bash
python app.py
```

you’ll be prompted to enter usernames (comma-separated), and it’ll check them across all supported platforms.

—

example output

— ico

  Twitter: Taken
  
  Instagram: Available
  
  Reddit: Taken
  
  Github: Available
  
  Youtube: Available

  Telegram: Invalid

  Snapchat: Taken

—

license

MIT License

—

credits

made by ico

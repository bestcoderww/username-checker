[OUTDATED] # username availability checker

check usernames across the most popular platforms:

twitter

instagram

reddit

github

youtube

telegram

snapchat


⚠️ note: this tool detects if a profile is publicly visible.
many inaccuracies occur, this was built in 5 minutes and is not to be trusted for serious or large scale use. 

—

## how to run

you’ll need python 3+ installed

1. clone the repo in your terminal or command prompt
```bash
git clone https://github.com/bestcoderww/username-checker.git
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

— ben

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

made by ben

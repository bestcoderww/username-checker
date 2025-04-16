# username availability checker

check usernames across the most popular platforms:

twitter (via socialscan)

instagram (via socialscan)

reddit (via socialscan)

github (custom check)

youtube (custom check)

to be added: telegram, discord, snapchat

⚠️ note: this tool detects if a profile is publicly visible.
suspended or banned usernames may appear as "available" but are not claimable.

—

## how to run

you’ll need python 3+ installed

### install requirements
```bash 
pip install socialscan requests
```

### run the script
```bash
python username_checker.py
```

you’ll be prompted to enter usernames (comma-separated), and it’ll check them across all supported platforms.

—

example output

— icozc

  Twitter: Taken
  
  Instagram: Available
  
  Reddit: Taken
  
  Github: Available
  
  Youtube: Available

—

license

MIT License

—

credits

made by ico

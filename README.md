# Supertrend-Discord
Send supertrend alerts to Discord webhook

# How To Use?
```
git clone https://github.com/spuqe/Supertrend-Discord/
cd Supertrend-Discord
sudo apt install python3-pip
pip install -r requirements.txt
python3 supertrend.py
```

# How to run 24/7 on linux
* Log in with ssh,
* Launch screen by running command screen
* Start program: python3 supertrend.py
* Detach from screen using key combination C-A(Ctrl+A) + D, (what's in your screen session will keep running)
* Log out from ssh
* To check again your program execution:

* Log in with ssh (with the same user as before)
* Re-attach to an existing screen session using $ screen -r

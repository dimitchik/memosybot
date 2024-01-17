# Check if the screen session exists
if screen -list | grep -q "botrunner"; then
    # Kill the screen session
    screen -X -S botrunner quit
fi
screen -dmS botrunner python3 memosybot.py
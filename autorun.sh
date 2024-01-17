# Check if the screen session exists
if screen -list | grep -q "botupdater"; then
    # Kill the screen session
    screen -X -S botupdater quit
fi
screen -dmS botupdater ./autoupdate.sh
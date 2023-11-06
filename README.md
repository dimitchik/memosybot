# Memosy Bot

Telegram bot that detects links to (some) websites to extract videos and send them directly.
- When used in a private chat, it just responds with a video message.
- When added to a group chat, it detects links to supported websites, deletes the original message (if it has the required permission, of course), and posts a video message with the name of the sender, original link, and any extra text that was in that message

## Why?

Link preview in Telegram ususally sucks for videos, and opening a separate website/app for a meme you friends sent to you is frustrating, especially on a mobile device

## Currently supported websites

- [9gag](https://9gag.com)
- [coub](https://coub.com)
- [youtube](https://youtube.com)
  - Duration limit is 5 minutes, if the video is longer, it will be cut
  - Timestamps are respected
  - Shorts are supported (bot assumes they're vertical)
  - There is some support for clips, but they are very inconsistent
- [reddit](https://reddit.com)
- [tiktok](https://tiktok.com)


## Dependencies

### Python 3

https://www.python.org

### FFmpeg

https://ffmpeg.org

Installation depends on the system, in the end you need to make sure that `ffmpeg` console command is available

### MediaInfo

Instructions are available [here](https://pymediainfo.readthedocs.io/en/stable/), but they weren't enough for me on MacOS
You can download a library file (dll, dylib, etc... depending on the platform) from https://mediaarea.net/en/MediaInfo/Download and put it in the project's root folder


### Python packages

Python packages are listed in `requirements.txt`, to autoatically install them run `pip install -r requirements.txt`


## Usage

To just run the bot, run `python memosybot.py`

First run will ask you for the bot token and debug chat id,
 - Here's how to get the bot token: [https://core.telegram.org/bots/tutorial#obtain-your-bot-token]
 - Debug chat id is id of the chat to send errors to, you can enter your telegram username, or just leave this blank
   
On Unix systems, you can run `autorun.sh` to run the bot in the background. Don't forget to `chmod +x autorun.sh`!

# 🕸️ Telegram scrapper

Simple package (+ CLI) for scrapping Telegram channel

# Features

✔️ auto explore new channels  
✔️ search text  
✔️ search mentions  

# Usage

```console
$ pip install telespider
$ tspider search -w "stonks" -n 100 # search word `stonks`
$ tspider search -u "andrewsap" -n 100 # search mentions of user `andrewsap`
```

# Configuration

App uses this environment variables:
- `API_HASH` and `API_ID` - required by `Pyrogram` (more about that [here](https://docs.pyrogram.org/start/auth))
- `ENTRYPOINT_CHANNELS` - comma separated list of channels to begin search in
- `MAX_PER_CHANNEL` - max number of messages to parse from one channel (can be set with `-n` option from CLI)
- `AUTO_EXPLORE_CHANNELS` - automatically explore new channels and add them to queue for parsing (can be set with `--explore\--no-explore` options in CLI)
- `SILENT` - suppress all output

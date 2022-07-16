run:
	while true; do ./sample-bot.py --test prod-like; sleep 1; done

prod: 
	while true; do ./sample-bot.py --production; sleep 1; done
runmain: 
	while true; do ./main.py --test prod-like; sleep 1; done

run:
	while true; do ./sample-bot.py --test prod-like; sleep 1; done

prod: 
	while true; do ./main.py --production; sleep 1; done
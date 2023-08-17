# 宣告使用 /bin/bash
#!/bin/bash

python3 main.py -p unsw.pickle -d 5 -t 10 -n 10 -f EC -S Entry
python3 main.py -p unsw.pickle -d 10 -t 10 -n 10 -f EC -S Entry
python3 main.py -p unsw.pickle -d 15 -t 10 -n 10 -f EC -S Entry
python3 main.py -p unsw.pickle -d 20 -t 10 -n 10 -f EC -S Entry
python3 main.py -p unsw.pickle -d 25 -t 3 -n 10 -f EC -S Entry
python3 main.py -p unsw.pickle -d 30 -t 3 -n 10 -f EC -S Entry


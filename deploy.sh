#!/bin/bash

cp rs_quests.py venv/lib/python3.6/site-packages/
cd venv/lib/python3.6/site-packages/
zip -r ~/Desktop/skill.zip *
rm rs_quests.py

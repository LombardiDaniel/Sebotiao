#!/bin/bash
cd src

python3 main.py |& tee -a ./logs/container.log

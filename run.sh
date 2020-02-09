#!/bin/bash

work_dir=`dirname $0`
cd $work_dir
. venv/bin/activate
python update.py

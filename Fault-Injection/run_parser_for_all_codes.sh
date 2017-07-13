#!/bin/bash

for i in clamr dgemm hotspot lavamd lud nw
do
	./faultinj_parser.py codes/$i csv_files/$i
done


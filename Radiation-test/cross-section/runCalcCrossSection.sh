#!/bin/bash

# LANSCE Dec 2016 test, distance data
#Device; Distance cm; Distance Factors -> (20^2)/((x+20)^2) x is the distance in meters
#Xeon Phi;	156 cm;	0.8605229915
rm -f summaries.csv
./calcCrossSection.py lansce_neutron.log logs_parsed_carolxeon2-mic0.csv 0.8605229915 

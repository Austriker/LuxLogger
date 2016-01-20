#!/usr/bin/env python
from tsl2561_2 import TSL2561 

if __name__ == "__main__": 
	tsl = TSL2561(debug=1) 
	print tsl.lux() 
fg {ff}
ff {
	writeLine('serverLog','Hello-- from irods rule language')
	fail  (-2);
	#failmsg (-2, "my message DWM" );
	#fail
}
INPUT  null
OUTPUT ruleExecOut

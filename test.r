fg {ff}
ff {
	writeLine('serverLog','Hello-- from irods rule language')
	#fail # (-2);
	failmsg (-2, "my message DWM" );
}
INPUT  null
OUTPUT ruleExecOut

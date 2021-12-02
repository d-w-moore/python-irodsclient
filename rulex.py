from irods.rule import Rule
from irods.test.helpers import make_session
ses = make_session()
rule = Rule( ses, rule_file = 'testfile.r', instance_name = 'irods_rule_engine_plugin-python-instance')
output  = rule.execute()
buf = output.MsParam_PI[0].inOutStruct.stdoutBuf.buf
print ('output =',buf)

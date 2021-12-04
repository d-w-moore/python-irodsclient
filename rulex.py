from irods.rule import Rule
from irods.test.helpers import make_session
ses = make_session()
rule = Rule( ses, body='defined_in_both',
        instance_name = 'irods_rule_engine_plugin-python-instance',
        output = 'ruleExecOut')
output  = rule.execute()
buf = output.MsParam_PI[0].inOutStruct.stdoutBuf.buf
print ('output =',buf)

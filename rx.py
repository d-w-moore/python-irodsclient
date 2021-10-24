from irods.rule import Rule
from irods.message import RErrorStack

from irods.exception import (FAIL_ACTION_ENCOUNTERED_ERR)

from irods.test.helpers import make_session

ses = make_session()
rule = Rule( ses, rule_file = 'test.r',
                  instance_name = 'irods_rule_engine_plugin-irods_rule_language-instance' )
r = RErrorStack()
rule.execute(r_error_stack = r, acceptable_errors = (-1, FAIL_ACTION_ENCOUNTERED_ERR))
print (r)
pass

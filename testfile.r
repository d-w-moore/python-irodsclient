def main(rule_args, callback, rei):
    callback.writeLine('serverLog','hello to server log - from python rule')
    callback.writeLine('stdout','hello to stdout - from python rule')

INPUT null
OUTPUT ruleExecOut

from configobj import ConfigObj,flatten_errors
from validate import Validator
import os

configspec={}
configspec['popolarenetworkd']={}

configspec['popolarenetworkd']['logfile']  = "string(default='popolarenetworkd.log')"
configspec['popolarenetworkd']['errfile']  = "string(default='popolarenetworkd.err')"
configspec['popolarenetworkd']['lockfile'] = "string(default='popolarenetworkd.lock')"
configspec['popolarenetworkd']['timestampfile'] = "string(default='popolarenetworkd.timestamp')"
configspec['popolarenetworkd']['jsonrpcfile'] = "string(default='popolarenetworkd.jsonrpc')"
configspec['popolarenetworkd']['user']     = "string(default=None)"
configspec['popolarenetworkd']['group']    = "string_list(default=None)"

configspec['popolarenetworkd']['rootpath']    = "string(default='.')"
configspec['popolarenetworkd']['prefix']    = "string(default='notiziario_')"
configspec['popolarenetworkd']['postfix']    = "string(default='.oga')"
configspec['popolarenetworkd']['maxlen']    = "integer(default=30)"


config    = ConfigObj ('/etc/popolarenetwork/popolarenetwork-site.cfg',file_error=False,configspec=configspec)

usrconfig = ConfigObj (os.path.expanduser('~/.popolarenetwork.cfg'),file_error=False)
config.merge(usrconfig)
usrconfig = ConfigObj ('popolarenetwork.cfg',file_error=False)
config.merge(usrconfig)

val = Validator()
test = config.validate(val,preserve_errors=True)
for entry in flatten_errors(config, test):
    # each entry is a tuple
    section_list, key, error = entry
    if key is not None:
       section_list.append(key)
    else:
        section_list.append('[missing section]')
    section_string = ', '.join(section_list)
    if error == False:
        error = 'Missing value or section.'
    print(section_string, ' = ', error)
    raise error


# section popolarenetworkd
logfilepopolarenetworkd              = config['popolarenetworkd']['logfile']
errfilepopolarenetworkd              = config['popolarenetworkd']['errfile']
lockfilepopolarenetworkd             = config['popolarenetworkd']['lockfile']
timestampfilepopolarenetworkd        = config['popolarenetworkd']['timestampfile']
jsonrpcfilepopolarenetworkd          = config['popolarenetworkd']['jsonrpcfile']
userpopolarenetworkd                 = config['popolarenetworkd']['user']
grouppopolarenetworkd                = config['popolarenetworkd']['group']

rootpathpopolarenetworkd             = config['popolarenetworkd']['rootpath']
prefixpathpopolarenetworkd           = config['popolarenetworkd']['prefix']
postfixpopolarenetworkd              = config['popolarenetworkd']['postfix']
maxlenpopolarenetworkd               = config['popolarenetworkd']['maxlen']

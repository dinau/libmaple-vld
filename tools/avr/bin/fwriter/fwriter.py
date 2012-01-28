# 
# Copyright (C) 2011, audin.
# 2011/11 : Modified by audin. Added verify option. 
# 2011/09 : Written by audin.
#
# This file is under the MIT License.
#

import  re, _winreg, sys
import subprocess, os, types


###
# Options
###
fList_file              = False        # If you need list file as debug info, set to True.
fPut_hex_to_temp_folder = False        # If you'd like to put hex file to temporary folder, set to True.
fVerify                 = False        # If you'd like to verify with hex file, set to True.

###
# Global value
###
base_key      = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
uninst_key    = os.path.join( base_key, 'InstallShield Uninstall Information' )
inst_key      = os.path.join( base_key, 'InstallShield_' )
st_link_str   = 'ST-LINK'

tchain_path   = os.path.join( 'hardware', 'tools', 'arm', 'bin' )
tchain        = 'arm-none-eabi-'
objcopy       = os.path.join( tchain_path, tchain + 'objcopy'   )
objdump       = os.path.join( tchain_path, tchain + 'objdump'   )
nm            = os.path.join( tchain_path, tchain + 'nm'        )
temp_hex      = 'tmp.hex'
verify        =''

###
# Thank you, Mr.fgshun.
# http://d.hatena.ne.jp/fgshun/20090110/1231557171
#
###
# enum_keys
###
def enum_keys( key ):
    try:
        i = 0
        while True:
            yield _winreg.EnumKey( key, i)
            i += 1
    except EnvironmentError:
        pass

###
# enum_values
###
def enum_values( key ):
    try:
        i = 0
        while True:
            yield _winreg.EnumValue( key, i)
            i += 1
    except EnvironmentError:
        pass

###
# get_st_link_utils_GUID
###
# This function has been checked on only Windows XP.

def get_st_link_utils_GUID():
    key_base = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE, uninst_key )
    r        = re.compile( st_link_str )
    _end     = False
    foundkey = None
    for subkey in enum_keys( key_base):
        key = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE, os.path.join( base_key, subkey ) )
        for lst in enum_values( key ):
            for v in lst:
                if ( type( v ) == types.StringType ) or ( type(v) == types.UnicodeType ):
                    if r.search( v ): # if include string 'ST-LINK' 
                        foundkey = subkey
                        _end = True
                        break
            if _end:
                break
        if _end:
            break
        _winreg.CloseKey( key )
    _winreg.CloseKey( key_base )
    return foundkey

###
# get_st_link_utils_dir
###
def get_st_link_utils_dir():
    guid = get_st_link_utils_GUID()
    if guid == None:
        print '#-#-# ERROR: ST-LINK Utility is not installed !'
        return
    _dir = None
    key_base = _winreg.OpenKey( _winreg.HKEY_LOCAL_MACHINE, inst_key + guid )
    for v in enum_values(key_base):
        if v[0] == 'InstallLocation':
            _dir = v[1]
            break
    if not os.path.exists( _dir ):
        print '#-#-# ERROR: ST-LINK Utility folder is not found !'
    return _dir

###
# Execute command
###
def exe_cmd( ary, disp=1 ):
    path = os.path.join( ary[1], ary[0] )
    cmd = ' '.join( ( '\"'+ path + '\"', ary[2] ) )
    if disp == 1:
        print 'Executing:\n%s\n' % cmd
        sys.stdout.flush()
    return subprocess.call( cmd, shell = True)

###
# Help
###
def help():
    print '\n Flash writer management utility'
    print '\n 2011, created by audin.'

###
# Start main
###
if fVerify:
    verify = "-V"
st_link_cmd_path = os.path.join( get_st_link_utils_dir(), 'ST-LINK Utility' )

args = sys.argv
argc = len(args)

if argc==1:
    help()
    sys.exit(0)

###
# Print args list
###
for i in range( argc ):
    print '%02d|%s|' % ( i, args[ i ] )
sys.stdout.flush()

###
# Get file names
###
last_arg  = args[ argc - 1 ]                        # including full path name
hex_name  = last_arg[10:-2]                         # get hex name, full path
base_name = hex_name[0:-4]
elf_name  = base_name + '.elf'                      # get elf name, full path
lst_name  = base_name + '.lst'
build_dir = os.path.dirname( elf_name )             # get build dir,full path
if fPut_hex_to_temp_folder:
    temp_hex = os.path.join( build_dir, temp_hex )  # get temp name ,full path

###
# Writer table
###
#              cmd        :[ exe          ,path              ,arg                                         ,disp ]
writer_tbl = { '-cdfuw'   :[ 'dfuw'       ,''                ,'%s' % temp_hex                             , 1],
               '-cst-link':[ 'ST-LINK_CLI', st_link_cmd_path ,'-c SWD -P %s %s -Rst' % (temp_hex, verify) , 1]
             }
###
# Command table
###
#              cmd        :[ exe    ,path ,arg                                             ,disp ]
cmd_tbl =    { 'make_hex' :[ objcopy, ''  , '-O ihex %s %s'        % (elf_name, temp_hex)  , 0]
              ,'make_lst' :[ objdump, ''  , '-afph -tr %s -d > %s' % (elf_name, lst_name)  , 0]  
             }


###
# Create hex file
###
if os.path.exists( temp_hex ): # First, delete tmp.hex.
    os.remove( temp_hex )
exe_cmd( cmd_tbl['make_hex'], 0 )
if fList_file:
    exe_cmd( cmd_tbl['make_lst'], 0 )

###
# Decide write command and execute
###
err = True
res = 100
for i in range( argc ):
    arg = args[i].lower()       # To compare with lowercase.
    if arg in writer_tbl:
        res = exe_cmd( writer_tbl[ arg ] )
        err = False
        break
if res != 0:
    print '#-#-# ERROR: Write command execution failed ! '
if err:
    print '#-#-# ERROR: Could not decide any writer command !'










#########################################################################

# The MIT License
# 
# Copyright (c) 2011  audin.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 


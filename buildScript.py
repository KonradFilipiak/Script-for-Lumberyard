
import sys
import os
import socket
import subprocess
import datetime

time_now = datetime.datetime.now()

pc_ip = socket.gethostbyname(socket.gethostname())	# IP of the gaming PC

# Script arguments
active_console = 'orbis'							# Console to build
build_config = 'profile'							# Build's config (profile/debug/release)
consoles_ip = '10.228.25.0'							# Console(s) IP(s)
project = 'SamplesProject'							# Project to build
use_uber_files = 'False'							# Whether using uber files or not
use_vfs = '0'										# Whether using VFS or not

dev_path = '..\dev\\'
template_files_path = 'FileTemplates\\'				

#######################################################################################################

def check_arguments(args):
	'''
	Returns True if the arguments are correct and False if they are not
	'''
	global active_console
	global build_config
	global consoles_ip
	global project
	global use_uber_files
	global use_vfs

	args_correct = True
	args_length = len(args)

	# Number of arguments
	if args_length > 6:
		print 'ERROR: To many arguments.'
		args_correct = False
	elif args_length < 1:
		print 'ERROR: Min 1 argument required.'
		args_correct = False

	# 1st argument: Active console
	if args_length > 0:
		args[0] = args[0].lower()

	if args_length == 0 or args[0] == '0':			# Active console is not supposed to change
		pass
	elif args[0] == 'orbis' or args[0] == 'durango':
		active_console = args[0]
	else:
		print 'ERROR: 1st argument: Wrong active console. Expected \"Orbis\" or \"Durango\".'
		args_correct = False

	# 2nd argument: Build config (profile/debug/release)
	if args_length > 1:
		args[1] = args[1].lower()

	if args_length < 2 or args[1] == '0':			# Build config is not supposed to change
		pass
	elif args[1] == 'profile' or args[1] == 'debug' or args[1] == 'release':
		build_config = args[1]
	else:
		print 'ERROR: 2nd argument: Wrong build config. Expected \"profile\", \"debug\" or \"release\".'
		args_correct = False

	# 3rd argument: Project to build
	if args_length > 2:
		args[2] = args[2].lower()

	if args_length < 3 or args[2] == '0':			# Project to build is not supposed to change
		with open(dev_path + 'bootstrap.cfg', 'r') as file:
			expected_string = 'sys_game_folder='

			for line in file:
				if expected_string in line:
					project = line[16:]
					break
	elif args[2] == 'samplesproject' or args[2] == 'sampleproject' or args[2] == 'samplesprojekt' \
					or args[2] == 'sampleprojekt':	# SamplesProject
		project = "SamplesProject"
	elif args[2] == 'featuretests' or args[2] == 'featurestests' or args[2] == 'featuretest' \
					or args[2] == 'featurestest':	# FeatureTests
		project = 'FeatureTests'
	elif args[2] == 'multiplayerproject' or args[2] == 'multiplayerprojects' or args[2] == 'multiplayerprojekt' \
					or args[2] == 'multiplayerprojekts' or args[2] == 'multiproject' or args[2] == 'multiprojects':
		project = 'MultiplayerProject'				# MultiplayerProject
	elif args[2] == 'multiplayersample' or args[2] == 'multiplayersamples' or args[2] == 'multisample' \
					or args[2] == 'multisamples':	# MultiplayerSample
		project = 'MultiplayerSample'				
	else:											# Wrong project name
		print 'ERROR: 3rd argument: Wrong project name. Expected \"SamplesProject\", \"FeatureTests\", ' + \
				'\"MultiplayerProject\" or \"MultiplayerSample\".' 
		args_correct = False

	# 4th argument: Console(s) IP(s)
	if args_length < 4 or args[3] == '0':			# Console(s) IP(s) is not supposed to change
		ip_needs_change = True

		with open(dev_path + 'bootstrap.cfg', 'r') as file:
			expected_string = 'white_list='

			for line in file:
				if expected_string in line:
					consoles_ip = line[13:]
					ip_needs_change = False
					break

			if ip_needs_change:						# Console(s) IP(s) needs to change for build to work
				print 'ERROR: 4th argument: Console(s) IP(s) has not been given and it has not been' + \
				 ' found in boostrap.cfg file. Expected to find: \"white_list = xx.xxx.xx.x\"'
				args_correct = False
	else:											# Console(s) IP(s) is correct
		consoles_ip = args[3]

	# 5th argument: Whether using uber files or not
	if args_length > 4:
		args[4] = args[4].lower()

	if args_length < 5 or args[4] == '0':			# "Whether using uber files or not" is not supposed to change
		try:
			with open(dev_path + '_WAF_\user_settings.options', 'r') as file:
				expected_string = 'use_uber_files = '

				for line in file:
					if expected_string in line:
						use_uber_files = line[17:]
						break
		except IOError:								# The "user_settings.options" does not exist yet (happens before 1st configuration)
			print 'WARNING: 3rd argument: The \"user_settings.options\" file does not exist yet.' + \
					' Default value of \"False\" will be assigned.'
	elif args[4] == 'false' or args[4] == '-1':		# use_uber_files = false
		use_uber_files = 'False'
	elif args[4] == 'true' or args[4] == '1':		# use_uber_files = true
		use_uber_files = 'True'
	else:											# Wrong "use_uber_files" argument
		print 'ERROR: 5th argument: Wrong argument. Accepted values are: True, 1, False and -1.'
		args_correct = False

	# 6th argument: Whether using VFS or not
	if args_length > 5:
		args[5] = args[5].lower()

	if args_length < 6 or args[5] == '0':			# Project to build is not supposed to change
		with open(dev_path + 'bootstrap.cfg', 'r') as file:
			expected_string = 'remote_filesystem='

			for line in file:
				if expected_string in line:
					use_vfs = line[18:]
					break
	elif args[5] == 'false' or args[5] == '-1':		# use_vfs = false
		use_vfs = '0'
	elif args[5] == 'true' or args[5] == '1':		# use_vfs = true
		use_vfs = '1'
	else:											# Wrong "use_vfs" argument
		print 'ERROR: 6th argument: Wrong argument. Accepted values are: True, 1, False and -1.'
		args_correct = False

	return args_correct

#######################################################################################################

def complete_SetupAssistant_files():
	filedata = None

	with open(template_files_path + 'template_SetupAssistantConfig.json', 'r') as file:
		filedata = file.read()

	with open(dev_path + 'SetupAssistantConfig.json', 'w') as file:
		file.write(filedata)
		
#######################################################################################################

def complete_boostrap():
	filedata = None

	with open(template_files_path + 'template_bootstrap.cfg', 'r') as file:
		filedata = file.read()

	filedata = filedata.replace('-- remote_ip=127.0.0.1', 'remote_ip=' + pc_ip)
	filedata = filedata.replace('sys_game_folder=SamplesProject', 'sys_game_folder=' + project)
	filedata = filedata.replace('remote_filesystem=0', 'remote_filesystem=' + use_vfs)

	filedata += ('\nwhite_list=' + consoles_ip)

	with open(dev_path + 'bootstrap.cfg', 'w') as file:
		file.write(filedata)

#######################################################################################################

def complete_user_settings_file():
	filedata = None

	with open(template_files_path + 'template_user_settings.options', 'r') as file:
		filedata = file.read()

	filedata = filedata.replace('use_uber_files = False', 'use_uber_files = ' + use_uber_files)

	with open(dev_path + '_WAF_\user_settings.options', 'w') as file:
		file.write(filedata)

#######################################################################################################

def complete_system_file(file_name):
	'''
	INPUT: file_name: Name of the system file to change : string
	'''
	filedata = None

	with open(template_files_path + 'template_' + file_name, 'r') as file:
		filedata = file.read()

	filedata = filedata.replace('r_ShaderCompilerServer=127.0.0.1', 'r_ShaderCompilerServer = ' + pc_ip)
	filedata += ('\nlog_RemoteConsoleAllowedAddresses = ' + pc_ip)

	with open(dev_path + file_name, 'w') as file:
		file.write(filedata)

#######################################################################################################

def run_program(path, program_name, script_name = 'run_program'):
	'''
	INPUT: path: path from the script to the file to run : string
		   program_name: full name of the program to run (with extenstion) : string
		   script_name: name of the script (.bat) which will run the program (name without extenstion) : string
	'''

	filedata = 'cd ' + path + '\n'
	filedata += 'start ' + program_name

	with open(path + script_name + '.bat', 'w') as file:
		file.write(filedata)

	subprocess.call(path + script_name + '.bat', shell = False)

#######################################################################################################

def current_time():
	'''
	Returns current time in format mm.dd-hh:mm
	'''
	month = time_now.month
	if month < 10:
		month = '0' + str(month)
	day = time_now.day
	if day < 10:
		day = '0' + str(day)
	hour = time_now.hour
	if hour < 10:
		hour = '0' + str(hour)
	minute = time_now.minute
	if minute < 10:
		minute = '0' + str(minute)

	return '%s.%s-%s.%s' % (str(month), str(day), str(hour), str(minute))

#######################################################################################################
def script(args):
	'''
	INPUT: Array of min 1 and max 6 arguments.
		   Not giving an argument (or giving it a value of 0) means that it is not supposed to change
		  	1) Console to build : string (durango/orbis)
		  	2) profile/debug/release : string
		  	3) Project to build : string (SamplesProject, FeatureTests, MultiplayerProject, MultiplayerSample)
			4) Console(s) IP(s) : string (in IP format e.g. 10.228.25.100)
			5) Whether using uber files or not : string (true, false, 1, 0)
			6) Whether using VFS or not : string (true, false, 1, 0)
	'''
	global active_console
	global build_config

	if not check_arguments(args):
		sys.exit()

	complete_SetupAssistant_files()
	complete_boostrap()
	complete_user_settings_file()

	complete_system_file('system_ps4_pc.cfg')
	complete_system_file('system_xbone_pc.cfg')

	output_folder = current_time()
	os.system('mkdir %s' % output_folder)

	os.system('%slmbr_waf configure > %s\configure' % (dev_path, output_folder))

	if not os.path.isfile('%sBin64vc140.Debug\EditorPlugins\AssetTagging.pdb' % dev_path):		# If PC profile is not builded
		os.system('%slmbr_waf build_win_x64_vs2015_profile -p all > %s\win_x64_profile -p all' % (dev_path, output_folder))

	os.system('%slmbr_waf build_%s_%s -p game_and_engine > %s\%s_%s -p game_and_engine' % \
				(dev_path, active_console, build_config, output_folder, active_console, build_config))

	run_program("%sTools\CrySCompileServer\\x64\profile\\" % dev_path, "CrySCompileServer_vc140x64.exe", "run_SC")
	run_program("%sBin64vc140\\" % dev_path, "AssetProcessor.exe", "run_AP")

#######################################################################################################

if __name__ == "__main__":
	script(sys.argv[1:])
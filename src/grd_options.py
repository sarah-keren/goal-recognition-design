'''
Created on May 18, 2014

@author: sarahn
'''
import getopt, os, sys,grd_defs

def usage() :
	print ("Parameters:",file =  sys.stderr)
	print ( "-e  --experiment <file or folder>  Plan Recognition experiment files (tar'ed)",file =  sys.stderr)
	print ( "-d  --destination folder (the subfolder of pgrd_defs.gen_files where the files are generated)",file = sys.stderr )
	print ( "-c  --calculation method    the method to be applied",file =  sys.stderr)
	print ( "-v  --combinations examined - either max over all pairs or the wcd of each pair",file =  sys.stderr)
	print ( "-h  --help                       Get Help",file =  sys.stderr)
	print ( "-t  --max-time <time>            Maximum allowed execution time (defaults to 1800 secs)",file =  sys.stderr)
	print ( "-m  --max-memory <time>          Maximum allowed memory consumption (defaults to 1Gb)",file =  sys.stderr)
	print ( "-x  --done-file-name          task names that need not be calculated",file =  sys.stderr)
	print ( "-o  --domain-file-name         grd domain file name(when specifing files instead of folder)",file =  sys.stderr)
	print ( "-p  --temPlate-file-name        grd template file name(when specifing files instead of folder)",file =  sys.stderr)
	print ( "-y  --hyps-file-name        grd hyps file name(when specifing files instead of folder)",file =  sys.stderr)
	print ( "-b  --obs-file-name        grd non-observable actions file name(when specifing files instead of folder)",file =  sys.stderr)
	print ( "-a  --action-tokens-file-name      grd action token file name(when specifing files instead of folder)",file =  sys.stderr)
	print ( "-u  --sub-optimal-bound-array",file =  sys.stderr)
	print ( "-f  --delete-log-folders  should the log folders be deleted",file =  sys.stderr)
	print ( "-r  --rec-obs-file-name     reciproce-observability actions file name(when specifing files instead of folder)",file =  sys.stderr)
	print ( "-g  --design-budget-array",file =  sys.stderr)
	print ( "-k  --token-file-string",file =  sys.stderr)
	print ( "-i  --actions-to-remove",file =  sys.stderr)
	print ( "-z  --actions-constraints",file =  sys.stderr)
	print ( "-n  --domain",file =  sys.stderr)

class Program_Options :

	def __init__( self, args ) :
		try:
			opts, args = getopt.getopt(	args,
							"e:d:c:v:h:t:m:x:o:p:y:b:a:u:f:r:g:k:i:z:n",
							["experiment=",
						     "destination-folder"
							"calc-methods",
							"combinations-examined",
							"help",
							"max-time=",
							"max-memory=",
							"done-file=",
							"domain-file=",
							"template-file=",
							"hyps-file=",
							"non-obs-file=",
							"action-tokens-file=",
							"sub-optimal-bound-array=",
							"delete-log-folders ",
							"rec-obs-file-name",
							"design-budget-array",
							"token-file-string",
							"actions-to-remove",
							"actions-constraints",
							"domain",
							] )
		except getopt.GetoptError :
			print("Missing or incorrect parameters specified!",file =  sys.stderr)
			usage()
			sys.exit(1)

		self.exp_file = grd_defs.NA
		self.destination_folder = grd_defs.NA
		self.calc_methods = []
		self.domain_name = grd_defs.NA
		self.instance_names = []
		self.max_time = grd_defs.NA
		self.max_memory = grd_defs.NA
		self.optimal = False
		self.comb_examined = grd_defs.comb_max
		self.done_file_path = grd_defs.NA
		self.domain_file_name = grd_defs.NA
		self.template_file_name = grd_defs.NA
		self.hyps_file_name = grd_defs.NA
		self.observability_file_name = grd_defs.NA
		self.reciproceobservability_file_name = grd_defs.NA
		self.action_tokens_file_name = grd_defs.NA
		self.sub_optimal_bound_array = grd_defs.NA
		self.delete_log_folders = True
		self.design_budget_array_string = grd_defs.NA
		self.action_tokens_file_name = grd_defs.NA
		self.actions_to_remove = grd_defs.NA
		self.action_constraints = False


		for opcode, oparg in opts :
			print(opcode)
			print(oparg)
			if opcode in ( '-h', '--help' ) :
				print ("Help invoked!",file =  sys.stderr)
				usage()
				sys.exit(0)

			if opcode in ('-e', '--experiment' ) :
				self.exp_file = oparg
				if not os.path.exists( self.exp_file ) :
					print("File %s does not exist"%self.exp_file,file =  sys.stderr)
					print("Aborting",file = sys.stderr)
					sys.exit(1)


			if opcode in ('-o', '--domainfile' ) :
				self.domain_file_name = oparg

			if opcode in ('-n', '--domain' ) :
				self.domain_name = oparg

			if opcode in ('-u', '--sub-optimal-bound-array' ) :
				self.sub_optimal_bound_array = oparg

			if opcode in ('-g', '--design-budget-array' ) :
				self.design_budget_array_string = oparg

			if opcode in ('-p', '--template' ) :
				self.template_file_name = oparg

			if opcode in ('-y', '--hyps' ) :
				self.hyps_file_name = oparg

			if opcode in ('-b', '--obs-file-name' ) :
				self.observability_file_name = oparg

			if opcode in ('-r', '--rec-obs-file-name' ) :
				self.reciproceobservability_file_name = oparg

			if opcode in ('-a', '--action_tokens_file' ) :
				self.action_tokens_file_name = oparg


			if opcode in ('-d','--destination-folder'):
				self.destination_folder = opcode
			else:
				self.destination_folder = ''

			if opcode in ('-c', '--calc-methods' ) :
				calc_methods_arr = oparg.split('-')
				for method_string in calc_methods_arr:
					if method_string not in grd_defs.calc_method_options :
						print("Calculation method %s not supported"%method_string,file =  sys.stderr)
						print("Aborting",file = sys.stderr)
						sys.exit(1)
					self.calc_methods.append(method_string)

			if opcode in ('-v', '--combinations-examined' ) :
				comb_examined = oparg
				if comb_examined not in grd_defs.comb_examined_options :
					print("Combinations-examined %s not supported"%comb_examined,file =  sys.stderr)
					print("Aborting",file = sys.stderr)
					sys.exit(1)
				self.comb_examined = comb_examined



			if opcode in ('-t', '--max-time' ) :
				try :
					self.max_time = int(oparg)
					if self.max_time <= 0 :
						print ("Maximum time must be greater than zero", file =  sys.stderr)
						sys.exit(1)
				except ValueError :
					print("Time must be an integer",file = sys.stderr)
					sys.exit(1)

			if opcode in ('-m', '--max-memory' ) :
				try :
					self.max_memory = int(oparg)
					if self.max_memory <= 0 :
						print ("Maximum memory must be greater than zero" , file = sys.stderr)
						sys.exit(1)
				except ValueError :
					print ("Memory amount must be an integer" , file = sys.stderr )
					sys.exit(1)

			if opcode in ('-x', '--done-file-name' ) :
				self.done_file_path = oparg

				if not os.path.exists( self.done_file_path ) :
					print("File %s does not exist"%self.done_file_path,file =  sys.stderr)
					print("Aborting",file = sys.stderr)
					sys.exit(1)

			if opcode in ('-f', '--delete-log-folders' ) :
				self.delete_log_folders = oparg

			if opcode in ('-k', '--action_tokens_file_name' ) :
				self.action_tokens_file_name = oparg

			if opcode in ('-i', '--actions-to-remove' ) :
				self.actions_to_remove = oparg

			if opcode in ('-z', '--actions-constraints' ) :
				self.action_constraints = oparg


		if self.exp_file is None and self.domain_file_name is None :
			print("No experiment files were specified!!", file =  sys.stderr)
			usage()
			sys.exit(1)


	def print_options( self ) :

		#def print_yes() : print ( "Yes")
		#def print_no() : print ( "No")

		print("Options set")
		print( "===========")
		print("Experiment File:", self.exp_file)
		print("domain_file_name:", self.domain_file_name)
		print("template_file_name:", self.template_file_name)
		print("observability_file_name:", self.observability_file_name)
		print("reciproceobservability_file_name:", self.reciproceobservability_file_name)



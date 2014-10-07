install:
	python2 setup.py install
dev:
	#
	# Creating virtual development environment
	# 
	virtualenv2 dev
	#
	# NOTICE! 
	# 
	# You must manually execute 'source dev/bin/activate' to enable the virtual environment.
	#   Type 'deactivate' once complete. 
	# 
	# Then, type 'make', 'make install', or 'python2 setup.py install' to package the module.
	#
clean:
	#
	# Removing virtual development environment and setup files.
	# 
	rm -rf dev build dist noise.egg-info
	#
	# NOTICE!
	# 
	# You must manually execute 'deactivate' to disable the virtual environment.
	# 

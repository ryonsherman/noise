install:
	python2 setup.py install
uninstall:
	echo "TODO: Uninstall"
dep:
	#
	# Installing dependencies
	#
	pip2 install jinja2 markdown
	#
	if [ -e `which xsel` ]; then \
		echo 'make install' | xsel --clipboard --input; \
	fi
	#
	# If the 'xsel' binary exists the previous text was copied to the clipboard for your convenience.
	#
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
	# To provide dependencies type 'make dep'.
	#   To install, type 'make', 'make install', or 'python2 setup.py install' to package the module.
	#
	if [ -e `which xsel` ]; then \
		echo 'source dev/bin/activate; make dep' | xsel --clipboard --input; \
	fi
	#
	# If the 'xsel' binary exists the previous text was copied to the clipboard for your convenience.
	#
clean:
	#
	# Removing virtual development environment and setup files.
	#
	rm -rf dev build dist *.egg-info *.log
	#
	# NOTICE!
	#
	# You must manually execute 'deactivate' to disable the virtual environment.
	#
	if [ -e `which xsel` ]; then \
		echo 'deactivate' | xsel --clipboard --input; \
	fi
	#
	# If the 'xsel' binary exists the previous text was copied to the clipboard for your convenience.
	#

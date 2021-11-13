VER=v0.3

JAR = https://github.com/colin4124/knitkit/releases/download/$(VER)/knitkit.jar

prepare:
	mkdir -p knitkit/jars
	wget -O knitkit/jars/knitkit.jar $(JAR)

install-local:
	if [ -d "dist" ]; then rm -r dist; fi
	python3 setup.py bdist_wheel
	pip3 uninstall knitkit -y
	pip3 install --user `ls dist/*.whl`

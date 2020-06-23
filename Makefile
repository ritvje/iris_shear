init:
	pip install -r requirements.txt
build:
	python setup.py build_ext --inplace && python setup.py clean
install:
	pip install ./
clean:
	python setup.py clean --all

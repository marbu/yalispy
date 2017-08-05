.PHONY: test

test: test_yalispy.py yalispy.py
	python3 -m pytest -v test_yalispy.py --pdb

deploy:
	scp -r src root@178.128.105.101:/root/github.com/decaptcha/
	scp Makefile root@178.128.105.101:/root/github.com/decaptcha/

train:
	python3	src/train.py -i ../data_sets/ -m src/

test:
	python3 src/predict.py -i ../data_sets/ -m src/
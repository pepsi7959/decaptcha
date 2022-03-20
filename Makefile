deploy:
	scp -r decaptcha root@178.128.105.101:/root/github.com/decaptcha/decaptcha
	scp Makefile root@178.128.105.101:/root/github.com/decaptcha/

train:
	python3	decaptcha/decaptcha/captcha_master/train.py -i ../data_sets/ -m decaptcha/decaptcha/captcha_master/

test:
	python3 decaptcha/decaptcha/captcha_master/predict.py -i ../data_sets/ -m decaptcha/decaptcha/captcha_master/
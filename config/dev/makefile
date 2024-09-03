network:
	docker network create -d bridge oimbranet

# ###################################
# Inverse proxy
# ###################################

nginx:
	docker run -d -p 80:80 -p 443:443 --name nginx --net=oimbranet \
		-v ${HOME}/nginx.conf:/etc/nginx/nginx.conf:ro \
		-v ${HOME}/www/sites:/usr/share/nginx/www:ro \
		-v /etc/letsencrypt:/certs \
		nginx

# ###################################
# Backoffice
# ###################################

cotown:
	docker run -d --name cotown --restart=unless-stopped --net=oimbranet \
		-e COTOWN_ENV='development' \
		-v ${HOME}/app:/app \
		cotown

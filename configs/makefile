network:
	docker network create -d bridge cotownnet

nginx:
	docker run -d --name nginx -p 80:80 -p 443:443 --net=cotownnet \
                -v ${HOME}/cotown:/usr/share/nginx:ro \
                -v ${HOME}/cotown/nginx.conf:/etc/nginx/nginx.conf:ro \
                -v /etc/letsencrypt:/certs \
                nginx

cotowndev:
	docker run -d --name cotowndev --net=cotownnet \
		-e COTOWN_BACK='dev.cotown.ciber.es' \
		-e COTOWN_SERVER='experis.flows.ninja' \
		-e COTOWN_SECRET='3e595f8d-4ba2-4a7d-bede-2fca09e9ec97' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/dev/app:/app gunicorn

cotownpre:
	docker run -d --name cotownpre --net=cotownnet \
		-e COTOWN_BACK='pre.cotown.ciber.es' \
		-e COTOWN_SERVER='core.cotown.com' \
		-e COTOWN_SECRET='dea8ff00-78fb-4839-9a6e-3b20b59bc4e5' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/pre/app:/app gunicorn


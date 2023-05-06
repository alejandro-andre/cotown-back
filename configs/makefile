network:
	docker network create -d bridge cotownnet

nginx:
	docker run -d --name nginx -p 80:80 -p 443:443 --net=cotownnet \
        -v ${HOME}/cotown:/usr/share/nginx:ro \
        -v ${HOME}/cotown/nginx.conf:/etc/nginx/nginx.conf:ro \
        -v /etc/letsencrypt:/certs \
        nginx

listendev:
	docker run -d --name listendev --net=cotownnet \
		-e COTOWN_BACK='dev.cotown.ciber.es' \
		-e COTOWN_SERVER='experis.flows.ninja' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/dev/app:/app pyrun

backdev:
	docker run -d --name backdev --net=cotownnet \
		-e COTOWN_BACK='dev.cotown.ciber.es' \
		-e COTOWN_SERVER='experis.flows.ninja' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/dev/app:/app gunicorn

listenpre:
	docker run -d --name listenpre --net=cotownnet \
		-e COTOWN_BACK='pre.cotown.ciber.es' \
		-e COTOWN_SERVER='core.cotown.com' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/pre/app:/app pyrun

backpre:
	docker run -d --name backpre --net=cotownnet \
		-e COTOWN_BACK='pre.cotown.ciber.es' \
		-e COTOWN_SERVER='core.cotown.com' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/pre/app:/app gunicorn

network:
	docker network create -d bridge cotownnet

# ###################################
# Monitoring
# ###################################

loki:
	docker volume create loki-data
	docker run -d -p 3100:3100 --name=loki --net=cotownnet \
		-v loki-data:/loki \
		grafana/loki
	docker plugin install grafana/loki-docker-driver --alias lokidriver --grant-all-permissions

monitor:
	docker run -d -p 9100:9100 --name=nodexp --privileged --net="host" --pid="host" \
		-v "/:/host:ro,rslave" \
		quay.io/prometheus/node-exporter --path.rootfs=/host
	docker run -d -p 8080:8080 --name=cadvisor --privileged --device=/dev/kmsg \
                -v /:/rootfs:ro \
		-v /var/run:/var/run:ro \
		-v /sys:/sys:ro \
		-v /var/lib/docker/:/var/lib/docker:ro \
		-v /dev/disk/:/dev/disk:ro \
		gcr.io/cadvisor/cadvisor

grafana:
	docker volume create grafana-data
	docker run -d -p 3000:3000 --name=grafana --net=cotownnet\
		-v ${HOME}/cotown/config/grafana.ini:/etc/grafana/grafana.ini \
		-v grafana-data:/var/lib/grafana \
		grafana/grafana

prometheus:
	docker volume create prometheus-data
	docker run -d -p 9090:9090 --name=prometheus --net=cotownnet \
		-v prometheus-data:/prometheus \
		-v $(HOME)/cotown/config/prometheus.yml:/etc/prometheus/prometheus.yml \
		prom/prometheus

# ###################################
# Inverse proxy
# ###################################

nginx:
	docker run -d -p 80:80 -p 443:443 --name nginx --net=cotownnet \
		--log-driver=lokidriver --log-opt loki-url="http://localhost:3100/loki/api/v1/push" \
        	-v ${HOME}/cotown:/usr/share/nginx:ro \
        	-v ${HOME}/cotown/config/nginx.conf:/etc/nginx/nginx.conf:ro \
        	-v /etc/letsencrypt:/certs \
        	nginx

# ###################################
# Containers
# ###################################

backdev:
	docker run -d --name backdev --restart=unless-stopped --net=cotownnet \
		--log-driver=lokidriver --log-opt loki-url="http://localhost:3100/loki/api/v1/push" \
		-e COTOWN_BACK='dev.cotown.ciber.es' \
		-e COTOWN_SERVER='experis.flows.ninja' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/dev/app:/app cotown

backpre:
	docker run -d --name backpre --restart=unless-stopped --net=cotownnet \
		--log-driver=lokidriver --log-opt loki-url="http://localhost:3100/loki/api/v1/push" \
		-e COTOWN_SERVER='core.cotown.com' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/cotown/pre/app:/app cotown

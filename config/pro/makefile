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

promtail:
	docker run -d --name promtail --link=loki --net=cotownnet \
		-v $(HOME)/config:/mnt/config \
		-v ${HOME}/log:/var/log/cotown \
		grafana/promtail -config.file=/mnt/config/promtail-config.yaml

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
		-v ${HOME}/config/grafana.ini:/etc/grafana/grafana.ini \
		-v grafana-data:/var/lib/grafana \
		grafana/grafana

prometheus:
	docker volume create prometheus-data
	docker run -d -p 9090:9090 --name=prometheus --net=cotownnet \
		-v prometheus-data:/prometheus \
		-v $(HOME)/config/prometheus.yml:/etc/prometheus/prometheus.yml \
		prom/prometheus

# ###################################
# Inverse proxy
# ###################################

nginx:
	docker run -d -p 80:80 -p 443:443 --name nginx --net=cotownnet \
        	-v ${HOME}/usr/share/nginx:ro \
        	-v ${HOME}/config/nginx.conf:/etc/nginx/nginx.conf:ro \
        	-v /etc/letsencrypt:/certs \
        	nginx

# ###################################
# Backoffice
# ###################################

#--log-driver=lokidriver --log-opt loki-url="http://localhost:3100/loki/api/v1/push" 
back:
	docker run -d --name back --restart=unless-stopped --net=cotownnet \
		-e COTOWN_SERVER='core.cotown.com' \
		-e COTOWN_DATABASE='niledb' \
		-e COTOWN_DBUSER='postgres' \
		-e COTOWN_DBPASS='postgres' \
		-e COTOWN_GQLUSER='modelsadmin' \
		-e COTOWN_GQLPASS='Ciber$$2022' \
		-e COTOWN_SSHUSER='themes' \
		-e COTOWN_SSHPASS='Admin1234!' \
		-v ${HOME}/app:/app cotown

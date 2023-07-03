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
		-v $(HOME)/cotown/config:/mnt/config \
		-v ${HOME}/cotown/log:/var/log/cotown \
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
        	-v ${HOME}/cotown/www:/usr/share/nginx/www:ro \
        	-v ${HOME}/cotown/config/nginx.conf:/etc/nginx/nginx.conf:ro \
        	-v /etc/letsencrypt:/certs \
        	nginx

# ###################################
# Backoffice
# ###################################

back:
	docker run -d --name back --restart=unless-stopped --net=cotownnet \
		--log-driver=lokidriver --log-opt loki-url="http://localhost:3100/loki/api/v1/push" \
		-e COTOWN_ENV='development' \
		-v ${HOME}/cotown/app:/app cotown

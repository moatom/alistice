sta:
	docker-compose build --parallel && docker-compose up -d

# chmod u+x .dev.env 
dev:
	./.dev.env
	python backend/run.py &
	cd frontend && yarn nbp && yarn serve

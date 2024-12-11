# JWT и его роль в 200-миллисекундных микросервисах
[UML Диаграммы последовательности](docs/)
Для запуска проекта нужно:
```bash
python3.11+
docker
pip install setuptools
```

В первую очередь собираем библиотеку:
```bash
cd auth-library/
```
[Инструкция по сборке библиотеки](auth-library/README.md)

Дальше подготавливаем ENV
```bash
cp sample.env .env
```

Запускаем docker
```bash
docker compose up -d --force-recreate --build
```

> Порт auth-api: 8000
> 
> Порт car-api: 8002

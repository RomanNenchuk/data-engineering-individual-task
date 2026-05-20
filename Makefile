# Визначаємо UID поточного користувача Ubuntu
AIRFLOW_UID := $(shell id -u)

.PHONY: start stop logs restart clean

# Команда для запуску проєкту
start:
	@echo "🚀 Налаштування UID ($(AIRFLOW_UID)) та запуск Airflow..."
	@AIRFLOW_UID=$(AIRFLOW_UID) docker compose up -d
	@echo "⏳ Чекаємо пару секунд, поки Airflow прокинеться та встановить бібліотеки..."
	@sleep 5
	@echo "🔑 Отримання пароля адміністратора (шукаємо в логах):"
	@docker compose logs airflow-webserver-scheduler | grep -i "generated" || echo "Старт... Якщо це перший запуск, пароль з'явиться в логах за хвилину."
	@echo "🌐 Готово! Відкривай: http://localhost:8080"
	@echo "👤 Логін: admin"

# Команда для зупинки проєкту
stop:
	@echo "🛑 Зупинка контейнерів Airflow..."
	@docker compose down
	@echo "💤 Контейнери зупинено."

# Зручна команда для перегляду логів у реальному часі
logs:
	@docker compose logs -f airflow-webserver-scheduler

# Перезапуск контейнерів
restart: stop start

# Повне очищення (видаляє контейнери та створені Airflow метадані, якщо треба почати з нуля)
clean:
	@echo "🧹 Повне очищення контейнерів та системних томів..."
	@docker compose down -v

password:
	@echo "🔑 Твій згенерований пароль від Airflow:"
	@docker compose exec airflow-webserver-scheduler cat /opt/airflow/standalone_admin_password.txt

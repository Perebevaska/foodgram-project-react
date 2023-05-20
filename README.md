# Foodgram
![foodgram_workflow](https://github.com/perebevaska/foodgram-project-react/workflows/foodgram/badge.svg)

## Описание пет-проекта
Проект написан в рамках дипломного проекта в Яндекс.Практикуме по предоставленному фронтенду и спецификации api. Проект представляет собой сервис где пользователи могу создавать рецепты и делиться ими, добавлять в избранное и скачивать список ингридиентов

## Доступ к проекту
Проект запущен по адресу
- http://158.160.58.72/admin - страница администратора
- http://158.160.58.72/recipes - главная страница
- http://158.160.58.72/api/ - api

## Стек 
* Python 3.7
* Django 3.0
* Django REST Framework 3.12.4
* PostgreSQL 13.0
* Docker
* Github Actions
* Ubuntu 20.04 LTS

## Зависимости
- backend/requirements.txt

## Для запуска на своем сервере необходимо выполнить следующее:
1. Использовать Ubuntu 20.04 LTS
2. Установите Docker, выполнить следующие команды:
	```
	# Удалите предыдущие версии Docker
	sudo apt remove docker docker-engine docker.io containerd runc
	
	# Установите необходимые пакеты для загрузки через https
	sudo apt update && sudo apt install \
  	apt-transport-https \
  	ca-certificates \
  	curl \
  	gnupg-agent \
  	software-properties-common -y 
  	
	# Добавьте ключ GPG
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	
	# Добавьте репозиторий Docker
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
	 
	# Установите Docker
	sudo apt update && sudo apt install docker-ce docker-compose -y 
	
	# Проверьте, что Docker работает
	sudo systemctl status docker 
	
	# Добавьте вашего пользователя ОС в Docker группу
	sudo usermod -aG docker $USER
	sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
	sudo service docker restart
	```
3. Скопируйте из директории infra в /home/$USER/ следующие файлы:
    * docker-compose.yml
    * nginx.conf
4. В директории infra выполните команды:
	```
	sudo docker-compose up -d
	sudo docker-compose exec backend python manage.py makemigrations
	sudo docker-compose exec backend python manage.py migrate
	sudo docker-compose exec backend python manage.py collectstatic --no-input
	```
5. Для создания суперпользователя, выполните команду:
	```
	sudo docker-compose exec backend python manage.py createsuperuser
	```
6. Для добавления ингредиентов в БД выполните команду:
	```
	sudo docker-compose exec backend python manage.py add_data ingredients.csv recipes_ingredient
	```
7. Проект будет работать в трёх контейнерах db, backend, nginx
8. Для добавления рецептов необходимо создать хотя бы 1 тэг в модель Tags на странице администратора http://158.160.58.72/admin
9. Не рекомендуется использовать Django 4 версии и выше. Гарантирована нестабильная работа api из-за необходимости устанавливать django-cors-headers 

### Автор
Dmitriy Kormin

dmitriykormin@yandex.ru


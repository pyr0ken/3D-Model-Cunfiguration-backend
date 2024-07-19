run:
	python manage.py runserver

admin:
	python manage.py createsuperuser

db:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver

admin:
	python manage.py createsuperuser

db:
	python manage.py makemigrations
	python manage.py migrate

translate:
	python manage.py makemessages -l fi -i venv -i admin

translate-compile:
	python manage.py compilemessages

seed:
	python manage.py seeder
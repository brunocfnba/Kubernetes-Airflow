import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser
user = PasswordUser(models.User())
user.username = '<define your username>'
user.email = '<username e-mail address>'
user.password = '<user password>'
session = settings.Session()
session.add(user)
session.commit()
session.close()

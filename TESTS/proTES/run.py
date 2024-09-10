from foca import Foca

foca = Foca(config_file="config.yaml")
app = foca.create_app()
celery_app = foca.create_celery_app()

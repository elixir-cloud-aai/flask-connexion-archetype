"""Entry point for petstore example app."""

from foca import Foca

if __name__ == '__main__':
    foca = Foca(
        config_file="config.yaml"
    )
    app = foca.create_app()
    app.run(host="0.0.0.0", port=8080, lifespan="on")

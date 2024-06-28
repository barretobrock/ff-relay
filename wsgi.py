from ffrelay.app import create_app
from ffrelay.config import ProductionConfig

# Instantiate log here, as the hosts API is requested to communicate with influx
app = create_app(config_class=ProductionConfig)

if __name__ == '__main__':
    app.run(host=ProductionConfig.DB_SERVER, port=ProductionConfig.PORT)

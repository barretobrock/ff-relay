#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ffrelay.config import ProductionConfig

if __name__ == '__main__':
    from ffrelay.app import create_app

    # Instantiate log here, as the hosts API is requested to communicate with influx
    app = create_app(config_class=ProductionConfig)
    app.run(host=ProductionConfig.DB_SERVER, port=ProductionConfig.PORT)

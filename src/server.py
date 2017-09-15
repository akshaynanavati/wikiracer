import sys
from gevent import monkey

import app
import logging
from config import LOG_DIR

application = app.create_app()
if __name__ == '__main__':
    if LOG_DIR is not None:
        logging.basicConfig(filename='{}/app.log'.format(LOG_DIR), level=logging.INFO)
    monkey.patch_all()
    application.run(debug=True, host='0.0.0.0', port=int(sys.argv[1]))

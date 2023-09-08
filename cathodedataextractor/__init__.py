# coding=utf-8
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s in %(filename)s[line:%(lineno)d]--> %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('clog.txt', mode='w', encoding='utf-8')]
                    )

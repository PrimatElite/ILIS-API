from elasticsearch import Elasticsearch

from app.config import Config


elasticsearch = Elasticsearch([Config.ELASTICSEARCH_URL])

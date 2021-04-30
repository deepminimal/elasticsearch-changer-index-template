import json
import elasticsearch
import sys
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

arguments = len(sys.argv) - 1
if arguments != 3:
   print("You must specify a list of Nodes like 'http://elastic:9200,http://elastic2:9200' 'login' 'passvord' 'index1,test_index,some_index'")
   sys.exit(1)
nodes = sys.argv[1].split(',')
login, password = sys.argv[2], sys.argv[3]
conn = elasticsearch.Elasticsearch(nodes, http_auth=(login, password))

indices = sys.argv[4].split(',') # array of new indices from args

for index_template_name in indices:
    # set ilm policy 
    ilm_policy = {
        "policy": {
            "phases": {
                "hot": {
                    "actions": {
                        "rollover": {
                            "max_age": "7d",
                            "max_size": "150gb",
                            "max_docs": 400000000
                        },
                        "set_priority": {
                            "priority": 100
                        }
                    }
                },
                "delete": {
                    "min_age": "14d",
                    "actions": {
                        "delete": {}
                    }
                }
            }
        }
    }

    # set index template settings
    index_template = {
        "order": 20010,
        "index_patterns": [
            "{}*".format(index_template_name)
        ],
        "settings": {
            "index": {
            "codec" : "best_compression",
            "lifecycle": {
                "name": "{}".format(index_template_name),
                "rollover_alias": "{}".format(index_template_name)
            },
            "refresh_interval": "1m",
            "number_of_shards": "3",
            "number_of_replicas": "0"
            }
        },
        "mappings": {
            "_doc": {
                "dynamic": True,
                "numeric_detection": True,
                "date_detection": True,
                "dynamic_date_formats": [
                    "strict_date_optional_time",
                    "yyyy/MM/dd HH:mm:ss Z||yyyy/MM/dd Z"
                ],
                "_source": {
                    "enabled": True,
                    "includes": [],
                    "excludes": []
                },
                "_routing": {
                    "required": False
                }
            }
        }
    }

    # set index aliases for ilm policy (this settings need for rollover)
    index_aliases = {
    "aliases": {
            "{}".format(index_template_name):{
                "is_write_index": True 
            }
        }
    }

    # put new ilm policy or overwite
    result = conn.ilm.put_lifecycle(index_template_name, ilm_policy)
    print("PUT ILM_POLICY", index_template_name, ilm_policy, result)

    # put new index template settings or overwite 
    result = conn.indices.put_template(index_template_name, index_template, params={"include_type_name":'true'})
    print("PUT INDEX_TEMPLATE", index_template_name, index_template, result)

    # this body need for index test doc
    doc = {
        'level': 'info',
        'text': 'Test message!',
        '@timestamp': datetime.now()
    }

    try: # check if index already present 
        result = conn.indices.get(index_template_name)
        print('!!! ERROR !!! Index: {} is already present.'.format(index_template_name)) 
    except:
        result = requests.put("{}{}-000001".format(nodes, index_template_name), json=index_aliases, auth=(login, password)) # put index aliases for rollover
        print("PUT {}-000001".format(index_template_name), result.text) 
        print("POST DATA= {}".format(conn.index(index=index_template_name, body=doc))) # post data to new index for activate ilm policys

import json
import elasticsearch
import sys

arguments = len(sys.argv) - 1
if arguments != 3:
    print('You must specify a list of Nodes like "http://elastic:9200,http://elastic2:9200" "login" "passvord"')
    sys.exit(1)
nodes = sys.argv[1].split(',')
login, password = sys.argv[2], sys.argv[3]
conn = elasticsearch.Elasticsearch(nodes, http_auth=(login, password))

for template in indices_templates.keys(): # for each template
    
    if not '.' in template: # filter system templates
        compare_current_template_settings = json.dumps(indices_templates[template], sort_keys=True) 
        modified_template_settings = json.loads(compare_current_template_settings)
        
        modified_template_settings['settings']['index']['number_of_shards'] = 3
        modified_template_settings['settings']['index']['auto_expand_replicas'] = False
        modified_template_settings['settings']['index']['number_of_replicas'] = 0
        modified_template_settings['settings']['index']['codec'] = 'best_compression'
        modified_template_settings['settings']['index']['refresh_interval'] = '1m'

        if not 'mapping' in modified_template_settings['settings']['index'].keys():
            modified_template_settings['settings']['index']['mapping'] = {}
            modified_template_settings['settings']['index']['mapping']['total_fields'] = {}
            
        if not 'mappings' in modified_template_settings.keys():
            modified_template_settings['mappings']['numeric_detection'] = False
            modified_template_settings['mappings']['dynamic'] = True
            
        modified_template_settings['settings']['index']['mapping']['total_fields']['limit'] = 100000
        modified_template_settings['mappings']['numeric_detection'] = False
        modified_template_settings['mappings']['dynamic'] = True
        compare_modified_template_settings = ''
        compare_modified_template_settings = json.dumps(modified_template_settings, sort_keys=True)
        if not compare_modified_template_settings == compare_current_template_settings:
            result = conn.indices.put_template(str(template), modified_template_settings)
            print(template, result)
        else:
            print(template)


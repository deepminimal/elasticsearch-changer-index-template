# elasticsearch-changer-index-template
 This script can automate change indexes templates for all index in cluster and put pre settings for new indecies
 
 Case: You have 2 data nodes and 2 primary shard in index template. You add third data nodes and you need to increase primary shard in all index templates. 

Usually we set index name, ilm policy, index template, index aliases names the same as index name
## HOW TO USE:
### index_template_changer 
Set ElasticSearch nodes separated by comma (,) login and password
#### Example:
python index_template_changer.py "http://elastic:9200,http://elastic2:9200" "login" "passvord"

Scripts get all index template in ElasticSearch (except system indices started from .*), set new settings, compare between old template and new and put changed template to ElasticSearch
#### =====================================
### new_index_pre_settings 
Set ElasticSearch nodes separated by comma (,) login and password, index name separeted by comma (,)
#### Example:
python new_index_pre_settings.py "http://elastic:9200,http://elastic2:9200" "login" "passvord" "new-index,test_index,some_new_index"
Scripts put new overwrite ilm policy and index template. Set index aliases for rollover and index test message
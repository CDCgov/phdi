# specifiy resource group
resource_group=$1
offset_days=$2

# prevent override by checking if "created-by" tag exists
tag_search='properties.tags.\"created-by\"'

# fetch resource activites (last 90d)
azout=$(az monitor activity-log list \
-g $resource_group \
--offset ${offset_days}d \
--max-events 1000000 \
--query "[].{op:operationName.localizedValue, opValue:operationName.value, action:authorization.action, \
resourceId:resourceId, eventTimestamp:eventTimestamp, eventName:eventName.value, status:status.value, \
caller:caller, name:claims.name, timestamp:claims.iat, subStatus:subStatus.value, \
correlationId:correlationId}[? (status=='Succeeded' || subStatus=='Created') && action==opValue \
&& contains(caller, '@') && op!='Write tags' \
&& !(contains(op, 'Deployment')) && !(contains(op, 'role assignment')) && !(contains(op, 'Subnet')) \
&& !(contains(op, 'zone link')) && !(contains(op, 'Linked Service')) && !(contains(op, 'Runtime')) \
&& !(contains(op, 'Peering')) && !(contains(op, 'record set')) && !(contains(op, 'diagnostic')) \
&& !(contains(op, 'Pipeline')) && !(contains(op, 'Consumer')) && !(ends_with(op, 'rule')) \
&& !(contains(op, 'Association')) && !(ends_with(op, 'proxy.')) && !(contains(op, 'Dataset')) \
&& !(contains(op, 'Configuration')) && !(contains(op, 'config'))]")

# list grouped by resource and min timestamp
resource_list=$(echo $azout | jq 'group_by(.resourceId) | map({resourceId: .[0].resourceId, caller: .[0].caller, op: .[0].op, min: map(.eventTimestamp) | min})[]')

# if "created-by" tag does not exist, create "created-by" and "created-at" tags
echo $resource_list \
| jq --arg b "$tag_search" '"if [[ -z $(az tag list --resource-id " + .resourceId + " -o tsv --query " + $b + " -o tsv 2>/dev/null) ]]; then " + "az tag update --resource-id " + .resourceId + " --operation merge --tags created-by=" + .caller + " created-at=`date -d " + .min + " --iso-8601=minutes` >/dev/null 2>/dev/null; fi;"' \
| while read line ; do eval ${line:1:-1} ; done

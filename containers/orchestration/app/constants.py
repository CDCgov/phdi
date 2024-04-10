from app.utils import read_json_from_assets

# /process endpoint #
process_message_request_examples = read_json_from_assets(
    "sample_process_message_requests.json"
)
raw_process_message_response_examples = read_json_from_assets(
    "sample_process_message_responses.json"
)
process_message_response_examples = {200: raw_process_message_response_examples}

# /configs endpoint #
raw_list_configs_response = read_json_from_assets("sample_list_configs_response.json")
sample_list_configs_response = {200: raw_list_configs_response}

upload_config_request_examples = read_json_from_assets(
    "sample_upload_config_requests.json"
)

upload_config_response_examples = {
    200: "sample_upload_config_response.json",
    201: "sample_update_config_response.json",
    400: "sample_upload_config_failure_response.json",
}

# /configs/{processing_config_name} endpoint #
raw_get_config_response = read_json_from_assets("sample_get_config_response.json")
sample_get_config_response = {200: raw_get_config_response}

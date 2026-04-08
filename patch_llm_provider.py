file_path = 'template_source/.agents/engine/core/llm_provider.py'
with open(file_path, 'r') as f:
    content = f.read()

search = """    def _log_raw_send(self, payload):
        if self.raw_send:
            logger.info(f"[RAW SEND]: {json.dumps(payload, indent=2, default=str)}")
            print(f"[RAW SEND]: {json.dumps(payload, indent=2, default=str)}")

    def _log_raw_return(self, response):
        if self.raw_return:
            # Attempt to stringify if not string
            if not isinstance(response, str):
                response = json.dumps(response, indent=2, default=str)
            logger.info(f"[RAW RETURN]: {response}")
            print(f"[RAW RETURN]: {response}")"""

replace = """    def _sanitize_payload(self, data):
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if k.lower() in ['api_key', 'key', 'token', 'secret']:
                    sanitized[k] = '***REDACTED***'
                elif isinstance(v, (dict, list)):
                    sanitized[k] = self._sanitize_payload(v)
                elif isinstance(v, str) and len(v) > 500:
                    sanitized[k] = v[:500] + '... [TRUNCATED]'
                else:
                    sanitized[k] = v
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_payload(item) for item in data]
        elif isinstance(data, str) and len(data) > 500:
            return data[:500] + '... [TRUNCATED]'
        return data

    def _log_raw_send(self, payload):
        if self.raw_send:
            sanitized_payload = self._sanitize_payload(payload)
            logger.info(f"[RAW SEND]: {json.dumps(sanitized_payload, indent=2, default=str)}")
            print(f"[RAW SEND]: {json.dumps(sanitized_payload, indent=2, default=str)}")

    def _log_raw_return(self, response):
        if self.raw_return:
            # Attempt to stringify if not string
            if not isinstance(response, str):
                try:
                    response_dict = json.loads(json.dumps(response, default=str))
                    sanitized_response = self._sanitize_payload(response_dict)
                    response = json.dumps(sanitized_response, indent=2, default=str)
                except Exception:
                    response = str(response)
            else:
                response = self._sanitize_payload(response)
            logger.info(f"[RAW RETURN]: {response}")
            print(f"[RAW RETURN]: {response}")"""

new_content = content.replace(search, replace)
if new_content == content:
    print("Failed to replace!")
else:
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("Replaced successfully!")

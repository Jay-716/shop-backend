import yaml

with open("config.yaml") as config:
    cfg = yaml.safe_load(config)
    user = cfg["database"]["user"]
    password = cfg["database"]["password"]
    db_name = cfg["database"]["db_name"]
    host = cfg["database"]["host"]
    SECRET_KEY = cfg["auth"]["secret_key"]
    ALGORITHM = cfg["auth"]["algorithm"]
    ACCESS_TOKEN_EXPIRE_MINUTES = cfg["auth"]["access_token_expire_minutes"]
    STORAGE_PATH = cfg["storage"]["storage_path"]
    FILE_BLOCK_SIZE = cfg["storage"]["file_block_size"]
    LOG_STORAGE_PATH = cfg["storage"]["log_storage_path"]
    api_root = cfg["api_root"]
    enable_doc = cfg["enable_doc"]
    allow_origins = cfg["allow_origins"]
    redis_host = cfg["redis"]["host"]
    redis_port = cfg["redis"]["port"]
    # mail
    smtp_server = cfg["mail"]["smtp_server"]
    smtp_port = cfg["mail"]["smtp_port"]
    account_name = cfg["mail"]["account_name"]
    account_password = cfg["mail"]["account_password"]
    account = cfg["mail"]["account"]
    subject = cfg["mail"]["subject"]

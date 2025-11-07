import json, logging, os, sys, asyncio, client


# Initialize config
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(funcName)s :: %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)])

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)

default_config = {
        "api-key": "",
        "max-tokens": 8192,
        "temperature": 1,
        "model": "", # Just used for custom
        "base-url": "", # Just used for custom
        "base-chat-cache-folder": "cache/chat_cache",
    }
if not os.path.exists(project_root+'/config.json'):
    with open(project_root+'/config.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(default_config, indent=2))
else:
    with open(project_root+'/config.json', 'r', encoding='utf-8') as f:
        _config = json.loads(f.read())
    missing_key = default_config.keys() - _config.keys()
    if missing_key:
        with open(project_root + '/config.json', 'w', encoding='utf-8') as f:
            for k in missing_key:
                _config[k] = default_config[k]
            f.write(json.dumps(_config, indent=2))


async def main():
    # Start MCP client only. MCP server will be started by client.
    await client.run()

if __name__ == '__main__':
    asyncio.run(main())
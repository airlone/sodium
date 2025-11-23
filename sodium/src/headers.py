from typing import Literal, Dict, Any, List
from typing_extensions import overload
import base64
import json

"""Supported Chrome Versions"""
CHROME_VERSIONS = Literal[
    "124",
    "136",
    "128",
    "116",
    "131"
]

"""Headers class"""
class headers:
    def __init__(self, chrome_version:CHROME_VERSIONS):
        self.chrome_version = chrome_version
        self.base_headers:Dict = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'priority': 'u=1, i',
            'sec-ch-ua': f'"Chromium";v="{chrome_version}", "Not;A=Brand";v="{chrome_version[-2:]}", "Google Chrome";v="{chrome_version}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
        }
    
    @overload
    def add_to_header(self, key: str, val: Any) -> None: ...
    
    @overload
    def add_to_header(self, new_vals: Dict[str, Any]) -> None: ...

    def add_to_header(self, *args):
        
        if len(args) == 2 and isinstance(args[0], str):
            key, val = args
            self.base_headers[key] = val
            return
    
        if len(args) == 1 and isinstance(args[0], dict):
            for k, v in args[0].items():
                self.base_headers[k] = v
            return

        raise TypeError("Invalid arguments for add_to_header()")

    def bulk_remove(self, keys:List[str]) -> None:
        for k in keys:
            if k in self.base_headers.keys():
                self.base_headers.pop(k)
            else:
                raise KeyError

    def remove_from_header(self, key:str) -> None:
        if key in self.base_headers.keys():
            self.base_headers.pop(key)
        else:
            raise KeyError

    def add_xsup(self) -> None:
        xsup_data = json.dumps({
            "os":"Windows",
            "browser":"Chrome",
            "device":"",
            "system_locale":"en-US",
            "has_client_mods": False,
            "browser_user_agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36",
            "browser_version":f"{self.chrome_version}.0.0.0",
            "os_version":"10",
            "referrer":"",
            "referring_domain":"",
            "referrer_current":"",
            "referring_domain_current":"",
            "release_channel":"stable",
            "client_build_number":471383,
            "client_event_source": None
        })

        json_bytes = xsup_data.encode('utf-8')
        self.base_headers["x-super-properties"] = str(base64.b64encode(json_bytes).decode('utf-8'))


    @property
    def chrome_ver(self) -> int:
        return int(self.chrome_version)

    @property
    def headers(self) -> Dict:
        return self.base_headers
import os
import time
import json
import asyncio
import aiohttp
import curl_cffi
from typing import Optional, Dict, List
from headers import headers
from console import GradientConsole
from pretty import logo


class Client:
    def __init__(
        self, 
        token: str, 
        targets:List[Dict], 
        guid:str, 
        password:str,
        console: GradientConsole
    ) -> None:
        self.token = token
        self.s: Optional[int] = None
        self.session_id: Optional[str] = None
        self.uri: Optional[str] = None
        self.tasks = []
        self.xtick = None
        self.session = curl_cffi.Session(impersonate="chrome136")
        self.dheaders = headers(chrome_version="136")
        self.targets = targets
        self.guid = guid
        self.password = password
        self.console = console

        self.gateway_url = "wss://gateway.discord.gg/?encoding=json&v=9"

    # ----------------------------------------------------------------------
    # Utility: Base Discord Headers
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # MFA Handler
    # ----------------------------------------------------------------------
    def _mfa(self, password: str, ticket: str, cookies):
        url = "https://discord.com/api/v9/mfa/finish"

        self.dheaders.add_to_header({
            "authorization": self.token,
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "America/New_York",
            "x-discord-mfa-authorization": self.xtick,
        })

        payload = {
            "ticket": ticket,
            "mfa_type": "password",
            "data": password,
        }

        try:
            response = self.session.post(url, json=payload, headers=self.dheaders.headers, cookies=cookies)
            data = response.json()

            return data.get("token"), response.cookies.get("__Secure-recent_mfa")

        except Exception as e:
            print(f"[MFA Error] {e}")
            return None, None

    # ----------------------------------------------------------------------
    # Vanity Sniper
    # ----------------------------------------------------------------------
    async def change_vanitys(self, vanity_code: str) -> None:
        url = f"https://discord.com/api/v9/guilds/{self.guid}/vanity-url"

        if self.xtick:
            self.dheaders.add_to_header("x-discord-mfa-authorization", self.xtick)

        try:
            response = self.session.patch(url, json={"code": vanity_code}, headers=self.dheaders.headers)

            if response.status_code == 200:
                self.console.println(f"Sniped Vanity -> {vanity_code}")
                return

            # MFA required
            if "mfa" in response.text:
                ticket = response.json()["mfa"]["ticket"]
                cookies = response.cookies

                tick, recent = self._mfa(self.password, ticket, cookies)
                if not tick:
                    self.console.println("Failed to solve MFA Ticket")
                    return

                self.xtick = tick
                self.dheaders.add_to_header("x-discord-mfa-authorization", tick)

                cookie_payload = {
                    "__Secure-recent_mfa": recent,
                    "__dcfduid": cookies.get("__dcfduid"),
                    "__sdcfduid": cookies.get("__sdcfduid"),
                    "__cfruid": cookies.get("__cfruid"),
                    "_cfuvid": cookies.get("_cfuvid"),
                }

                final = self.session.patch(url, json={"code": vanity_code}, headers=self.dheaders.headers, cookies=cookie_payload)

                if final.status_code == 200:
                    self.console.println(f"Sniped Vanity -> {vanity_code}")

        except Exception as e:
            self.console.println(f"[VANITY ERROR]]\t" + e)

    # ----------------------------------------------------------------------
    # Gateway Start
    # ----------------------------------------------------------------------
    async def start(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.gateway_url, max_msg_size=20 * 1024 * 1024) as ws:
                    await self.send_presence(ws)
                    self.tasks = [self._handle_events(ws)]
                    await asyncio.gather(*self.tasks)

        except Exception as e:
            print(f"Error starting connection: {e}")

    # ----------------------------------------------------------------------
    # Presence Payload
    # ----------------------------------------------------------------------
    async def send_presence(self, ws):
        try:
            await ws.send_json({
                "op": 2,
                "d": {
                    "token": self.token,
                    "capabilities": 30717,
                    "properties": {
                        "os": "Windows",
                        "browser": "Chrome",
                        "device": "Desktop",
                        "system_locale": "en-US",
                        "browser_user_agent": self.dheaders.headers["user-agent"],
                        "browser_version": "136",
                        "os_version": "10",
                        "referrer": "",
                        "referring_domain": "",
                        "release_channel": "stable",
                        "client_build_number": 468244,
                        "client_event_source": None
                    },
                    "presence": {
                        "afk": False,
                        "since": time.time(),
                        "activities": [],
                        "status": "dnd"
                    },
                    "compress": False,
                    "client_state": {"guild_versions": {}}
                }
            })
        except Exception as e:
            print(f"Error sending presence: {e}")

    # ----------------------------------------------------------------------
    # Gateway Event Loop
    # ----------------------------------------------------------------------
    async def _handle_events(self, ws):
        try:
            async for msg in ws:
                event = json.loads(msg.data)

                # Sequence ID
                if "s" in event:
                    self.s = event["s"]

                # Heartbeat
                op = event.get("op")
                t = event.get("t")
                d = event.get("d")

                if op == 10:
                    interval = event["d"]["heartbeat_interval"] / 1000
                    asyncio.create_task(self.send_heartbeat(ws, interval))

                if t == "READY":
                    self.gateway_url = event["d"]["resume_gateway_url"] + '/?encoding=json&v=9'
                    logo()
                    self.console.println("LOGGED INTO CLIENT. Sniping Vanities: " + str(len(self.targets.keys())))

                if t == "GUILD_UPDATE":
                    gid = d["id"]
                    current = d["vanity_url_code"]

                    if gid in self.targets and self.targets[gid] != current:
                        await self.change_vanitys(self.targets[gid], self.password)

        except Exception as e:
            print(f"[Events Error] {e}")

    # ----------------------------------------------------------------------
    # Heartbeats
    # ----------------------------------------------------------------------
    async def send_heartbeat(self, ws, interval: float):
        try:
            while True:
                await ws.send_json({"op": 1, "d": self.s})
                await asyncio.sleep(interval)

        except Exception as e:
            print(f"Error sending heartbeat: {e}")


    @staticmethod
    def fetch_guild_id(vanity:str) -> str | None:
        url = "https://discord.com/api/v9/invites/" + vanity

        resp = curl_cffi.requests.get(url, headers=headers(chrome_version="136").headers)
        if "id" in resp.text:
            return resp.json()["guild"]["id"]
        return None
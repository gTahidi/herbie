import asyncio
import json
import aiohttp
from dataclasses import dataclass
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import os

@dataclass
class State:
    current_target: str = None
    scan_results: dict = None

class APISecurityTool(Tool):
    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        await self.prepare_state()

        action = self.args.get("action", "").lower().strip()
        target = self.args.get("target", "").strip()

        if not target:
            return Response(
                message=self.agent.read_prompt("pentest/api_security_tool_usage.md"),
                break_loop=False
            )

        if action == "subdomain_scan":
            response = await self.scan_subdomains(target)
        elif action == "dns_lookup":
            response = await self.dns_lookup(target)
        elif action == "ssl_check":
            response = await self.ssl_check(target)
        elif action == "port_scan":
            response = await self.port_scan(target)
        elif action == "whois":
            response = await self.whois_lookup(target)
        else:
            response = self.agent.read_prompt("pentest/api_security_tool_usage.md")

        return Response(message=response, break_loop=False)

    async def prepare_state(self):
        if not hasattr(self.agent.state, "api_security"):
            self.agent.state.api_security = State()

    async def scan_subdomains(self, target):
        """Scan subdomains using RapidAPI's subdomain scanner"""
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            return "Error: RAPIDAPI_KEY not found in environment variables"

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "subdomain-scan.p.rapidapi.com",
            'Content-Type': "application/x-www-form-urlencoded"
        }

        payload = f"domain={target}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://subdomain-scan.p.rapidapi.com/subdomain-scan/",
                    headers=headers,
                    data=payload
                ) as response:
                    result = await response.json()
                    self.agent.state.api_security.scan_results = result
                    return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error during subdomain scan: {str(e)}"

    async def dns_lookup(self, target):
        """Perform DNS lookup using RapidAPI's DNS lookup service"""
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            return "Error: RAPIDAPI_KEY not found in environment variables"

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "dns-lookup6.p.rapidapi.com"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"https://dns-lookup6.p.rapidapi.com/?domain={target}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error during DNS lookup: {str(e)}"

    async def ssl_check(self, target):
        """Check SSL certificate information using RapidAPI's SSL checker"""
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            return "Error: RAPIDAPI_KEY not found in environment variables"

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "ssl-checker7.p.rapidapi.com"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"https://ssl-checker7.p.rapidapi.com/?domain={target}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error during SSL check: {str(e)}"

    async def port_scan(self, target):
        """Perform port scanning using RapidAPI's port scanner"""
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            return "Error: RAPIDAPI_KEY not found in environment variables"

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "port-scanner8.p.rapidapi.com"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"https://port-scanner8.p.rapidapi.com/scan?host={target}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error during port scan: {str(e)}"

    async def whois_lookup(self, target):
        """Perform WHOIS lookup using RapidAPI's WHOIS service"""
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            return "Error: RAPIDAPI_KEY not found in environment variables"

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "whois-lookup1.p.rapidapi.com"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"https://whois-lookup1.p.rapidapi.com/?domain={target}",
                    headers=headers
                ) as response:
                    result = await response.json()
                    return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error during WHOIS lookup: {str(e)}"

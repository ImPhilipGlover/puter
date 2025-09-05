# /puter/aura/clients/cli_client.py
"""
An interactive command-line client for sending messages to the running AURA system.
"""
import httpx
import shlex
import json
from rich.console import Console
from rich.prompt import Prompt

AURA_API_URL = "http://localhost:8000/message"
console = Console()

def print_welcome():
    """Prints a welcome message."""
    console.print("[bold cyan]AURA Command Line Interface[/bold cyan]")
    console.print("Type 'health' to check system status.")
    console.print("Type 'exit' or 'quit' to close the client.")
    console.print("Send messages in the format: [target_id][method_name] *[arg1] *[arg2] **[kwarg1=value]...")
    console.print("Example: system greet name='Architect'")
    console.print("-" * 50)

def parse_args(args_list: list) -> tuple[list, dict]:
    """
    RECTIFICATION: Replaced naive parser with a more robust implementation
    that correctly handles quoted JSON strings for positional and keyword arguments.
    """
    args = []
    kwargs = {}
    for arg in args_list:
        if '=' in arg:
            key, value = arg.split('=', 1)
            try:
                # Try to parse value as JSON (for numbers, bools, lists, dicts)
                kwargs[key] = json.loads(value)
            except json.JSONDecodeError:
                # Fallback to string if not valid JSON
                kwargs[key] = value
        else:
            try:
                args.append(json.loads(arg))
            except json.JSONDecodeError:
                args.append(arg)
    return args, kwargs

async def main():
    """Main async loop for the CLI client."""
    print_welcome()
    async with httpx.AsyncClient(timeout=120.0) as client:
        while True:
            try:
                input_str = Prompt.ask("> ")
                if input_str.lower() in ['exit', 'quit']:
                    break
                
                if input_str.lower() == 'health':
                    try:
                        response = await client.get("http://localhost:8000/health")
                        console.print(response.json())
                    except httpx.RequestError as e:
                        console.print(f"[bold red]Error checking health: {e}[/bold red]")
                    continue

                parts = shlex.split(input_str)
                if len(parts) < 2:
                    console.print("[bold red]Invalid format. Use: [target_id][method_name]...[/bold red]")
                    continue

                target_id = parts[0]
                method_name = parts[1]
                args, kwargs = parse_args(parts[2:])

                payload = {
                    "target_object_id": target_id,
                    "method_name": method_name,
                    "args": args,
                    "kwargs": kwargs
                }

                console.print(f"Sending: {payload}")
                response = await client.post(AURA_API_URL, json=payload)

                if response.status_code == 200:
                    console.print("[bold green]Response:[/bold green]")
                    console.print(response.json())
                else:
                    console.print(f"[bold red]Error ({response.status_code}):[/bold red]")
                    console.print(response.json())

            except httpx.RequestError as e:
                console.print(f"[bold red]Connection error: {e}[/bold red]")
            except Exception as e:
                console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
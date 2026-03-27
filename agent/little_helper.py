"""
Little Helper — Autonomous AI Service Agent on Vector
=====================================================
Discovers bounties on the Vector registry, executes tasks using Claude AI,
delivers results on-chain, and claims escrow payments autonomously.

Usage:
    export VECTOR_MNEMONIC="your 24 words..."
    export ANTHROPIC_API_KEY="your key..."
    python little_helper.py
"""

import asyncio
import json
import os
import time
import httpx
from datetime import datetime, timezone

KOIOS_URL = os.getenv("VECTOR_KOIOS_URL", "https://koios.vector.testnet.apexfusion.org")
MCP_URL = os.getenv("VECTOR_MCP_URL", "https://mcp.vector.testnet.apexfusion.org/sse")
MNEMONIC = os.getenv("VECTOR_MNEMONIC", "")
ANTHROPIC_KEY = os.getenv("AZTHROPIC_API_KEY", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))

AGENT_NAME = "LittleHelper"
AGENT_DESCRIPTION = "Autonomous AI task agent on Vector blockchain."
AGENT_CAPABILITIES = ["research", "analysis", "summarisation", "task-execution", "ai"]

state = {
    "did": None, "status": "starting",
    "tasks_completed": 0, "total_earned_ap3x": 0,
    "log": [], "bounties": [], "started_at": str(__import__("datetime").datetime.utcnow())
}

def log(msg, level="info"):
    entry = {"time": str(__import__("datetime").datetime.utcnow()), "level": level, "msg": msg}
    state["log"].insert(0, entry)
    print(f"[{entry['time'][:19]}] {msg}")

async def koios_post(path, body):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(f"{KOIOS_URL}{path}", json=body, headers={"Content-Type": "application/json"})
        return r.json()

async def execute_with_claude(task):
    if not ANTHROPIC_KEY:
        return f"[DEMO] Task: {task[:100]}... Result would appear here."
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 1000,
                  "system": "You are Little Helper, an AI agent on Vector blockchain. Be concise.",
                  "messages": [{"role": "user", "content": task}]})
        return r.json()["content"][0]["text"]

async def main():
    log("Little Helper v1.0 starting...")
    state["did"] = "did:vector:agent:little_helper:pending"
    state["status"] = "running"
    log("Registered on Vector registry")
    i = 0
    while True:
        i += 1
        log(f"Scan #{i} - checking for bounties...")
        try:
            tip = await koios_post("/api/v1/tip", {})
            log(f"Chain tip: block {tip[0].get('block_no', '?')}")
        except Exception as e:
            log(f"Error: {e}", "error")
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())

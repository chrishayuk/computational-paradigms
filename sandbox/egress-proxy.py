#!/usr/bin/env python3
"""The only way out of a role's container.

Role containers sit on a host-only network (`cp-roles`) with no route to
the internet. This proxy, on the host, listens on that network's gateway
and accepts only HTTPS CONNECT requests to the hosts allowed for the port
used: one port for Claude roles, one for Codex roles. Every request,
allowed or refused, is logged with its time and host.

    egress-proxy.py GATEWAY_IP LOGFILE
"""
import asyncio, sys, time

ALLOW = {
    3128: {"api.anthropic.com"},                                   # Claude roles
    3129: {"chatgpt.com", "api.openai.com", "auth.openai.com"},    # Codex roles
}

def log(path, port, host, verdict):
    with open(path, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{port}\t{host}\t{verdict}\n")

async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data)
            await w.drain()
    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    finally:
        w.close()

def handler(port, logfile):
    async def handle(reader, writer):
        try:
            line = (await reader.readline()).decode("latin-1").split()
            while (await reader.readline()) not in (b"\r\n", b"\n", b""):
                pass
            if len(line) < 2 or line[0] != "CONNECT":
                log(logfile, port, " ".join(line)[:200], "refused-method")
                writer.write(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
                return writer.close()
            host, _, p = line[1].rpartition(":")
            if host not in ALLOW[port] or p != "443":
                log(logfile, port, line[1], "refused")
                writer.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
                return writer.close()
            ur, uw = await asyncio.open_connection(host, 443)
            log(logfile, port, line[1], "allowed")
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()
            await asyncio.gather(pipe(reader, uw), pipe(ur, writer))
        except Exception as e:  # a broken client must not stop the proxy
            log(logfile, port, f"error {e!r}"[:200], "error")
            writer.close()
    return handle

async def main(ip, logfile):
    servers = [await asyncio.start_server(handler(p, logfile), ip, p) for p in ALLOW]
    await asyncio.gather(*(s.serve_forever() for s in servers))

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))

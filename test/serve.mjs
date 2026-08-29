// Minimal static server with the MIME types the viewer needs for ES-module
// import() and WebAssembly. `node test/serve.mjs <root> <port>`.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const ROOT = process.argv[2] || process.cwd();
const PORT = Number(process.argv[3] || 8791);

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".wasm": "application/wasm",
  ".css": "text/css",
  ".json": "application/json",
  ".nsigii": "application/octet-stream",
  ".bin": "application/octet-stream",
};

createServer(async (req, res) => {
  try {
    const { pathname } = new URL(req.url, "http://x");
    const rel = normalize(decodeURIComponent(pathname)).replace(/^([/\\]|\.\.[/\\])+/, "");
    const body = await readFile(join(ROOT, rel || "index.html"));
    res.writeHead(200, { "content-type": TYPES[extname(rel)] || "application/octet-stream" });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end("not found");
  }
}).listen(PORT, "127.0.0.1", () => console.log(`serving ${ROOT} on http://127.0.0.1:${PORT}`));

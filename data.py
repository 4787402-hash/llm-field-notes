# -*- coding: utf-8 -*-
"""Content for the site. Every entry below was reproduced and fixed on real
hardware before being written here. Do not add entries that were not verified.
"""

SITE = {
    "name": "Local AI Field Notes",
    "tagline": "Errors reproduced on real hardware, with the fix that actually worked.",
    "base": "https://4787402-hash.github.io/llm-field-notes",
}

ERRORS = [
    {
        "slug": "llama-cpp-invalid-split-file-name",
        "title": "llama.cpp: error loading model: invalid split file name",
        "err": "error loading model: invalid split file name",
        "stack": "llama.cpp / llama-server, any OS",
        "symptom": (
            "You concatenated a multi-part GGUF (name-00001-of-00002.gguf + "
            "name-00002-of-00002.gguf) into a single file to keep things tidy. "
            "llama-server now refuses to load it."
        ),
        "cause": (
            "A split GGUF stores split.count = N in its header. Concatenating the "
            "parts gives you the bytes of both files but the header still claims the "
            "model is split, so the loader goes looking for a second shard that is no "
            "longer there. The byte count is right; the metadata is lying."
        ),
        "fix": [
            "Do not concatenate. Delete the merged file and keep the original shards.",
            "Point -m at the first shard only: <code>-m model-00001-of-00002.gguf</code>.",
            "Keep every shard in the same directory with its original filename. The loader resolves the rest from split.no / split.count.",
        ],
        "verify": (
            "Reproduced with Qwen2.5-7B-Instruct Q4_K_M split into two files "
            "(3,993,201,344 + 689,872,288 = 4,683,073,632 bytes). The merged file fails; "
            "pointing -m at shard 1 loads normally and reports the full parameter count."
        ),
        "tags": ["llama.cpp", "gguf"],
    },
    {
        "slug": "codex-wire-api-chat-not-supported",
        "title": 'Codex: `wire_api = "chat"` is no longer supported',
        "err": '`wire_api = "chat"` is no longer supported',
        "stack": "OpenAI Codex CLI 0.170.0+, custom provider in ~/.codex/config.toml",
        "symptom": (
            "You pointed Codex at a local or third-party OpenAI-compatible endpoint with "
            'wire_api = "chat" and it refuses to start.'
        ),
        "cause": (
            "Codex 0.170 dropped the Chat Completions wire protocol for custom providers. "
            "Only the Responses API is accepted now. Most local servers (llama.cpp, LM Studio, "
            "vLLM, LiteLLM) expose both, so this is usually a one-line config change."
        ),
        "fix": [
            "In <code>~/.codex/config.toml</code>, set <code>wire_api = \"responses\"</code> under your provider block.",
            "Do not name the provider <code>openai</code>. That id is reserved and a custom block with it fails to parse with <code>config could not be loaded</code>.",
            "For a purely local model you can skip the provider entirely and use <code>codex --oss --local-provider ollama</code> (or <code>lmstudio</code>).",
        ],
        "verify": (
            "Verified against Codex 0.170.0 with a LiteLLM proxy exposing /v1/responses. "
            "Config parses, doctor passes, and a real task completes end to end."
        ),
        "tags": ["codex", "config"],
    },
    {
        "slug": "mihomo-invalid-find-process-mode",
        "title": "mihomo / OpenClash: Parse config error: invalid find process mode",
        "err": 'level=fatal msg="Parse config error: invalid find process mode"',
        "stack": "OpenClash 0.47.x + mihomo on OpenWrt",
        "symptom": (
            "You added find-process-mode to your YAML to quieten process matching, and the "
            "core now dies at startup. The config passes a standalone `-t` test but the "
            "service will not come up."
        ),
        "cause": (
            "OpenClash rewrites your config into a runtime file and injects its own "
            "find-process-mode. Your key plus its key means a duplicate mapping key, and "
            "mihomo rejects the document. A standalone `clash_meta -t -f your.yaml` passes "
            "because it never goes through OpenClash's rewrite step."
        ),
        "fix": [
            "Remove find-process-mode from your source config entirely.",
            "Let OpenClash own it. If you need a specific value, patch the generated file from <code>/etc/openclash/custom/openclash_custom_overwrite.sh</code> instead of the source.",
            "Restart with <code>touch /etc/config/openclash &amp;&amp; uci set openclash.config.restart=1 &amp;&amp; uci commit openclash</code>, otherwise OpenClash takes the Quick Start path and generates an empty config.",
        ],
        "verify": (
            "Reproduced on LibWrt (OpenWrt snapshot, aarch64) with mihomo alpha-gbc76c13. "
            "Removing the key restores startup; the same key in the custom overwrite script works."
        ),
        "tags": ["openwrt", "mihomo", "openclash"],
    },
    {
        "slug": "litellm-context-window-exceeded",
        "title": "LiteLLM: request exceeds the available context size",
        "err": "litellm.ContextWindowExceededError: This model's maximum context length is 8192 tokens. However, your messages resulted in 20926 tokens",
        "stack": "LiteLLM proxy in front of llama-server / LM Studio",
        "symptom": (
            "A coding agent works fine on hosted APIs but dies immediately against your local "
            "stack with a context-length error, even though the model supports far more."
        ),
        "cause": (
            "The agent's system prompt alone is large. Claude Code ships roughly 21K tokens of "
            "tools and instructions before your first message. llama-server defaults to a small "
            "-c value, so the request is rejected at the proxy layer before the model sees it."
        ),
        "fix": [
            "Start llama-server with a context that covers the prompt: <code>-c 32768</code> or higher.",
            "Budget VRAM for it. KV cache grows linearly with -c; on a 12 GB card a 7B Q4_K_M model at 32K context fits comfortably, at 128K it does not.",
            "If VRAM is tight, reduce the agent's context rather than the server's: the failure is about total prompt size, not output length.",
        ],
        "verify": (
            "Measured on an RX 6700 XT 12 GB with Qwen2.5-Coder-7B Q4_K_M. -c 8192 fails at "
            "20926 tokens; -c 32768 completes. Time to first token at 21K prompt on this GPU: "
            "about 383 s, because prefill degrades as the prompt grows."
        ),
        "tags": ["litellm", "llama.cpp", "claude-code"],
    },
    {
        "slug": "litellm-no-module-main",
        "title": "LiteLLM: No module named litellm.__main__",
        "err": "No module named litellm.__main__; 'litellm' is a package and cannot be directly executed",
        "stack": "Python 3.12, pip install litellm[proxy]",
        "symptom": "python -m litellm fails even though the package imports fine.",
        "cause": (
            "The package does not ship a __main__.py. The console entry point is installed "
            "separately as litellm.exe / litellm."
        ),
        "fix": [
            "Run the console script instead: <code>litellm --config config.yaml --port 4000</code>.",
            "On Windows with a per-user install it lives at <code>%LOCALAPPDATA%\\Programs\\Python\\Python312\\Scripts\\litellm.exe</code>.",
        ],
        "verify": "Verified with litellm 1.110.0 on Python 3.12.10 / Windows 11.",
        "tags": ["litellm", "python"],
    },
    {
        "slug": "pyyaml-gbk-unicode-decode-error",
        "title": "PyYAML: 'gbk' codec can't decode byte 0x94",
        "err": "UnicodeDecodeError: 'gbk' codec can't decode byte 0x94 in position 18: illegal multibyte sequence",
        "stack": "Python + PyYAML on a Chinese-locale Windows install",
        "symptom": (
            "A YAML config that loads fine on macOS or Linux throws a GBK decode error on "
            "Windows. The file looks like plain text."
        ),
        "cause": (
            "On a zh-CN system Python opens files with the ANSI code page (cp936 / GBK) unless "
            "told otherwise. A UTF-8 file containing non-ASCII characters - a Chinese comment, "
            "a curly quote, an emoji - is not valid GBK, so decoding fails at the first such byte."
        ),
        "fix": [
            "Keep machine-read config files pure ASCII. Comments included.",
            "If you control the loading code, pass <code>encoding=\"utf-8\"</code> explicitly.",
            "Do not \"fix\" it by saving as GBK - the next tool that reads it as UTF-8 will break instead.",
        ],
        "verify": (
            "Reproduced with a LiteLLM config.yaml containing a Chinese comment. Byte 0x94 at "
            "position 18 is the third byte of the first Chinese character. ASCII-only file loads."
        ),
        "tags": ["python", "yaml", "windows"],
    },
    {
        "slug": "mihomo-url-regex-unsupported",
        "title": "mihomo: unsupported rule type: URL-REGEX",
        "err": "parse classical rule [URL-REGEX,...] error: unsupported rule type: URL-REGEX",
        "stack": "mihomo (Clash.Meta) loading a Clash Premium style config",
        "symptom": "The core logs a rule parse error and the rule is silently dropped.",
        "cause": (
            "URL-REGEX is a Clash Premium rule type. mihomo does not implement it. Configs "
            "copied from subscription providers often contain it."
        ),
        "fix": [
            "Replace with <code>DOMAIN-REGEX</code> (same syntax, matches the host) or <code>DOMAIN-KEYWORD</code>.",
            "If you only care about a whole category, <code>GEOSITE</code> is cheaper than a regex.",
        ],
        "verify": "Verified on mihomo alpha-gbc76c13 (linux/arm64). Swapping to DOMAIN-REGEX parses cleanly.",
        "tags": ["mihomo", "openwrt"],
    },
    {
        "slug": "mihomo-dns-resolve-failed-deadline",
        "title": "mihomo: dns resolve failed: context deadline exceeded",
        "err": "dns resolve failed: context deadline exceeded",
        "stack": "mihomo / OpenClash with DNS-over-HTTPS upstreams",
        "symptom": (
            "Every proxy shows as dead on a latency test, and the log fills with DNS timeouts, "
            "even though the nodes work in another client."
        ),
        "cause": (
            "A chicken-and-egg loop. nameserver points at DoH endpoints such as "
            "https://1.1.1.1/dns-query. Resolving those requires the proxy. The proxy requires "
            "DNS to resolve node hostnames. Nothing ever resolves."
        ),
        "fix": [
            "Give the proxy its own plaintext resolver: <code>proxy-server-nameserver: [223.5.5.5, 119.29.29.29]</code>.",
            "Set default-nameserver to plaintext IPs as well - it is the bootstrap for everything else.",
            "DoH can stay in nameserver for client queries once bootstrap no longer depends on it.",
        ],
        "verify": (
            "Reproduced with a 2000-node config: 0 alive out of 2121 before the change, "
            "44 alive after. Fix is three lines of YAML."
        ),
        "tags": ["mihomo", "dns"],
    },
    {
        "slug": "powershell-missing-equals-operator",
        "title": "PowerShell: Missing '=' operator after key in hash literal",
        "err": "Missing '=' operator after key in hash literal.",
        "stack": "Windows PowerShell 5.1 running a .ps1 file",
        "symptom": (
            "A script that runs on another machine produces a wall of parser errors pointing at "
            "lines that look correct."
        ),
        "cause": (
            "The .ps1 is UTF-8 without a BOM. PowerShell 5.1 reads script files using the "
            "system ANSI code page, so Chinese comments and string literals become mojibake, and "
            "the parser eventually hits a character sequence it cannot interpret. The reported "
            "line numbers are frequently wrong by several lines."
        ),
        "fix": [
            "Save the file as UTF-8 <b>with BOM</b>. In PowerShell: <code>[IO.File]::WriteAllText($p, $text, (New-Object System.Text.UTF8Encoding($true)))</code>.",
            "Or avoid non-ASCII entirely in .ps1 files.",
            "PowerShell 7 reads UTF-8 by default, so the problem is specific to 5.1.",
        ],
        "verify": "Reproduced on Windows 11 26200 with Windows PowerShell 5.1.1702. Adding the BOM removes all errors.",
        "tags": ["powershell", "windows", "encoding"],
    },
    {
        "slug": "powershell-writealltext-parameter-count-4",
        "title": "PowerShell: WriteAllText 的重载，参数计数为 4",
        "err": "找不到“WriteAllText”的重载，参数计数为“4”。",
        "stack": "Windows PowerShell 5.1",
        "symptom": "A one-line file write fails with an overload resolution error that counts four arguments.",
        "cause": (
            "<code>[IO.File]::WriteAllText($path, $text -replace 'a','b', $enc)</code> - the "
            "-replace operator binds looser than the comma, so PowerShell passes four arguments "
            "to a three-parameter method."
        ),
        "fix": [
            "Parenthesise the expression: <code>[IO.File]::WriteAllText($path, ($text -replace 'a','b'), $enc)</code>.",
            "The same trap applies to <code>$i:</code> inside a double-quoted string - it is parsed as a drive qualifier. Use <code>${i}</code>.",
        ],
        "verify": "Verified on PS 5.1; the parenthesised form compiles and writes the expected bytes.",
        "tags": ["powershell", "windows"],
    },
    {
        "slug": "python-win32-globallock-access-violation",
        "title": "ctypes: OSError access violation writing 0x0 when setting the clipboard",
        "err": "OSError: exception: access violation writing 0x0",
        "stack": "Python ctypes + Win32 clipboard API on 64-bit Windows",
        "symptom": (
            "Your GlobalAlloc / GlobalLock / memmove clipboard helper works in 32-bit Python and "
            "crashes in 64-bit, or crashes only sometimes."
        ),
        "cause": (
            "ctypes assumes c_int for an undeclared restype. On 64-bit Windows an HGLOBAL is a "
            "pointer, so the handle is truncated to 32 bits. memmove then writes to a bogus address."
        ),
        "fix": [
            "<code>kernel32.GlobalAlloc.restype = ctypes.c_void_p</code>",
            "<code>kernel32.GlobalLock.restype = ctypes.c_void_p</code> and <code>kernel32.GlobalLock.argtypes = [ctypes.c_void_p]</code>",
            "<code>ctypes.memmove(ptr, text.encode('utf-16-le') + b'\\x00\\x00', len(encoded))</code>, then SetClipboardData(CF_UNICODETEXT, handle).",
        ],
        "verify": (
            "Verified on Python 3.12.10 / Windows 11 x64. Without the declarations the call "
            "raises OverflowError or access violation; with them the clipboard holds correct "
            "UTF-16 including CJK characters."
        ),
        "tags": ["python", "ctypes", "windows"],
    },
    {
        "slug": "albion-api-throttled-use-compression",
        "title": "Albion Online Data API: Throttled, be nice to the server, use compression",
        "err": "Throttled, be nice to the server, use compression",
        "stack": "albion-online-data.com public API",
        "symptom": "Price queries start returning 429 with that body even at a modest request rate.",
        "cause": (
            "The API requires compressed responses. Requests without Accept-Encoding: gzip are "
            "counted as abusive regardless of how few you send."
        ),
        "fix": [
            "curl: add <code>--compressed</code>.",
            "Python urllib: send <code>Accept-Encoding: gzip</code> and <code>gzip.decompress()</code> the body.",
            "Batch item ids into one request (up to 100 comma-separated) instead of looping.",
        ],
        "verify": "Verified against east/europe servers; without the header even a single request is throttled.",
        "tags": ["api", "python"],
    },
    {
        "slug": "urllib-incompleteread-github-api",
        "title": "Python urllib: IncompleteRead on large GitHub API responses",
        "err": "http.client.IncompleteRead: IncompleteRead(1234567 bytes read, 89012 more expected)",
        "stack": "Python urllib.request against api.github.com",
        "symptom": "Small API calls work; endpoints returning megabytes fail intermittently.",
        "cause": (
            "urllib's HTTP client is brittle with chunked, compressed multi-megabyte responses. "
            "The connection closes early and the read raises rather than retrying."
        ),
        "fix": [
            "Shell out to <code>curl.exe -sS --compressed</code> and parse its stdout.",
            "Or use requests / httpx, which handle chunked transfer properly.",
            "If you must stay on urllib, retry with Range and assemble the body yourself - usually not worth it.",
        ],
        "verify": "Verified against a 17 MB GitHub Contents API response; curl succeeds where urllib raises.",
        "tags": ["python", "api"],
    },
    {
        "slug": "python-textiowrapper-closed-file",
        "title": "Python: I/O operation on closed file after re-wrapping sys.stdout",
        "err": "ValueError: I/O operation on closed file",
        "stack": "Python on Windows with a legacy console code page",
        "symptom": (
            "You wrap sys.stdout twice to force UTF-8 output and later print fails, or the "
            "failure only appears when output is piped."
        ),
        "cause": (
            "Assigning sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...) a second time drops "
            "the last reference to the first wrapper. When that object is collected it closes the "
            "underlying buffer, which the new wrapper is still using."
        ),
        "fix": [
            "Use <code>sys.stdout.reconfigure(encoding=\"utf-8\", errors=\"replace\")</code> - no new object, no close.",
            "Set <code>PYTHONIOENCODING=utf-8</code> in the environment instead of touching sys.stdout at all.",
        ],
        "verify": "Verified on Python 3.12.10 / Windows 11 zh-CN. reconfigure() prints CJK and emoji without error.",
        "tags": ["python", "windows", "encoding"],
    },
]

BENCH_NOTES = [
    ("Qwen2.5-Coder-7B-Instruct, Q4_K_M, RX 6700 XT 12 GB, Vulkan backend", [
        ("Prefill, default batch sizes", "52 tok/s"),
        ("Prefill after -b 4096 -ub 1024", "234.6 tok/s"),
        ("Generation, -t 8", "32.3 tok/s"),
        ("Generation, -t 12", "slower - CPU contention"),
        ("Generation with --cache-type-k q8_0", "4.4 tok/s"),
        ("Model load (cold)", "about 16 s"),
    ]),
    ("Prefill decay on a 21K-token prompt (same hardware)", [
        ("first 4K tokens", "384 tok/s"),
        ("8K", "166 tok/s"),
        ("12K", "106 tok/s"),
        ("16K", "78 tok/s"),
        ("20K", "61 tok/s"),
        ("total time to first token", "about 383 s"),
    ]),
]

NOTES = [
    {
        "slug": "kv-cache-quantization-on-vulkan",
        "title": "Do not enable KV cache quantization on the Vulkan backend",
        "body": [
            "Setting --cache-type-k q8_0 --cache-type-v q8_0 on llama.cpp with the Vulkan backend "
            "does not fail. It silently destroys throughput: generation went from 40 tok/s to "
            "4.4 tok/s on a 7B Q4_K_M model.",
            "The dequantisation path is not implemented for Vulkan, so the KV cache is converted "
            "on the CPU per token. On a discrete GPU that is slower than just keeping the cache in f16.",
            "Check with a one-line benchmark before committing to it. On CUDA the same flags are "
            "usually a straight win.",
        ],
        "tags": ["llama.cpp", "vulkan"],
    },
    {
        "slug": "prefill-is-not-linear",
        "title": "Prefill time is quadratic, and it dominates agent workloads",
        "body": [
            "Generation speed is what everyone benchmarks, but for coding agents the cost is in prefill. "
            "A 21K-token system prompt took 383 seconds to process on a mid-range GPU, while the "
            "answer itself took a few seconds.",
            "Measured in 4K windows on the same machine: 384 tok/s for the first window, 61 tok/s for "
            "the fifth. The average is not the number you experience - the tail is.",
            "Practical consequences: keep the agent's tool definitions small, cache the system prompt "
            "if your server supports prompt caching, and do not assume a bigger context window is free.",
        ],
        "tags": ["llama.cpp", "benchmark"],
    },
]

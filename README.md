# guns.lol view bot

become an egangster and mass inflate your guns.lol profile views to attract ekittens. because nothing screams "i'm dangerous" like a suspiciously high view count.

## what it does

solves guns.lol's proof-of-work challenge in pure python (reversed their wasm solver), solves cloudflare turnstile, and sends view requests through rotating proxies. no untrusted code execution. fully automated.

## requirements

- python 3.10+
- ~~node.js~~ not needed anymore. if the reverse gets patched, check the sandboxed version in commit history
- rotating or sticky proxy with a big pool
- [uncaptcha.io](https://uncaptcha.io/) api key

## setup

```bash
git clone https://github.com/notemrovsky/guns-lol-view-bot.git
cd guns-lol-view-bot
pip install blake3 curl-cffi requests
```

## config

create `config.json` in the root directory:

```json
{
    "username": "target_username",
    "proxy": "http://user:pass@host:port",
    "threads": 10,
    "views": 1000,
    "sleep": 0.1,
    "uncaptcha_key": "your-api-key-here"
}
```

| field | description |
|-------|-------------|
| `username` | the guns.lol profile you want to inflate |
| `proxy` | proxy url. for rotating proxies just use the url directly. for session-based proxies put `{s}` where the session id goes and it'll be randomized per session (e.g. `http://user:pass_session-{s}@host:port`) |
| `threads` | how many concurrent workers |
| `views` | total views to send |
| `sleep` | delay in seconds between launching each thread. if you send views too fast they get removed, so adding some delay here helps them actually stick |
| `uncaptcha_key` | your uncaptcha.io api key |

## getting an uncaptcha api key

1. go to [uncaptcha.io](https://uncaptcha.io/) and create an account
2. top up your balance ($1 per 1k solves)
3. go to dashboard and copy your api key
4. paste it in `config.json` under `uncaptcha_key`

## usage

```bash
python3 main.py
```


## how it works

guns.lol uses a wasm-based proof-of-work system to protect view counting. the server sends a challenge token containing a 59-char hex target (64-char seal with 5 nibbles removed at known positions). the client needs to find those 5 missing nibbles where `sha256(seal + salt + timestamp)` equals the challenge hash.

the original wasm iterates a counter and xor-encodes it, we just solve the 5 nibbles directly. the nonce includes a blake3 integrity check and a score computed from `blake3(seal)` vs `blake3(challenge_hash_bytes + salt + timestamp)`. the analytics endpoint is protected by both cloudflare turnstile and the pow.

## the funny part

guns.lol devs are actually pretty clever, they count views through a tiny analytics gif request instead of a regular api call. smart move. except they also put `simple-analytics-feedback: Thanks for sending this page view!` in the response headers. thanks for the confirmation i guess?

![request](assets/sa_request.png)
![response](assets/sa_response.png)

## heads up

views take around 3 to 5 minutes to show up on the profile. go touch grass, get some water, maybe even talk to a real person while you wait.

also dont get greedy, if you send a massive amount at once they remove almost half of them. do small batches, your ereputation is a marathon not a sprint.

## disclaimer

this is for educational purposes only. i am not responsible for what you do with this. if guns.lol patches their pow and your ekittens leave you, that's on you.

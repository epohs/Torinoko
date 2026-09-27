# Example configuration files for deploying Torinoko

These are the files Torinoko runs with in production, with the specifics swapped for placeholders. Copy them out of the project, replace `YOURUSERNAME`, `/path/to/Torinoko` and `secret.your-domain.com`, and install them where they belong.

Before you start, set `DEVELOPMENT` and `DEBUG` to `False` in `config.py` and give it a real `SECRET_KEY`. Torinoko refuses to start on the sample key.

> **IMPORTANT:** Don't run Torinoko publicly without the nginx config below. Its slugs are short on purpose, and the rate limit in nginx is what keeps them from being guessed.




## Why security lives in nginx

Torinoko stays small by leaving some jobs to the web server in front of it.

- **Rate limiting.** A 5 character slug is only safe if it can't be guessed quickly. nginx counts requests for every Gunicorn worker at once. A limiter inside the app would count each worker separately.
- **TLS and HSTS.** nginx terminates TLS, so it's the only layer that knows how a visitor connected.
- **Security headers.** Set in one place, alongside TLS, instead of in the app. Pick one place for them: nginx adds its headers next to the app's, and duplicates conflict.

What only the app knows, the app handles: `Cache-Control: no-store` on the page showing a decrypted note, the `Secure` session cookie, and CSRF checks on every form.




## [torinoko.service](./torinoko.service.example)

### systemd Service

Runs Torinoko under Gunicorn on a unix socket that nginx connects to. `--preload` sets up the database once, before the workers start. The socket is only reachable by your user and the `www-data` group.

```
sudo cp deploy/torinoko.service.example /etc/systemd/system/torinoko.service
sudo systemctl enable --now torinoko
```




## [nginx.conf](./nginx.conf.example)

### nginx Site

Terminates TLS, sets the security headers, and rate limits `/secret/`, `/note/` and `/new`: 10 quick requests, then one every 3 seconds per visitor. That's plenty for creating and reading notes, and slow enough that guessing slugs goes nowhere.

```
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/torinoko
sudo ln -s /etc/nginx/sites-available/torinoko /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```




## [cloudflare-realip](./cloudflare-realip.example)

### Running Behind Cloudflare

Only needed if Cloudflare proxies your site. Two things matter:

**nginx has to see real visitors.** Behind Cloudflare, every request arrives from a Cloudflare server, so the rate limit would lump unrelated visitors together. Copy this file to `/etc/nginx/cloudflare-realip` and uncomment its `include` in the nginx config. Cloudflare changes its ranges occasionally, so check the list now and then.

**Set Cloudflare's SSL mode to Full (strict).** In Flexible mode the connection from Cloudflare to your server is plain HTTP. Decrypted notes cross the internet unencrypted, and share URLs come out as `http://`. A rule scoped to your Torinoko hostname is enough.




## Updating

```
git pull --ff-only
uv sync --locked
sudo systemctl restart torinoko
```

# sportyhq_custom_component
A Home Assistant Custom Component for summary data from SportyHQ.

Provides sensors for your SportyHQ rating, rating confidence, matches YTD, and matches all-time.

## Why a session cookie instead of username/password?

SportyHQ's login page is protected by Cloudflare Bot Management and reCAPTCHA, which block automated credential-based logins. Authentication is instead handled by injecting a real browser session cookie.

## Installation

1. Copy the `sportyhq` folder into your `<config>/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **SportyHQ**.

## Getting your session cookie

1. Open Chrome or Firefox and log in to [sportyhq.com](https://www.sportyhq.com) — make sure to tick **Remember me**.
2. Open DevTools:
   - **Chrome**: F12 → **Application** tab → **Cookies** → `https://www.sportyhq.com`
   - **Firefox**: F12 → **Storage** tab → **Cookies** → `https://www.sportyhq.com`
3. Find the cookie named **`sportyhq_v10`** and copy its **Value**.
4. Paste that value into the **Session Cookie** field when prompted by the integration setup.

## Refreshing an expired cookie

If sensors stop updating, the cookie has likely expired. Go to **Settings → Devices & Services → SportyHQ → Configure** to paste a fresh cookie value. With "Remember me" ticked the cookie typically stays valid for several weeks.

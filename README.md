# Ultimate Discord Server Joiner / Discord Token Filler

## Folder Structure

### `input/` folder
Contains all input files:
- `tokens.txt` - List of Discord tokens
- `invites.txt` - List of Discord invites to join 
- `proxies.txt` - List of residential proxies
  - Auth format: `user:pass@ip:port`
  - No-auth format: `ip:port`

### `output/` folder
Contains all output files:
- `invitesdone.txt` - Successful invites
- `invitesfailed.txt` - Failed invites
- `invitesbackup.txt` - Invite backup at startup
- `tokenscaptcha.txt` - Banned tokens (too many captchas)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Put your tokens in `input/tokens.txt`
2. Put your invites in `input/invites.txt`
3. (Optional) Put your proxies in `input/proxies.txt`
4. Run the script: `python main.py`
5. Enter the number of threads you want

## Features

- Automatic thread handling with reallocation
- Residential proxy support
- Captcha detection and handling
- Automatic token ban after too many captchas
- Real-time stats in the console title
- Windows terminal colors (via `colorama`)
- Organized input/output file structure
- Bypass Verifications (Onboarding,Restorecord,rules)

## Configuration

All settings are configurable in `config.json`:

```json
{
    "max_captcha_before_ban": 3,
    "delay_between_joins_min": 45,
    "delay_between_joins_max": 75,
    "use_proxy": true,
    "proxy_rotation": true,
    "retry_on_failure": true,
    "max_retries": 3,
    "bypass_onboarding": true,
    "bypass_rules": true,
    "bypass_restorecord": false,
    "timeout": 30,
    "user_agent": "Mozilla/5.0..."
}
```

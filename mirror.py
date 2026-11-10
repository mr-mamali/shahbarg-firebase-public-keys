"""Mirror only release-signed public keys; never handle Firebase user tokens."""
import datetime as dt
import base64
import json
import pathlib
import subprocess
import tempfile
import urllib.request

SOURCE = 'https://mark-game-ceb93c.gitlab.io/firebase-signing-keys.json'
DEST = pathlib.Path('firebase-signing-keys.json')
with urllib.request.urlopen(SOURCE, timeout=30) as response:
    raw = response.read(65537)
if len(raw) > 65536:
    raise RuntimeError('Public envelope is too large')
envelope = json.loads(raw)
bundle = envelope['bundle']
signature = envelope['signature']
if not isinstance(bundle, str) or not isinstance(signature, str):
    raise RuntimeError('Invalid public envelope')
with tempfile.TemporaryDirectory() as directory:
    signature_file = pathlib.Path(directory) / 'keys.sig'
    signature_file.write_bytes(base64.b64decode(signature, validate=True))
    subprocess.run(['ssh-keygen', '-Y', 'verify', '-f', 'allowed-signers',
                    '-I', 'shahbarg-ci', '-n', 'shahbarg-firebase-keys-v1',
                    '-s', str(signature_file)], input=bundle.encode(),
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
body = json.loads(bundle)
fetched = dt.datetime.fromisoformat(body['fetched_at'])
expires = dt.datetime.fromisoformat(body['expires_at'])
now = dt.datetime.now(dt.timezone.utc)
if not fetched <= now + dt.timedelta(seconds=30) or not fetched < expires <= fetched + dt.timedelta(hours=6) or expires <= now:
    raise RuntimeError('Public key bundle is expired or has invalid dates')
if DEST.exists():
    old = json.loads(json.loads(DEST.read_text())['bundle'])
    if dt.datetime.fromisoformat(old['fetched_at']) >= fetched:
        print('Public mirror already has this update or a newer one')
        raise SystemExit(0)
DEST.write_bytes(raw)
print(f'Mirrored signed public keys expiring {expires.isoformat()}')

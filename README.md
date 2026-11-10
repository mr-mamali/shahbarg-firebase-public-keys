# Shahbarg Firebase public signing keys

This repository mirrors only Google's public signing keys and their release signature.
No user ID tokens, user data, API credentials or private keys are stored here.

The game independently verifies the original pinned SSH publisher signature,
Google's original expiry (maximum six hours), and monotonic update time.
This transport cannot forge a trusted signing-key update.

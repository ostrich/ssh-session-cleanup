# ssh-session-cleanup

Disconnect OpenSSH sessions before networking stops during systemd shutdown,
so clients don't hang waiting for a TCP timeout.

## Install on Arch Linux

```sh
cd arch
makepkg -si
sudo systemctl enable --now ssh-session-cleanup.service
```

Starting the service arms the shutdown hook without disconnecting anyone.
Cleanup runs at shutdown or reboot; manual stop/restart is refused.
To disable it for future boots:

```sh
sudo systemctl disable ssh-session-cleanup.service
```

The currently armed hook still runs at the next shutdown.

## How it works

Sends SIGTERM to authenticated OpenSSH connections, including terminals, remote
commands, file transfers and forwarding. Uses Linux pidfds to avoid PID reuse
races and waits up to five seconds; never sends SIGKILL.

Requires Linux with pidfds, Python 3.9+, systemd and root access. Ordering is
configured for Arch's `sshd.service` and `sshd.socket`; other unit names need a
local drop-in. Network teardown must honor `network.target`.

## Inspect and test

List matching sessions without disconnecting them:

```sh
sudo ./ssh-session-cleanup --dry-run
```

Run tests (no reboot or live SSH disconnection):

```sh
python -m unittest discover -s tests -v
```

Licensed under [GPL-3.0-or-later](LICENSE).

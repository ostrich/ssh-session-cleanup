import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import os
import unittest
from unittest.mock import patch


loader = importlib.machinery.SourceFileLoader("cleanup", str(Path(__file__).resolve().parents[1] / "ssh-session-cleanup"))
spec = importlib.util.spec_from_loader(loader.name, loader)
cleanup = importlib.util.module_from_spec(spec)
loader.exec_module(cleanup)


class CleanupTests(unittest.TestCase):
    def test_authenticated_sessions(self):
        for binary in ("sshd", "sshd-session"):
            for terminal in ("pts/12", "notty"):
                with self.subTest(binary=binary, terminal=terminal):
                    self.assertTrue(cleanup.is_session(f"/usr/lib/ssh/{binary}", f"{binary}: alice@{terminal}\0\0".encode()))
        self.assertTrue(cleanup.is_session("/usr/bin/sshd (deleted)", b"sshd: root@pts/0\0"))

    def test_forwarding_only_connections(self):
        for binary in ("sshd", "sshd-session"):
            with self.subTest(binary=binary):
                self.assertTrue(cleanup.is_session(f"/usr/lib/ssh/{binary}", f"{binary}: alice\0".encode()))

    def test_multiplexed_terminals(self):
        for binary in ("sshd", "sshd-session"):
            with self.subTest(binary=binary):
                self.assertTrue(cleanup.is_session(f"/usr/lib/ssh/{binary}", f"{binary}: alice@pts/0,pts/12\0".encode()))

    def test_excludes_listeners_authentication_and_impostors(self):
        for title in (b"sshd: /usr/bin/sshd -D [listener]", b"sshd-session: alice [priv]",
                      b"sshd-session: alice [postauth]", b"sshd: alice [net]",
                      b"bash\0sshd: alice@pts/0", b"sshd: alice@pts/0 trailing",
                      b"sshd-session: [accepted]", b"sshd-session: [rexeced]",
                      b"sshd-session: alice@", b"sshd-session: alice@pts/0,",
                      b"sshd-session: alice@pts/0,garbage", b"sshd-session: "):
            self.assertFalse(cleanup.is_session("/usr/bin/sshd", title))
        self.assertFalse(cleanup.is_session("/usr/bin/bash", b"sshd: alice@pts/0"))

    def run_child(self, dry_run):
        child = subprocess.Popen(["sleep", "30"])
        fd = os.pidfd_open(child.pid)
        try:
            with patch.object(cleanup, "sessions", return_value=iter([(child.pid, fd)])):
                cleanup.cleanup(dry_run=dry_run, timeout=1)
            if dry_run:
                self.assertIsNone(child.poll())
            else:
                self.assertEqual(child.wait(timeout=1), -15)
        finally:
            os.close(fd)
            if child.poll() is None:
                child.terminate()
            child.wait()

    def test_pidfd_signal_and_wait(self):
        self.run_child(False)

    def test_dry_run_does_not_signal(self):
        self.run_child(True)


if __name__ == "__main__":
    unittest.main()

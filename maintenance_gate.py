"""Cross-process advisory recording gate shared with the VPS updater.

Every recording worker holds a shared flock from before FFprobe starts until
FFmpeg is reaped. The updater holds an exclusive flock during Docker recreation.
A failed lock attempt must never be interpreted as permission to record.
"""

import fcntl
import os
from pathlib import Path

DEFAULT_LOCK_PATH = Path(os.environ.get("IRR_MAINTENANCE_LOCK", "/config/.irr-maintenance.lock"))
RECORDING_GATE_VERSION = "flock-v1"


def acquire_shared(path=DEFAULT_LOCK_PATH):
    """Return an owned fd, or None if maintenance has the exclusive lock.

    Creates an empty persistent lock file (mode 0644 with a normal umask).
    The VPS updater opens this inode read-only, including when root owns it.
    Never unlink/replace the file: Linux flock locks inode, not pathname.
    """
    fd = os.open(os.fspath(path), os.O_RDONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    except BaseException:
        os.close(fd)
        raise
    return fd


def release_shared(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)

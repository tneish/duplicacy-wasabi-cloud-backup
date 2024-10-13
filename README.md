# duplicacy-wasabi-cloud-backup

Read the [`HOWTO`](https://github.com/tneish/duplicacy-wasabi-cloud-backup/blob/master/HOWTO.md) to get started.

Edit configuration options in the `Config` class in the `duplicacybackupconfig.py` file, then let systemd periodically run the script by copying .timer and .service files to `/etc/systemd/system`, run `systemctl daemon-reload`, then `systemctl enable` and `systemctl start` on the timer.

`filesFromChunks.py` is useful if you need to restore a backup with missing chunks.

# duplicacy-wasabi-cloud-backup

Read the [`HOWTO`](https://github.com/tneish/duplicacy-wasabi-cloud-backup/blob/master/HOWTO.md) to get started.

Edit configuration options in the `Config` class in the `duplicacybackupconfig.py` file, then either copy them to `/etc/cron.daily` or for systemd, copy .timer and .service files to `/etc/systemd/system`, run `systemctl daemon-reload`, then `systemctl enable` and `systemctl start` on the timer.

`filesFromChunks.py` is useful if you need to restore a backup with missing chunks.

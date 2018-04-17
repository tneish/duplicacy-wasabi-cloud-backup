# Cloud storage backup life-cycle

Assuming you already have some local storage solution setup. In this case we are assuming it is a linux server of some sort, with access to the internet.

The life-cycle is, 

1. First some once-off steps:

    1. Create wasabi account, storage bucket (give it a name), and access keys (save these for later)

    2. Download duplicacy binary to your linux server, so it is accessible from `$PATH` (for convenience). 

    3. Create a safe place to store key information for when your local storage has crashed and you need to restore from the cloud backup. E.g. A good password manager database like KeePass, *stored somewhere else*.

    4. Initialize duplicacy repository by running a command on local linux server towards remote wasabi backend.

    5. Run first backup. This might take a long time, and must complete before any subsequent backups are run (e.g. via cron job) so you should do this once-off manually and not via your cron job.

2. Then periodically (e.g. cron job):

    1. Run backups (create snapshots) to capture changes to local storage.

    2. Check backups to see if all the expected chunks can be seen on cloud storage.
        The cloud may have lost them or you might have accidently deleted them by running prune and backup at the same time towards the same cloud storage (best not to do that).

        Note: This will catch deletion of a whole chunk from cloud storage, but not "bit rot", i.e. corruption of chunk contents.  See section “Catching bit rot”.

    3. Prune backups (delete old snapshots [& old chunks] from cloud storage) to save cloud storage costs in case you delete/modify files locally.

    Please see the [duplicacy-backup](https://github.com/tneish/duplicacy-wasabi-cloud-backup/blob/master/duplicacy-backup) script in this repository for an example of a cron script that can be used.

3. Fix errors that happen now and again. 
Sometimes the backup or check, or prune might halt with an error.  First you have to know about it, then act straight away. This means email/SMS notification.  Timing is of the essence, because backup problems are easier to fix if you still have a local copy of the data.  If you don’t have a local copy (e.g. your local storage crashes before you fix the cloud storage problem), then your backup problem with a local copy becomes a restore problem with an inconsistent/incomplete copy which is much harder to solve, and you probably permanently lost data.

# Safe keeping, in case of restore.

If your local storage crashes you will need the following information to restore from the cloud backup. Store it all in a good password manager like KeePass, but store the KeePass database file *somewhere else*!

1. S3 url, 
e.g. `s3://us-east-1@s3.wasabisys.com/<bucket name>`

2. Repository name.  
Can be seen in Wasabi web portal as a filename if you know the bucket name.

3. S3 ID. 
Can be seen in Wasabi web portal, if you know which Wasabi access key you used.

4. (secret) S3 secret.  
You got this when you created the access key in Wasabi, but only you have this now, you can’t recover it from Wasabi later.

5. (secret) storage password.  
Only you have this.   

6. (optional, but ideally) Duplicacy version used to create the backup 
In-case there are backwards compatibility problems in future.

# Initialize a repository

Make sure duplicacy binary is in your PATH environment variable:

```
user@linuxserver:/path/to/local/storage$ which duplicacy
/usr/local/bin/duplicacy
```

Run init command

`user@linuxserver:/path/to/local/storage$ duplicacy init -e <repository name, unique for cloud storage bucket> s3://us-east-1@s3.wasabisys.com/<bucket name>`

You want the backup to be encrypted on Wasabi, so add "-e" and supply a storage password. Typically the storage password is kept the same for the life of the cloud storage, so autogenerate a long complicated one with help from a good password manager like KeePass.

You will also need to supply the init command with the s3_id, and s3_secret you got from creating access keys in Wasabi.

These three things, together with the s3 url, respository name, and bucket name need to be kept in a safe place for some future nightmare when you are desperately trying to restore (see section "safe keeping, in case of restore").

If you are automating the backup (e.g. with a cron job), you don’t want an interactive prompt asking for s3 ID, s3 secret, and storage password each time.

The (easiest) option is to store the passwords in the `.duplicacy/preferences` file. Add them, like this:

```
duplicacy set -key s3_id -value <s3 id you got from wasabi access key>
duplicacy set -key s3_secret -value <s3 secret you got from wasabi access key>
duplicacy set -key password -value <your own storage password>
```

The file is created with restrictive permissions, so it is only read and writable for the user that created it:

```
user@linuxserver:/path/to/local/storage$ ls -al .duplicacy/preferences
-rw------- 1 user user 442 Mar 27 09:22 .duplicacy/preferences
```

Duplicacy can also get keys from a gpg keyring, but if run from cron the keyring has to be unlocked all the time, so I think storing in the preferences file is just as good.

# First Backup

Read this whole section first before you start the backup.

```
user@linuxserver:/path/to/local/storage$ duplicacy backup -stats -threads 10
Storage set to s3://us-east-1@s3.wasabisys.com/bucketname
No previous backup found
Indexing /path/to/local/storage
Listing all chunks
Uploaded chunk 1 size 1080867, 1.03MB/s 00:06:45 0.2%
Uploaded chunk 2 size 5411837, 1.24MB/s 00:05:33 1.4%
Uploaded chunk 3 size 3596049, 1.20MB/s 00:05:40 2.3%
…
```
Since it will run for a long time, you might want to run it in e.g. screen so that it does not terminate when you logout or lose connection to your ssh session.

It's useful to specify more than one thread to maximize uplink bandwidth. 10 threads worked for me on a 10Mbps uplink.

`user@linuxserver:/path/to/local/storage$ screen duplicacy backup -stats -threads 10`

To get it back later, e.g. in a different ssh session (for the same user), do `screen -r`  (-r for "reattach").

# Prune policy

When you run the backup command you create a snapshot.

Snapshots point to chunks, which are stored in the cloud.

If you delete a file locally and then do a backup (create a new snapshot, say #N), there’s a good chance the old snapshot (#N-1) references a chunk that snapshot #N does not.

If you want to keep cloud storage costs down, you could decide the deleted file does not need to be kept any longer on cloud storage. Either because you are already doing snapshots on your local storage (e.g. btrfs) or you just know you will never need the file again.

If you are running Wasabi backend though, you have already paid for 90 days storage so there is no extra cost to keeping the deleted file until it is 90 days old.

So, a snapshot that points to a chunk that is younger than 90 days does not have to be pruned.

If you are keeping local snapshots (e.g. btrfs) or don’t need to restore deleted/modified files older than 90 days you should do.

`duplicacy prune -keep 0:80`

"Keep 0 snapshots older than 80 days"

80 days are used to be on the safe side of billing, assuming you run prune and backup every day it gives 10 days margin.

This prune command will mark the chunks as "fossils" on the Wasabi backend without actually deleting them.  This is a safety measure in case another backup is running at the same time towards the same cloud storage. The other backup might reference the chunk you just deleted, otherwise.

Marking the chunks as "fossils" might start another 90 day billing period on Wasabi since you “touched” the chunk (Wasabi sees it as a “new” file). So perhaps you need to run:

`duplicacy prune -keep 0:89 -exclusive`

Adding `"-exclusive"` will immediately delete the chunk.  But you should be sure there are no other backups running towards the cloud storage at the same time (since they might reference the chunk you just permanently deleted).

# Restore with lost metadata

If your snapshot file, or one of your metadata chunks are lost from the cloud storage there does not seem to be a way to restore your data without first fixing the data from a known good copy. You don’t know in what sequence the chunks are, and you don’t know where files start and stop within a chunk. 

# Restore with lost chunks

You do `duplicacy cat -r <n>`, find the files that are in the lost chunks, then exclude them from the restore by doing `duplicacy restore -r <n> -- e:<filename 1> e:<filename 2> …`

There is a convenience script to get the list of filenames for you.  Please see [filesFromChunks.py](https://github.com/tneish/duplicacy-wasabi-cloud-backup/blob/master/filesFromChunks.py).

# Catching Bit Rot

Catching "bit rot" on cloud storage means downloading everything each time you want to check for bit rot, which is not practical to do for large archives over the internet.  Better to have local bit rot protection (e.g. btrfs or ZFS bit redundancy, possibly ECC memory, and periodic scrubbing) and a third offsite storage, e.g. periodically swapping USB hard-drives.

(ed note: Do any cloud storage providers claim bit-rot protection?)


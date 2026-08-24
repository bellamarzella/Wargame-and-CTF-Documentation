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
| Task | Solution 
| :--- | :--- |
| Find the flag | Use `gobuster` to enumerate the web server and discover a wordpress page, which details a `simple backup` plugin. Use `searchsploit` to find a public exploit for this plugin, and use `msfconsole` to exploit it and read the flag. |

### Section 6 - Privilege Escalation
| Task | Solution 
| :--- | :--- |
| Find `user2`'s flag | Use `sudo -l` to discover that we can run `/bin/bash` as `user2`. Use `sudo -u user2 /bin/bash` to spawn a shell as `user2`, and read the flag. | 
| Escalate to root and find the final flag | Use `ls -ld /root/.ssh/` to discover that `user2` has read access to the root user's `.ssh` directory. Use `cat /root/.ssh/id_rsa` to read the private key, and use it to SSH into the root account with `ssh -i id_rsa root@[ip]`, who can read the final flag. |
| Level | Command / Tool | Explanation |
| :--- | :--- | :--- |
| **0** | `ssh` | Connected to the remote OverTheWire server using specified credentials and port. |
| **0 → 1** | `cat`, `ls` | Located and read the standard `readme` text file in the home directory to find the flag. |
| **1 → 2** | `cat ./-` | Handled a dashed filename (`-`) by using relative pathing to stop terminal command interpretation. |
| **2 → 3** | `cat ./"file name"` | Handled spaces in a filename using quotes. |
| **3 → 4** | `ls -la` | Revealed hidden dotfiles (`.hidden`) by listing all files including hidden ones. |
| **4 → 5** | `file ./*` | Interrogated file types in the directory to isolate the only human-readable ASCII text file. |
| **5 → 6** | `find . -type f -size 1033c ! -executable` | Filtered directory to locate a file matching exact byte size, readability, and non-executable constraints. |
| **6 → 7** | `find / -user bandit7 -group bandit6 -size 33c 2>/dev/null` | Searched system for specific file matching precise user/group owners and byte size, ignoring permission errors. |
| **7 → 8** | `grep "millionth" data.txt` | Parsed a massive text file to locate the password string positioned next to the word 'millionth'. |
| **8 → 9** | `sort data.txt \| uniq -u` | Chained utilities together to sort text lines and isolate the only string occurring exactly once. |
| **9 → 10** | `strings data.txt \| grep "=="` | Extracted human-readable text from a binary file, filtering for the password preceded by '=' characters. |
| **10 → 11** | `base64 -d data.txt` | Decoded a text block containing base64-encoded data to reveal the cleartext password. |
| **11 → 12** | `tr 'A-Za-z' 'N-ZA-Mn-za-m'` | Decorrupted a text file by shifting alphabetic characters 13 positions using a ROT13 cipher bypass. |
| **12 → 13** | `xxd`, `gzip`, `bzip2`, `tar` | Reversed a hexdump back into binary, then repeatedly identified and decompressed nested archive formats (gzip, bzip2, tar) until reaching the final plaintext password. |
| **13 → 14** | `scp <key>`, `ssh <key>` | Copied the provided private SSH key from the remote server to the local machine using `scp`, then authenticated into the next level using the key instead of a password. |
| **14 → 15** | `nc localhost <port>` | Connected to the local service running on a specified port using netcat, then submitted the current level’s password to receive the next one. |
| **15 → 16** | `ncat --ssl localhost <port>` | Similar to level 14 → 15, `--ssl` automatically encrypts all inputs before transmitting, as required for this level. |
| **16 → 17** | `nmap -sV -p <port range> localhost` | Scanned localhost within specified port range for listening ports, identified only one that uses SSL and doesn't echo input, submitted password using an encrypted connection method, as seen in level 15 → 16. |
| **17 → 18** | `diff <old> <new>` | Found only line that differs between two files. |
| **18 → 19** | `ssh <address, port, username> "cat <filename>"` | Appended a quoted command to the SSH login string to execute it and return the output before the server forced an immediate logout. |
| **19 → 20** | `./<setuid> cat <password_directory>` | Ran a command through the provided setuid to access the file containing the password which we would otherwise not have permission to access. |
| **20 → 21** | `echo <password> \| nc -l -p <port>` | Bound a daemon to listen on an arbitrary port and echo a password when connected to, then used the setuid binary to communicate with this port. |
| **21 → 22** | `cat /etc/cron.d/*, cat <script>` | Analysed a cron configuration file and its target shell script to find the specific temporary file path where the next password was being copied. |
| **22 → 23** | `echo \| md5sum \| cut` | Analysed a cron script that dynamically generates its target password file path using an MD5 hash of the username, then replicated the hash calculation to locate the file in /tmp. |
| **23 → 24** | [script](\levels\bandit23\payload.sh) | Created a custom shell script payload, made it executable, and dropped it into a watched cron folder to trick a background daemon into copying the password to an open directory. |
| **24 → 25** | [script](\levels\bandit24\bruteForcer.sh) | Iterated 10,000 padded PIN variations through a single, continuous Netcat session to prevent connection throttling, filtering out failure messages using an inverted `grep` match to isolate the flag. |
| **25 → 26** | `more`, `v`, `:r <file>` | Inspected `/etc/passwd` to identify a custom text-viewing shell wrapper, shrank the terminal to force `more` command, exploited a quirk of `more` to pause, escaped into Vim and used internal file-reading to read the password. |
| **26 → 27** | `:set shell=/bin/bash` | Used the same method as level 25 → 26 to enter Vim, changed the shell and then used the setuid to read the password. |
| **27 → 28** | `git clone` | Cloned a remote repo onto my local machine. |
| **28 → 29** | `git log -p -- <filename>` | Inspected git history to find an exposed password. |
| **29 → 30** | `git branch -a` | Inspected git branches to locate one with an exposed password. |
| **30 → 31** | `git tag`, `git show <tag>` | Inspected tags to find an annotated tag containing the password. |
| **31 → 32** | `add -f`, `commit`, `push` | Created the required key file, forced it to be staged (bypassing the `.gitignore`), committed and pushed. |
| **32 → 33** | `$0` | Escaped a restricted shell by spawning a subshell with the positional parameter. |
# Setting up Git and GitHub

This guide walks through the one-time setup needed to use Git and GitHub for this course.

Course materials and work you produce will be managed with a repository.
A **local repository** is the copy of the project on your computer, and a **remote repository** is the copy stored on GitHub.

You will use Git commands to synchronize the two.

___

## 1. Create a GitHub Account.

If you do not already have a GitHub account, create one at 

https://github.com/

Choose a username that you are comfortable using for coursework and potentially for future professional projects.

___

## 2. Install Git

### macOS

Open the **Terminal** application and type:

```bash
git --version
```

If Git is not already installed, macOS should prompt you to install the Apple Command Line Tools. Accept the installation.

Verify that Git works:
```bash
git --version
```

### Linux

Check if Git is already installed with 

```bash
git --version
```

If it is not installed, use your distribuion's package manager. For Ubuntu/Debian distributions,

```bash
sudo apt update
sudo apt install git
```

After installation, verify with
```bash
git --version
```

## Windows

Download and install Git for Windows from:

https://git-scm.com/install/windows

You can use the default options. Git for Windows includes Git Bash, a terminal that provides many of the same commands available on macOS and Linux.

After installation, open the Start menu, Search for Git Bash and open. Check installation with

```bash
git --version
```

## Configure Git

Open the terminal or Git Bash.

Tell Git your name and email address:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@ripon.edu"
git config --global push.default simple
```

Use the email address associated with your GitHub account.

You can check your configuration with:
```bash
git config --global --list
```


## 4. Create an SSH Key.

GitHub needs a way to authenticate your computer when you access repositories from the command line. We will use an SSH key for authentication.

Check whether you already have a key.

Run:

```bash
ls -la ~/.ssh
```

If you see files named
```
id_ed25519
id_ed25519.pub
```
then you may already have an SSH key. If the files are not present, generate a new key.

Run:
```bash
ssh-keygen -t ed25519
```

You will see something like
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (.../.ssh/id_ed25519):
```

Press Enter to accept the default location.

You will be asked for a passphrase. You may add a passphrase you will remember for security. 

After this step, two files should have been created
```
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```
The ```.pub```file contains your public key. Never share the file ```id_ed25519```. That is your private key.

##5. Add your SSH Key to GitHub

Display your public SSH key:

```bash
cat ~/.ssh/id_ed25519.pub
```

You should see on long line beginning with something like
```
ssh-ed25519 ...
```

Copy the entire line.

Now go to GitHub (https://github.com).

Then 
1. Log in to your GitHub account.
2. Click your profile picture on the top-right corner.
3. Select Settings.
4. Select SSH and GPG keys from the menu on the left.
5. Click New SSH Key.
6.  Give the key a descriptive title such as
	- Personal Windows Laptop
7. Leave the key type as Authentication Key.
8. Paste the contents of ```id_ed25519.pub``` into the Key field.
9. Click Add SSH key.

## 6. Test your GitHub connection

Return to Terminal or Git Bash and run

```bash
ssh -T git@github.com
```

The first time you connect, you may see a message similar to:
```
The authenticity of host 'github.com' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Type in yes. If everything is configured correctly, GitHub should respond with a message like
```
Hi your-username! You've successfully authenticated, but GitHub does not provide shell access.
```

and you are good to go!

## Cloning a Repository.

Once Git and GitHub are configured, you can download this using ```git clone```.

On the repository page click the green Code button and select SSH. Copy the address.

In Terminal or Git Bash, navigate to the directory you want to keep your coursework and run ```git clone``` followed by the copied address.
You can also copy the line below:

```bash
git clone git@github.com:soonho-eric/CSC371_Fa2026.git
```

Move into the repository:
```bash
cd CSC371_Fa2026
```

To check the status of the repository:

```bash
git status
```


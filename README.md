# Introduction
This project can be used to setup a 1 to 1 VPN tunnel between two servers. On one end a second VPN server will be running to provide VPN connection to multiple clients.
The main purpose of this project is to bypass internet censorship and filtering wherever implemented.

This project started during the 2022 protests in Iran.

# Problem Description
The main problem we are trying to solve, is the severe restrictions put on the internet access in totalitarian countries, e.g. Iran as of 2022.
In these countries, access to the internet is very limited and is possible only to specific websites.

In this situation, sometimes the government offers an alternative Intranet instead of the free internet. In Iran it is called the "National Internet". Which is basically a huge intranet in which people can access the selected services and web sites that are hosted inside Iran, and are controlled by the governemtn.

In such countries, whenever there are protests ongoing, the internet access will be even further restricted.
Sometimes the restriction process works as follows:
1. The "National Internet" mode is enabled and access to the outside world is cut down.
2. Access to the internet from the mobile network is restricted (No cell phone will be able to access google.com for example)
3. Access to the internet from the main ISPs is restricted (No home DSL/WiMax/Dial-Up!! will be able to access google.com for example)
4. Total blackout of the internet.

The problem we are trying to solve is to find a way to stay connected to the outside world as long as possible.

# How VPP works
## Basic Setup
This repository contains the required ansible role and playbooks to setup a VPN tunnel between two servers A and B. Server B is located inside the restricted area (where heavy censorship is in place) and server A is located somewhere else with free access to the internet.

```mermaid
graph LR
    Z((Free Internet))---A[Server A]
    A[Server A]---B[Server B]
    B---C[Client 1]
    B---D[Client 2]
    B---E[Client 3]
    B---F[...]
    B---G[Client N]
```

## How it helps
While the previously mentioned censorship process will cut off access to the internet for most of the users, there will still remain some servers who can have access to the internet.
These servers are the ones inside specific datacenters in which some government servers also exist.
During the internet shudown, some financial systems, post systems, and some other systems still need to have access to the outside world.
Also some startups and businesses have already paid a lot of money to the government to stay connected to the outside world even if there are some restrictions on the internet access for others.
This usually means that some datacenters are to be filtered the last. The will stay connected to the internet until the internet is shut down completely.
Therefore, by placing the server B inside one of those datacenters, clients will be able to access internet up to the last moment (until the whole internet access is blocked by the government).

## Requirements
When you clone this repo, you'll have an almost ready to go ansible structure in your working directory. 
Only 2 steps are required before you can use the playbooks:
1. Add the IP address of the purchased servers (A, B) in the inventory.yml file.
2. Add the ssh private keys used to connect to these servers (root access) to the keys directory.

### Add Servers to the Inventory
To add IP address of the servers, you just need to add them into the inventory.yml file.
To do so, just add the IP address of the server B (the one inside the restircted region, e.g. Iran) to the iran_servers part, also for each server, there is a "peer" attribute which specifies the peer server for this server (The peer for server B is server A and should be added to the inventory)

The same thing should be done for the server A (the one outside the restricted region, e.g. the one located in Europe):
```
all:
  hosts:
  children:
    iran_servers:
      hosts:
        X.X.X.X:
          peer: "Y.Y.Y.Y"
        W.W.W.W:
          peer: "Z.Z.Z.Z"
      vars:
        country: "Iran"
    foreign_servers:
      hosts:
        Y.Y.Y.Y:
          peer: "X.X.X.X"
        Z.Z.Z.Z:
          peer: "W.W.W.W"
      vars:
        country: "Foreign"
```

As you can see in the above example, there is a server in Iran (X.X.X.X) who is going to be paired with it's peer (Y.Y.Y.Y), and both of them are added to the inventory.

### Add ssh private keys to the key directory
To add the private keys to the "key" directory, you should name them correctly. The naming convension is quite simple.
Just add the IP address of the host, and then add _ssh_key.pem to the end.
This way ansible will be able to connect to those servers and do the setup.
Please note that keys should have root access to the host for now.
So, if a host is accessible via IP address 1.2.3.4 the key should be named:
```
1.2.3.4_ssh_key.pem
```
and you should put it inside the key directory.

# Possible Challenges
If users try to access websites which are banned according to the regulations of the target country (the country where Server A is located), then the owner of the Server A will have to face the consequences (e.g. banning of their account, ...)

## How to run the playbooks
### Setting up the servers
After providing the keys and adding the hosts into the inventory, run the following command:
```
ansible-playbook -i inventory.yml playbooks/ovpnsetup.yml -l X.X.X.X,Y.Y.Y.Y
```
Not that how we limitted the execution of the playbook to the specified servers, and not all the servers listed in the inventory.

This will take some time, and then all the A-B server pairs listed in the inventory should be ready to server independently.

### Adding some clients
To add clients, simply run the addclient playbook:
```
ansible-playbook -i inventory.yml playbooks/client_add.yml -l "Y.Y.Y.Y" --tags addclient
```
Note that how we limitted the execution of the playbook to the mentioned server (this is the B server, e.g. the one located in Iran).

After that, in the control host (the host which you ran the ansible-playbook command on), there will be a folder containing the config file for the recently added client.
Please not that all the client config files will ask for a password at some point, after running the addclient playbook, the password will be printed out on the screen in a debug message at the end of the playbook execution.

# Limitations
As of now, only Ubuntu 22.0.4 systems are supported. Others may work, but not tested.

# Future Developments
We believe in decentralized approach.
The goal of this project is to make it easy for everyone to setup this tunneling mechanism. Everyone inside the totalitarian countries, knows someone from outside who can purchase the "Foreign Server" for them, and they can purchase the "Internal Server" themselves. 
Having this pair of servers, the tunnel can be set up easily.

This way, each pair of servers, is not supposed to server multiple thousands of users, but maybe some hundereds at most.
But there will be hundereds of such A-B pairs.

In order to reach that point, we plan to provide a website template, that when implemented, will bring up a web page, in which people can donate server pairs and setup server pairs, and users can choose a specific pair to connect through.

For that, we are planning to develope the required playbooks/roles/scripts so that the site setup will also be easy for everyone.


# How to participate
If you want to help improving the service, you need to create pull requests. But do not use your personal GitHub user for that. Try to stay as much anonymous as possible. Create an anonymous GitHub user, using an anonymous mail service like protonmail or ... and contribute to this project only using that account.

This is to avoid being identified and chased by government agents.

We will try to study the PRs and merge them if suited.

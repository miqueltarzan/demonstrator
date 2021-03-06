###############################################################################
## 1. OVERVIEW                                                                #
###############################################################################

This repository contains a command-line tool (gen.py) which allows the user to
easily try and test the IRATI stack in a multi-node scenario.

The purpose of the tool is twofold:

* Allow people interested in RINA to trial the IRATI stack, which includes the
  PRISTINE Software Development Kit;
* Help IRATI developers and software release engineers to carry out integration
  and regression tests;

For the first kind of users, no knoweledge about how to compile and install
IRATI is required. Everything the user need is self-contained in this
repository and is explained in this document.

Each node is emulated using a light Virtual Machine (VM), run under the control
of the QEMU hypervisor. All the VMs are run locally without any risk for your
PC, so you don't need a dedicated machine or multiple physical machines.

All the user has to do is to prepare a configuration file which describes the
scenario to be demonstrated. This requires the user to specify all the Layer 2
connections between the nodes and all the DIFs which lay over this L2 topology.
A DIF can be stacked over other DIFs, and arbitrary levels of recursion is
virtually supported by the tool (be aware that the IRATI stack may place
restrictions on the recursion depth, so the scenario bootstrap may fail if
you use too many levels of recursion).

The syntax of the configuration file is detailed in section 4.

Using the -g option, the tool is able to generate an image depicting the graph
of all normal DIFs, showing the lower-level DIFs connecting them.

Run

	$ ./gen.py -h

to see all the available options.


###############################################################################
## 2. WORKFLOW                                                                #
###############################################################################

Once the configuration file has been prepared, the user can invoke the tool

    $ ./gen.py -c /path/to/config/file

which will generate two bash scripts: up.sh and down.sh.

Running the up.sh script will bootstrap the specified scenario, which involves
the following operations:

* Create TAP interfaces and linux software-bridges to emulate the
  specified L2 topology.

* Run the VMs emulating the nodes.

* Bootstrap the IRATI stack on each node, with proper configuration
  (IPCM configuration, DIF templates, DIF Allocator map, ...)

* Perform all the enrollment, at all DIF layers, respecting the
  dependency order.

The up.sh script reports verbose information about ongoing operations. If
everything goes well, you should be able to see the script reporting about
successful enrollment operations right before terminating.

Once the bootstrap is complete, the user can access any node an play with
them (e.g. running the rina-echo-time test application to check connectivity
between the nodes).

The tool can work in two different modes: buildroot (default) and legacy. The
way you access the nodes depends on the modes. In any case, unless you know
what you are doing, you want to use the default buildroot mode. More
information about the legacy mode can be found in section 6.

To undo the operations carried out by the up.sh, the user can run the down.sh
script. Once the latter script terminates, all the VMs have been terminated.

The user can run up.sh/down.sh multiple times, and use gen.py only when she
wants to modify the scenario. If you run up.sh, make sure you run down.sh
before generating a new scenario, otherwise a PC reboot may be necessary in
order to clean-up leftover artifacts.

By default, every VM is assigned 128 MB of memory, so with 4GB or memory you
can run topologies with up to 32 nodes. You may even try to reduce the per-VM
memory more, to achieve higher density.


###############################################################################
## 3. HARDWARE AND SOFTWARE REQUIREMENTS                                      #
###############################################################################

* [HW] An x86\_64 processor with hardware-assisted virtualization support (e.g.
  Intel VT-X or AMD-V)

* [SW] Linux-based Operating System.

* [SW] QEMU, a fast and portable machine emulator.

* [SW] brctl command-lilne tool (usually found in a distro package called
  bridge-utils or brctl).


###############################################################################
## 4. SCENARIO CONFIGURATION FILE SYNTAX                                      #
###############################################################################

The configuration file for gen.py contains a list of declarations, with one
declaration per line.
Lines starting with '#' are ignored by the tool so that they can be used for
comments.

There are a few types of declarations or directives:

* **eth**, to specify Layer 2 connections between nodes;
* **dif**, to specify how normal DIFs stack onto each other;
* **policy**, to specify non-default policies for normal DIFs;
* **appmap**, to specify static application-to-DIF mappings for normal DIFs;
* **overlay**, to specify a per-node directory to be overlaid on the node
               file system;
* **netem**, to specify a per-node, per-shim-dif link emulation features
             (delay, loss, duplicate packets, etc.)
* **enroll**, to specify manual enrollment, in case the automatic enrollment
              strategies do not meet the user requirements

Each type of declaration may occur many times.
Note that nodes are implicitely declared by means of **eth** and **dif** lines:
there don't have an separate explicit declaration type.

The repository contains some example of scenario configuration files:

	gen.conf, examples/star.conf, examples/two-layers.conf, ...

with comments explaining the respective configuration.

### 4.1 **eth** declarations

An **eth** declaration is used to specify an L2 (Ethernet) connection between
two or more nodes. A star topology - one with a central L2 switch - is used
to connect together the specified nodes.
Consequentely, each **eth** declaration corresponds to a separate Ethernet L2
broadcast domain.

Each L2 domain is identified by a different VLAN number, which will be used
by the IRATI stack as a name for the Shim DIFs over 802.1q, and that will be
used to configure the VLAN on the nodes' interfaces.

The syntax for the **eth** declaration is as follows:

    eth VLAN_ID LINK_SPEED NODE_NAME...

where

* VLAN\_ID is an integer between 1 and 4095, identifying the L2 domain.

* LINK\_SPEED indicates the maximum speed for this L2 domain (e.g. 30Mbps,
  500 Kbps, 1Gbps, ...), which is implemented by rate-limiting the TAP
  interfaces, outside the VMs. If 0Mbps is specified, no rate-limiting is
  used.

* NODE\_NAME is an identifier for a node, which can by any non-space character.
  Two or more node can be specified, separated by spaces.


### 4.2 **dif** declarations

A **dif** declaration gives information about how a single node partecipates in
a specific N-DIF. It is used to specify what N-1 (lower) DIFs are used by the
node to partecipate in the N-DIF.

Consequently, for each normal DIF there will be a separate **dif** declaration
for each node taking part in that DIF.

The syntax for the **dif** declaration is as follows:

	dif DIF_NAME NODE_NAME LOWER_DIF_NAME...

where

* DIF\_NAME is the name of the N-DIF under specification.

* NODE\_NAME is the name of the node that takes part in DIF\_NAME.

* LOWER\_DIF\_NAME is the name of an N-1-DIF (either Shim or normal) which is
  used by NODE\_NAME to connect to its neighbors in the N-DIF. One or more
  N-1-DIFs can be specified, separated by space. Having more N-1-DIFs usually
  happens when a node has multiple neighbors.


### 4.3 **policy** declarations

A **policy** declaration is used to instruct the the tool to setup a particular
non-default *policy-set* for a single IRATI component in a specific DIF.
The policy-set is an IRATI-specific object that groups together all the
policies belonging to a certain IRATI component (which maps to a component
of the RINA architecture). A policy-set is logically associated with an
instance of an IPCP component in a certain DIF.

Consequently, for each normal DIF there will be a separate **policy**
declaration for each IRATI DIF component that needs a non-default policy-set.

The syntax for the **policy** declaration is as follows:

	policy DIF_NAME ( * | NODE_NAME_1,NODE_NAME2,... ) COMPONENT_PATH POLICY_SET_NAME [PARAM1=VALUE1 PARAM2=VALUE2 ...]

where

* DIF\_NAME is the name of the DIF under specification.

* The second argument can be '*' or a list of comma-separated node names. In
  the former case, the policy is deployed on all nodes in the DIF, while in
  the latter the policy is deployed only in the listed nodes.

* COMPONENT\_PATH is a string identifying the DIF component under
  specification. The string syntax is the same one used by the PRISTINE SDK
  to identify components (e.g. "rmt.pff" to indicate the PDU Forwarding
  Function component).

* POLICY\_SET\_NAME is the name of a policy set to use for the specified
  component in the specified DIF. The name must correspond to the one declared
  in some plugin's manifest file.

* A list of name/values couples is used to specify policy-set parameters.


### 4.4 **appmap** declarations

An **appmap** declaration is used to specify a static mapping of an application
name to a normal DIF. This static configuration is used by the DIF allocator
during the flow allocation procedure.

The syntax is as follows:

        appmap DIF_NAME AP_NAME AP_INSTANCE

where

* DIF\_NAME is the name of the DIF that the applications name maps to
* AP\_NAME is the application process name of the mapped application
* AP\_INSTANCE is the application process instance of the mapped application


### 4.5 **overlay** directive

An **overlay** directive is used to specify a directory on the host file system
to be overlaid on the file system of a specific node.
This directive overrides the behaviour of the --overlay option, because the
--overlay option is processed (i.e. the files copied on the node file system)
before the directive is processed.

The syntax is as follows:

        overlay NODE_NAME OVERLAY

where

* NODE\_NAME is the name of the node to which the overlay applies
* OVERLAY is the path (absolute or relative to the path of the demonstrator
          command line tool) of the overlay directory tree on the host file
          system


### 4.6 **netem** directive

An **netem** directive allows link emulation, using the *netem* features
of the Linux traffic control framework. Any valid netem command can be
used (e.g. see http://man7.org/linux/man-pages/man8/tc-netem.8.html).
However, don't use the netem *rate* command unless you know what you are
doing. The recommended way to add rate limiting is to specify a non-zero
link speed value in the **eth** directive.

The syntax is as follows:

        netem SHIM_NAME NODE_NAME NETEM_COMMAND

where

* SHIM\_NAME is the name of the Shim DIF where link emulation applies
* NODE\_NAME is the name of the node for which the link must be emulated
	     for the specified link

Example to add delay and packet loss to node xyz in shim wan.DIF

	netem wan.DIF xyz delay 100ms loss random 0.1%


### 4.7 **enroll** directive

A list of **enroll** directives may be specified when the user does not want
to use the automatic enrollment strategies supported by the demonstrator
(e.g. minimal, full-mesh, ...). If you are not sure about what are you
doing, don't use the **enroll** directive and rely on the automatic
(default) strategies.

The syntax of a directive is as follows:

        enroll DIF_NAME NODE_NAME NEIGH_NODE_NAME N_1_DIF

where

* DIF\_NAME is the name of the DIF where the enrollment should happen
* NODE\_NAME is the name of the enrollee node
* NEIGH\_NODE\_NAME is the name of the enroller node
* N\_1\_DIF is the name of the N-1-DIF in common between enrollee and
            enroller, to be used for the enrollment procedure



###############################################################################
## 5. BUILDROOT MODE                                                          #
###############################################################################

When using the tool in buildroot (default) mode, things are straightforward.

Once you have run up.sh, you can access the node named "XYZ" using

    $ ./access.sh XYZ

Each node runs in a minimal VM environment, which is an RAM filesystem
(initramfs) created using the buildroot framework (https://buildroot.org/).
All the IRATI software and its dependencies (except for the kernel image) are
packed into about 30 MB.

A snapshot of both the kernel image and the file system the are available in
the buildroot directory of this repository.
The SHA identifier of the IRATI stack built into the current image is
11b684eaed18b6f12c1888031b4a2fc7ea29123d.

Be aware that any modifications done on the VM filesystem are discarded when
the scenario is torn down.


### 5.1 IRATI mini-tutorial

This document is *not* a tutorial on how to use the IRATI stack. However, this
section describes some basic tests you can do in order to check that things
are working as they are supposed to work.

Generate a simple three-node scenario, with two Shim DIFs over 802.1q and one
normal DIF laying over those:

	$ ./gen.py -c gen.conf

Run the up.sh script to boostrap the scenario

	$ ./up.sh

waiting for it to finish (it may take tens of seconds).

Access node "a" and run rina-echo-time in server ping mode

	$ ./access.sh a
	# rina-echo-time -l

Using a different terminal, access node "c" and run rina-echo-time in client
ping mode, sending 10 packets to the server.

	$ ./access.sh c
	# rina-echo-time -c 10

Once the experiment terminates, use CTRL-C to stop the rina-echo-time server,
and issue the "exit" command on both terminals to exit from the nodes.

Run the down.sh script to tear down the scenario

	$ ./down.sh

That's it, you successfully ran a ping application in the RINA world!


###############################################################################
## 6. LEGACY MODE                                                             #
###############################################################################

In short, don't use this mode unless you know what you are doing.

When using legacy mode, you are not using the buildroot-generated kernel and
filesystem, already available in the repository. Instead, you have build your
own VM disk image, which must contain the IRATI kernel and user-space software.

The disadvantage of this approach is that it is hard to build such an image
using less than 4 GB. See section 5 for a better approach.

In addition to the requirements specified in section 3, you need a QEMU VM
image containing:

* The IRATI stack installed
* The bootloader configured to boot the IRATI kernel
* Python
* sudo enabled for the login username on the VM (referred to as ${username}
  in the following), with NOPASSWD, e.g. /etc/sudoers should contain something
  similar to the following line:

    % wheel ALL=(ALL) NOPASSWD: ALL


### 6.1 Instructions, to be followed in the specified order

1. Edit the gen.env file to set the IRATI installation path (on the VM
   filesystem), the path of the QEMU VM image (on your physical machine
   file system) and the login username on the VM (${username})

2. Specify the desired topology in gen.conf

3. Run ./gen.py to generate bootstrap and teardown script for the
  topology specified in (2)

4. Use ./up.sh to bootstrap the scenario

5. VMs are accessible at localhost ports 2223, 2224, 2225, etc.
   e.g. ssh -p2223 ${username}@localhost

6. Perform your tests on the VMs using ssh (5)

7. Shutdown the scenario (destroying the VMs) using ./down.sh

8. VMs launched by ./up.sh have a non-persistent disk --> modifications
   will be lost at shutdown time (7).
   To make persistent modifications to the VM image (e.g. to update PRISTINE
   software), run ./update\_vm.sh and access the VM at
        ssh -p2222 ${username}@localhost

Don't try to run ./update\_vm.sh while the test is running (i.e. you've run
./up.sh but still not run ./down.sh).


### 6.2 Automatic login to the VMs

In order to automatically login to the VMs, it's highly recommended to use SSH
keys. In this way it is possible to avoid inserting the password again and
again (during the tests):

    $ ./update_vm.sh
    $ ssh-keygen -t rsa  # e.g. save the key in /home/${username}/.ssh/pristine_rsa
    $ ssh-copy-id -p2222 ${username}@localhost
    $ shutdown the VM

[http://serverfault.com/questions/241588/how-to-automate-ssh-login-with-password]

Now you should be able to run ./up.sh without the need to insert the password


###############################################################################
## 7. CREDITS                                                                 #
###############################################################################

This tool has been developed on behalf of FP7 PRISTINE and H2020 ARCIFIRE
EU-funded projects.

Author:
* Vincenzo Maffione, v DOT maffione AT nextworks DOT it

Contributors:
* Eduard Grasa, I2CAT
* Leonardo Bergesio, I2CAT

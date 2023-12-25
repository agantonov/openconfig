<<<<<<< Updated upstream
### OpenConfig CRUD with Juniper
OpenConfig defines and implements a common, vendor-independent software layer for managing network devices. The goal of OpenConfig is to enable network automation teams to use a single unified data model for configuring network devices from various vendors. Juniper has [incorporated](https://www.juniper.net/documentation/us/en/software/junos/open-config/topics/concept/openconfig-installing.html) OpenConfig models into the standard Junos package starting from Junos 18.3R1.
By default, the OpenConfig schema is not accessible through the CLI. To reveal the OpenConfig knob in the CLI, execute the following command:
```
set system schema openconfig unhide
```
You can explore all supported OpenConfig models through the following [link](https://www.juniper.net/documentation/us/en/software/junos/open-config/topics/concept/openconfig-data-model-version.html).

Below, I will demonstrate the four fundamental functions that an OpenConfig model should be capable of: Create, Read, Update, and Delete (CRUD).

I have prepared two simple Python scripts to load and read configurations to/from a Juniper device. These scripts utilize the Juniper [PyEZ library](https://www.juniper.net/documentation/us/en/software/junos-pyez/junos-pyez-developer/topics/concept/junos-pyez-overview.html), which significantly simplifies the way developers interact with Juniper devices.

* [load_config.py](https://github.com/agantonov/openconfig/blob/main/load_config.py) loads configuration to Juniper Device:
```
$ python3 load_config.py -h
usage: load_config.py [-h] [-u USER] [-p PASSWD] config format device

Load Juniper Config

positional arguments:
  config                Name of the file containing the configuration to be uploaded
  format                Configuration file format
  device                IP address or domain name of the Juniper router

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  User name
  -p PASSWD, --passwd PASSWD
                        Password
```
* [read_config.py](https://github.com/agantonov/openconfig/blob/main/read_config.py) reads Juniper configuration:
```
$ python3 read_config.py -h
usage: read_config.py [-h] [-o OUTPUT] [-m MODEL] [-f FILTER] [-u USER] [-p PASSWD] format device

Read Juniper Config

positional arguments:
  format                Configuration output format: xml, text, set, json
  device                IP address or domain name of the Juniper router

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Write output to a file
  -m MODEL, --model MODEL
                        YANG data model: custom, ietf, openconfig
  -f FILTER, --filter FILTER
                        return a specific XML subtree
  -u USER, --user USER  User name
  -p PASSWD, --passwd PASSWD
                        Password
```
#### Create
[Here](https://github.com/agantonov/openconfig/blob/main/openconfig-create.xml) you can find the configuration file in XML format using the Openconfig model. It creates the following objects:
  - Interface lo0.2 = 2.2.2.2/32
  - Routing-policies:
      - openconfig-vrf-import
      - openconfig-vrf-export 
  - L3VPN openconfig-vrf
      - interface: lo0.2
      - import-policy: openconfig-vrf-import
      - export-policy: openconfig-vrf-export
```
$ python3 load_config.py openconfig-create.xml xml mx204-83

[edit]
+  openconfig-routing-policy:routing-policy {
+      defined-sets {
+          openconfig-bgp-policy:bgp-defined-sets {
+              community-sets {
+                  community-set openconfig-vrf-export-com {
+                      config {
+                          community-set-name openconfig-vrf-export-com;
+                          community-member target:65100:9999;
+                      }
+                  }
+                  community-set openconfig-vrf-import-com {
+                      config {
+                          community-set-name openconfig-vrf-import-com;
+                          community-member target:65100:9999;
+                      }
+                  }
+              }
+          }
+      }
+      policy-definitions {
+          policy-definition openconfig-vrf-export {
+              config {
+                  name openconfig-vrf-export;
+              }
+              statements {
+                  statement term1 {
+                      conditions {
+                          config {
+                              install-protocol-eq DIRECTLY_CONNECTED;
+                          }
+                      }
+                      actions {
+                          config {
+                              policy-result ACCEPT_ROUTE;
+                          }
+                          openconfig-bgp-policy:bgp-actions {
+                              set-community {
+                                  config {
+                                      options ADD;
+                                  }
+                                  reference {
+                                      config {
+                                          community-set-ref openconfig-vrf-export-com;
+                                      }
+                                  }
+                              }
+                          }
+                      }
+                  }
+              }
+          }
+          policy-definition openconfig-vrf-import {
+              config {
+                  name openconfig-vrf-import;
+              }
+              statements {
+                  statement term1 {
+                      conditions {
+                          openconfig-bgp-policy:bgp-conditions {
+                              config {
+                                  community-set openconfig-vrf-import-com;
+                              }
+                          }
+                      }
+                      actions {
+                          config {
+                              policy-result ACCEPT_ROUTE;
+                          }
+                      }
+                  }
+              }
+          }
+      }
+  }
[edit openconfig-interfaces:interfaces interface lo0]
+    subinterfaces {
+        subinterface 2 {
+            openconfig-if-ip:ipv4 {
+                addresses {
+                    address 2.2.2.2 {
+                        config {
+                            prefix-length 32;
+                        }
+                    }
+                }
+            }
+        }
+    }
[edit]
+  openconfig-network-instance:network-instances {
+      network-instance openconfig-vrf {
+          config {
+              name oc-vrf;
+              type L3VRF;
+              enabled true;
+              router-id 1.1.0.9;
+              route-distinguisher 1.1.0.9:9999;
+          }
+          inter-instance-policies {
+              apply-policy {
+                  config {
+                      import-policy openconfig-vrf-import;
+                      export-policy openconfig-vrf-export;
+                  }
+              }
+          }
+          interfaces {
+              interface lo0.2 {
+                  config {
+                      id lo0.2;
+                      interface lo0;
+                      subinterface 2;
+                  }
+              }
+          }
+      }
+  }
```
The configuration has been successfully applied.

#### Read
Now let's read the configuration we have just uploaded to the device:
* Interfaces subtree in the XML format
```
$ python3 read_config.py -f 'interfaces' -m openconfig xml mx204-83
<interfaces>
  <interface>
    <name>lo0</name>
    <config>
      <name>lo0</name>
      <type>loopback</type>
      <enabled>true</enabled>
    </config>
    <subinterfaces>
      <subinterface>
        <index>2</index>
        <ipv4>
          <addresses>
            <address>
              <ip>2.2.2.2</ip>
              <config>
                <prefix-length>32</prefix-length>
              </config>
            </address>
          </addresses>
        </ipv4>
      </subinterface>
    </subinterfaces>
  </interface>
</interfaces>
```
* Routing-policy subtree in the SET format
```
$ python3 read_config.py -f 'routing-policy' -m openconfig set mx204-83
<configuration-set>
set openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-export-com config community-set-name openconfig-vrf-export-com
set openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-export-com config community-member target:65100:9999
set openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-import-com config community-set-name openconfig-vrf-import-com
set openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-import-com config community-member target:65100:9999
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export config name openconfig-vrf-export
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 conditions config install-protocol-eq DIRECTLY_CONNECTED
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions config policy-result ACCEPT_ROUTE
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions openconfig-bgp-policy:bgp-actions set-community config options ADD
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions openconfig-bgp-policy:bgp-actions set-community reference config community-set-ref openconfig-vrf-export-com
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import config name openconfig-vrf-import
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import statements statement term1 conditions openconfig-bgp-policy:bgp-conditions config community-set openconfig-vrf-import-com
set openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import statements statement term1 actions config policy-result ACCEPT_ROUTE
</configuration-set>
```
#### Update
The next action is the configuration modification. We will do the following: 
  - Create interface: ae83.4083
  - Add inteface ae83.4083 to L3VPN openconfig-vrf
  - Add a static route to L3VPN openconfig-vrf
  - Add another term to export static routes from L3VPN openconfig-vrf

To accomplish this, I will apply the XML configuration file [openconfig-update.xml](https://github.com/agantonov/openconfig/blob/main/openconfig-update.xml):
```
$ python3 load_config.py openconfig-update.xml xml mx204-83

[edit openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements]
       statement term1 { ... }
+      statement term2 {
+          conditions {
+              config {
+                  install-protocol-eq STATIC;
+              }
+          }
+          actions {
+              config {
+                  policy-result ACCEPT_ROUTE;
+              }
+              openconfig-bgp-policy:bgp-actions {
+                  set-community {
+                      config {
+                          options ADD;
+                      }
+                      reference {
+                          config {
+                              community-set-ref openconfig-vrf-export-com;
+                          }
+                      }
+                  }
+              }
+          }
+      }
[edit openconfig-interfaces:interfaces]
+   interface ae83 {
+       config {
+           name ae83;
+           type ethernetCsmacd;
+           enabled true;
+       }
+       subinterfaces {
+           subinterface 4083 {
+               openconfig-if-ip:ipv4 {
+                   addresses {
+                       address 83.83.83.83 {
+                           config {
+                               prefix-length 24;
+                           }
+                       }
+                   }
+               }
+               openconfig-vlan:vlan {
+                   match {
+                       single-tagged {
+                           config {
+                               vlan-id 4083;
+                           }
+                       }
+                   }
+               }
+           }
+       }
+   }
[edit openconfig-network-instance:network-instances network-instance openconfig-vrf interfaces]
+     interface ae83.4083 {
+         config {
+             id ae83.4083;
+             interface ae83;
+             subinterface 4083;
+         }
+     }
[edit openconfig-network-instance:network-instances network-instance openconfig-vrf]
+    protocols {
+        protocol STATIC static-routes {
+            static-routes {
+                static 3.3.3.0/24 {
+                    config {
+                        prefix 3.3.3.0/24;
+                    }
+                    next-hops {
+                        next-hop 83.83.83.1 {
+                            config {
+                                next-hop 83.83.83.1;
+                            }
+                        }
+                    }
+                }
+            }
+        }
+    }
```
#### Delete
The last CRUD function is Delete. We can remove the Openconfig configuration either with the XML [file](https://github.com/agantonov/openconfig/blob/main/openconfig-delete.xml) using the delete="delete" attribute or using the ASCII [text](https://github.com/agantonov/openconfig/blob/main/openconfig-delete.set) and the "delete:" statement
```
$ python3 load_config.py openconfig-delete.xml xml mx204-83

[edit]
-  openconfig-routing-policy:routing-policy {
...
(omitted for brevity)
...
-  }
[edit openconfig-interfaces:interfaces interface lo0]
-    subinterfaces {
...
(omitted for brevity)
...
-    }
[edit]
-  openconfig-network-instance:network-instances {
...
(omitted for brevity)
...
-  }
```

ASCII text:
```
$ python3 load_config.py openconfig-delete.set set mx204-83

[edit]
-  openconfig-routing-policy:routing-policy {
...
(omitted for brevity)
...
-  }
-  openconfig-interfaces:interfaces {
...
(omitted for brevity)
...
-  }
-  openconfig-network-instance:network-instances {
...
(omitted for brevity)
...
-  }
```

As a result, we succesfully demonstrated that Juniper devices can support CRUD operations with the Openconfig data model.

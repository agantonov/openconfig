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
=======
{"payload":{"allShortcutsEnabled":false,"fileTree":{"":{"items":[{"name":"README.md","path":"README.md","contentType":"file"},{"name":"load_config.py","path":"load_config.py","contentType":"file"},{"name":"openconfig-create.xml","path":"openconfig-create.xml","contentType":"file"},{"name":"openconfig-delete.set","path":"openconfig-delete.set","contentType":"file"},{"name":"openconfig-delete.xml","path":"openconfig-delete.xml","contentType":"file"},{"name":"openconfig-update.xml","path":"openconfig-update.xml","contentType":"file"},{"name":"read_config.py","path":"read_config.py","contentType":"file"}],"totalCount":7}},"fileTreeProcessingTime":2.3432370000000002,"foldersToFetch":[],"reducedMotionEnabled":null,"repo":{"id":734859043,"defaultBranch":"main","name":"openconfig","ownerLogin":"agantonov","currentUserCanPush":false,"isFork":false,"isEmpty":false,"createdAt":"2023-12-22T20:41:20.000Z","ownerAvatar":"https://avatars.githubusercontent.com/u/34284048?v=4","public":true,"private":false,"isOrgOwned":false},"symbolsExpanded":false,"treeExpanded":true,"refInfo":{"name":"main","listCacheKey":"v0:1703338454.0","canEdit":false,"refType":"branch","currentOid":"ed0690a9c9fb8efb72ccbb330aba1a4f5e74fb7a"},"path":"README.md","currentUser":null,"blob":{"rawLines":null,"stylingDirectives":null,"csv":null,"csvError":null,"dependabotInfo":{"showConfigurationBanner":false,"configFilePath":null,"networkDependabotPath":"/agantonov/openconfig/network/updates","dismissConfigurationNoticePath":"/settings/dismiss-notice/dependabot_configuration_notice","configurationNoticeDismissed":null,"repoAlertsPath":"/agantonov/openconfig/security/dependabot","repoSecurityAndAnalysisPath":"/agantonov/openconfig/settings/security_analysis","repoOwnerIsOrg":false,"currentUserCanAdminRepo":false},"displayName":"README.md","displayUrl":"https://github.com/agantonov/openconfig/blob/main/README.md?raw=true","headerInfo":{"blobSize":"14.5 KB","deleteInfo":{"deleteTooltip":"You must be signed in to make or propose changes"},"editInfo":{"editTooltip":"You must be signed in to make or propose changes"},"ghDesktopPath":"https://desktop.github.com","gitLfsPath":null,"onBranch":true,"shortPath":"bda545b","siteNavLoginPath":"/login?return_to=https%3A%2F%2Fgithub.com%2Fagantonov%2Fopenconfig%2Fblob%2Fmain%2FREADME.md","isCSV":false,"isRichtext":true,"toc":[{"level":3,"text":"OpenConfig CRUD with Juniper","anchor":"openconfig-crud-with-juniper","htmlText":"OpenConfig CRUD with Juniper"},{"level":4,"text":"Create","anchor":"create","htmlText":"Create"},{"level":4,"text":"Read","anchor":"read","htmlText":"Read"},{"level":4,"text":"Update","anchor":"update","htmlText":"Update"},{"level":4,"text":"Delete","anchor":"delete","htmlText":"Delete"}],"lineInfo":{"truncatedLoc":"379","truncatedSloc":"362"},"mode":"file"},"image":false,"isCodeownersFile":null,"isPlain":false,"isValidLegacyIssueTemplate":false,"issueTemplateHelpUrl":"https://docs.github.com/articles/about-issue-and-pull-request-templates","issueTemplate":null,"discussionTemplate":null,"language":"Markdown","languageID":222,"large":false,"loggedIn":false,"newDiscussionPath":"/agantonov/openconfig/discussions/new","newIssuePath":"/agantonov/openconfig/issues/new","planSupportInfo":{"repoIsFork":null,"repoOwnedByCurrentUser":null,"requestFullPath":"/agantonov/openconfig/blob/main/README.md","showFreeOrgGatedFeatureMessage":null,"showPlanSupportBanner":null,"upgradeDataAttributes":null,"upgradePath":null},"publishBannersInfo":{"dismissActionNoticePath":"/settings/dismiss-notice/publish_action_from_dockerfile","dismissStackNoticePath":"/settings/dismiss-notice/publish_stack_from_file","releasePath":"/agantonov/openconfig/releases/new?marketplace=true","showPublishActionBanner":false,"showPublishStackBanner":false},"rawBlobUrl":"https://github.com/agantonov/openconfig/raw/main/README.md","renderImageOrRaw":false,"richText":"<article class=\"markdown-body entry-content container-lg\" itemprop=\"text\"><h3 tabindex=\"-1\" dir=\"auto\"><a id=\"user-content-openconfig-crud-with-juniper\" class=\"anchor\" aria-hidden=\"true\" tabindex=\"-1\" href=\"#openconfig-crud-with-juniper\"><svg class=\"octicon octicon-link\" viewBox=\"0 0 16 16\" version=\"1.1\" width=\"16\" height=\"16\" aria-hidden=\"true\"><path d=\"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z\"></path></svg></a>OpenConfig CRUD with Juniper</h3>\n<p dir=\"auto\">OpenConfig defines and implements a common, vendor-independent software layer for managing network devices. The goal of OpenConfig is to enable network automation teams to use a single unified data model for configuring network devices from various vendors. Juniper has <a href=\"https://www.juniper.net/documentation/us/en/software/junos/open-config/topics/concept/openconfig-installing.html\" rel=\"nofollow\">incorporated</a> OpenConfig models into the standard Junos package starting from Junos 18.3R1.\nBy default, the OpenConfig schema is not accessible through the CLI. To reveal the OpenConfig knob in the CLI, execute the following command:</p>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"set system schema openconfig unhide\"><pre class=\"notranslate\"><code>set system schema openconfig unhide\n</code></pre></div>\n<p dir=\"auto\">You can explore all supported OpenConfig models through the following <a href=\"https://www.juniper.net/documentation/us/en/software/junos/open-config/topics/concept/openconfig-data-model-version.html\" rel=\"nofollow\">link</a>.</p>\n<p dir=\"auto\">Below, I will demonstrate the four fundamental functions that an OpenConfig model should be capable of: Create, Read, Update, and Delete (CRUD).</p>\n<p dir=\"auto\">I have prepared two simple Python scripts to load and read configurations to/from a Juniper device. These scripts utilize the Juniper <a href=\"https://www.juniper.net/documentation/us/en/software/junos-pyez/junos-pyez-developer/topics/concept/junos-pyez-overview.html\" rel=\"nofollow\">PyEZ library</a>, which significantly simplifies the way developers interact with Juniper devices.</p>\n<ul dir=\"auto\">\n<li><a href=\"https://github.com/agantonov/openconfig/blob/main/load_config.py\">load_config.py</a> loads configuration to Juniper Device:</li>\n</ul>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 load_config.py -h\nusage: load_config.py [-h] [-u USER] [-p PASSWD] config format device\n\nLoad Juniper Config\n\npositional arguments:\n  config                Name of the file containing the configuration to be uploaded\n  format                Configuration file format\n  device                IP address or domain name of the Juniper router\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -u USER, --user USER  User name\n  -p PASSWD, --passwd PASSWD\n                        Password\"><pre class=\"notranslate\"><code>$ python3 load_config.py -h\nusage: load_config.py [-h] [-u USER] [-p PASSWD] config format device\n\nLoad Juniper Config\n\npositional arguments:\n  config                Name of the file containing the configuration to be uploaded\n  format                Configuration file format\n  device                IP address or domain name of the Juniper router\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -u USER, --user USER  User name\n  -p PASSWD, --passwd PASSWD\n                        Password\n</code></pre></div>\n<ul dir=\"auto\">\n<li><a href=\"https://github.com/agantonov/openconfig/blob/main/read_config.py\">read_config.py</a> reads Juniper configuration:</li>\n</ul>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 read_config.py -h\nusage: read_config.py [-h] [-o OUTPUT] [-m MODEL] [-f FILTER] [-u USER] [-p PASSWD] format device\n\nRead Juniper Config\n\npositional arguments:\n  format                Configuration output format: xml, text, set, json\n  device                IP address or domain name of the Juniper router\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTPUT, --output OUTPUT\n                        Write output to a file\n  -m MODEL, --model MODEL\n                        YANG data model: custom, ietf, openconfig\n  -f FILTER, --filter FILTER\n                        return a specific XML subtree\n  -u USER, --user USER  User name\n  -p PASSWD, --passwd PASSWD\n                        Password\"><pre class=\"notranslate\"><code>$ python3 read_config.py -h\nusage: read_config.py [-h] [-o OUTPUT] [-m MODEL] [-f FILTER] [-u USER] [-p PASSWD] format device\n\nRead Juniper Config\n\npositional arguments:\n  format                Configuration output format: xml, text, set, json\n  device                IP address or domain name of the Juniper router\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTPUT, --output OUTPUT\n                        Write output to a file\n  -m MODEL, --model MODEL\n                        YANG data model: custom, ietf, openconfig\n  -f FILTER, --filter FILTER\n                        return a specific XML subtree\n  -u USER, --user USER  User name\n  -p PASSWD, --passwd PASSWD\n                        Password\n</code></pre></div>\n<h4 tabindex=\"-1\" dir=\"auto\"><a id=\"user-content-create\" class=\"anchor\" aria-hidden=\"true\" tabindex=\"-1\" href=\"#create\"><svg class=\"octicon octicon-link\" viewBox=\"0 0 16 16\" version=\"1.1\" width=\"16\" height=\"16\" aria-hidden=\"true\"><path d=\"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z\"></path></svg></a>Create</h4>\n<p dir=\"auto\"><a href=\"https://github.com/agantonov/openconfig/blob/main/openconfig-create.xml\">Here</a> you can find the configuration file in XML format using the Openconfig model. It creates the following objects:</p>\n<ul dir=\"auto\">\n<li>Interface lo0.2 = 2.2.2.2/32</li>\n<li>Routing-policies:\n<ul dir=\"auto\">\n<li>openconfig-vrf-import</li>\n<li>openconfig-vrf-export</li>\n</ul>\n</li>\n<li>L3VPN openconfig-vrf\n<ul dir=\"auto\">\n<li>interface: lo0.2</li>\n<li>import-policy: openconfig-vrf-import</li>\n<li>export-policy: openconfig-vrf-export</li>\n</ul>\n</li>\n</ul>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 load_config.py openconfig-create.xml xml mx204-83\n\n[edit]\n+  openconfig-routing-policy:routing-policy {\n+      defined-sets {\n+          openconfig-bgp-policy:bgp-defined-sets {\n+              community-sets {\n+                  community-set openconfig-vrf-export-com {\n+                      config {\n+                          community-set-name openconfig-vrf-export-com;\n+                          community-member target:65100:9999;\n+                      }\n+                  }\n+                  community-set openconfig-vrf-import-com {\n+                      config {\n+                          community-set-name openconfig-vrf-import-com;\n+                          community-member target:65100:9999;\n+                      }\n+                  }\n+              }\n+          }\n+      }\n+      policy-definitions {\n+          policy-definition openconfig-vrf-export {\n+              config {\n+                  name openconfig-vrf-export;\n+              }\n+              statements {\n+                  statement term1 {\n+                      conditions {\n+                          config {\n+                              install-protocol-eq DIRECTLY_CONNECTED;\n+                          }\n+                      }\n+                      actions {\n+                          config {\n+                              policy-result ACCEPT_ROUTE;\n+                          }\n+                          openconfig-bgp-policy:bgp-actions {\n+                              set-community {\n+                                  config {\n+                                      options ADD;\n+                                  }\n+                                  reference {\n+                                      config {\n+                                          community-set-ref openconfig-vrf-export-com;\n+                                      }\n+                                  }\n+                              }\n+                          }\n+                      }\n+                  }\n+              }\n+          }\n+          policy-definition openconfig-vrf-import {\n+              config {\n+                  name openconfig-vrf-import;\n+              }\n+              statements {\n+                  statement term1 {\n+                      conditions {\n+                          openconfig-bgp-policy:bgp-conditions {\n+                              config {\n+                                  community-set openconfig-vrf-import-com;\n+                              }\n+                          }\n+                      }\n+                      actions {\n+                          config {\n+                              policy-result ACCEPT_ROUTE;\n+                          }\n+                      }\n+                  }\n+              }\n+          }\n+      }\n+  }\n[edit openconfig-interfaces:interfaces interface lo0]\n+    subinterfaces {\n+        subinterface 2 {\n+            openconfig-if-ip:ipv4 {\n+                addresses {\n+                    address 2.2.2.2 {\n+                        config {\n+                            prefix-length 32;\n+                        }\n+                    }\n+                }\n+            }\n+        }\n+    }\n[edit]\n+  openconfig-network-instance:network-instances {\n+      network-instance openconfig-vrf {\n+          config {\n+              name oc-vrf;\n+              type L3VRF;\n+              enabled true;\n+              router-id 1.1.0.9;\n+              route-distinguisher 1.1.0.9:9999;\n+          }\n+          inter-instance-policies {\n+              apply-policy {\n+                  config {\n+                      import-policy openconfig-vrf-import;\n+                      export-policy openconfig-vrf-export;\n+                  }\n+              }\n+          }\n+          interfaces {\n+              interface lo0.2 {\n+                  config {\n+                      id lo0.2;\n+                      interface lo0;\n+                      subinterface 2;\n+                  }\n+              }\n+          }\n+      }\n+  }\"><pre class=\"notranslate\"><code>$ python3 load_config.py openconfig-create.xml xml mx204-83\n\n[edit]\n+  openconfig-routing-policy:routing-policy {\n+      defined-sets {\n+          openconfig-bgp-policy:bgp-defined-sets {\n+              community-sets {\n+                  community-set openconfig-vrf-export-com {\n+                      config {\n+                          community-set-name openconfig-vrf-export-com;\n+                          community-member target:65100:9999;\n+                      }\n+                  }\n+                  community-set openconfig-vrf-import-com {\n+                      config {\n+                          community-set-name openconfig-vrf-import-com;\n+                          community-member target:65100:9999;\n+                      }\n+                  }\n+              }\n+          }\n+      }\n+      policy-definitions {\n+          policy-definition openconfig-vrf-export {\n+              config {\n+                  name openconfig-vrf-export;\n+              }\n+              statements {\n+                  statement term1 {\n+                      conditions {\n+                          config {\n+                              install-protocol-eq DIRECTLY_CONNECTED;\n+                          }\n+                      }\n+                      actions {\n+                          config {\n+                              policy-result ACCEPT_ROUTE;\n+                          }\n+                          openconfig-bgp-policy:bgp-actions {\n+                              set-community {\n+                                  config {\n+                                      options ADD;\n+                                  }\n+                                  reference {\n+                                      config {\n+                                          community-set-ref openconfig-vrf-export-com;\n+                                      }\n+                                  }\n+                              }\n+                          }\n+                      }\n+                  }\n+              }\n+          }\n+          policy-definition openconfig-vrf-import {\n+              config {\n+                  name openconfig-vrf-import;\n+              }\n+              statements {\n+                  statement term1 {\n+                      conditions {\n+                          openconfig-bgp-policy:bgp-conditions {\n+                              config {\n+                                  community-set openconfig-vrf-import-com;\n+                              }\n+                          }\n+                      }\n+                      actions {\n+                          config {\n+                              policy-result ACCEPT_ROUTE;\n+                          }\n+                      }\n+                  }\n+              }\n+          }\n+      }\n+  }\n[edit openconfig-interfaces:interfaces interface lo0]\n+    subinterfaces {\n+        subinterface 2 {\n+            openconfig-if-ip:ipv4 {\n+                addresses {\n+                    address 2.2.2.2 {\n+                        config {\n+                            prefix-length 32;\n+                        }\n+                    }\n+                }\n+            }\n+        }\n+    }\n[edit]\n+  openconfig-network-instance:network-instances {\n+      network-instance openconfig-vrf {\n+          config {\n+              name oc-vrf;\n+              type L3VRF;\n+              enabled true;\n+              router-id 1.1.0.9;\n+              route-distinguisher 1.1.0.9:9999;\n+          }\n+          inter-instance-policies {\n+              apply-policy {\n+                  config {\n+                      import-policy openconfig-vrf-import;\n+                      export-policy openconfig-vrf-export;\n+                  }\n+              }\n+          }\n+          interfaces {\n+              interface lo0.2 {\n+                  config {\n+                      id lo0.2;\n+                      interface lo0;\n+                      subinterface 2;\n+                  }\n+              }\n+          }\n+      }\n+  }\n</code></pre></div>\n<p dir=\"auto\">The configuration has been successfully applied.</p>\n<h4 tabindex=\"-1\" dir=\"auto\"><a id=\"user-content-read\" class=\"anchor\" aria-hidden=\"true\" tabindex=\"-1\" href=\"#read\"><svg class=\"octicon octicon-link\" viewBox=\"0 0 16 16\" version=\"1.1\" width=\"16\" height=\"16\" aria-hidden=\"true\"><path d=\"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z\"></path></svg></a>Read</h4>\n<p dir=\"auto\">Now let's read the configuration we have just uploaded to the device:</p>\n<ul dir=\"auto\">\n<li>Interfaces subtree in the XML format</li>\n</ul>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 read_config.py -f 'interfaces' -m openconfig xml mx204-83\n&lt;interfaces&gt;\n  &lt;interface&gt;\n    &lt;name&gt;lo0&lt;/name&gt;\n    &lt;config&gt;\n      &lt;name&gt;lo0&lt;/name&gt;\n      &lt;type&gt;loopback&lt;/type&gt;\n      &lt;enabled&gt;true&lt;/enabled&gt;\n    &lt;/config&gt;\n    &lt;subinterfaces&gt;\n      &lt;subinterface&gt;\n        &lt;index&gt;2&lt;/index&gt;\n        &lt;ipv4&gt;\n          &lt;addresses&gt;\n            &lt;address&gt;\n              &lt;ip&gt;2.2.2.2&lt;/ip&gt;\n              &lt;config&gt;\n                &lt;prefix-length&gt;32&lt;/prefix-length&gt;\n              &lt;/config&gt;\n            &lt;/address&gt;\n          &lt;/addresses&gt;\n        &lt;/ipv4&gt;\n      &lt;/subinterface&gt;\n    &lt;/subinterfaces&gt;\n  &lt;/interface&gt;\n&lt;/interfaces&gt;\"><pre class=\"notranslate\"><code>$ python3 read_config.py -f 'interfaces' -m openconfig xml mx204-83\n&lt;interfaces&gt;\n  &lt;interface&gt;\n    &lt;name&gt;lo0&lt;/name&gt;\n    &lt;config&gt;\n      &lt;name&gt;lo0&lt;/name&gt;\n      &lt;type&gt;loopback&lt;/type&gt;\n      &lt;enabled&gt;true&lt;/enabled&gt;\n    &lt;/config&gt;\n    &lt;subinterfaces&gt;\n      &lt;subinterface&gt;\n        &lt;index&gt;2&lt;/index&gt;\n        &lt;ipv4&gt;\n          &lt;addresses&gt;\n            &lt;address&gt;\n              &lt;ip&gt;2.2.2.2&lt;/ip&gt;\n              &lt;config&gt;\n                &lt;prefix-length&gt;32&lt;/prefix-length&gt;\n              &lt;/config&gt;\n            &lt;/address&gt;\n          &lt;/addresses&gt;\n        &lt;/ipv4&gt;\n      &lt;/subinterface&gt;\n    &lt;/subinterfaces&gt;\n  &lt;/interface&gt;\n&lt;/interfaces&gt;\n</code></pre></div>\n<ul dir=\"auto\">\n<li>Routing-policy subtree in the SET format</li>\n</ul>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 read_config.py -f 'routing-policy' -m openconfig set mx204-83\n&lt;configuration-set&gt;\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-export-com config community-set-name openconfig-vrf-export-com\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-export-com config community-member target:65100:9999\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-import-com config community-set-name openconfig-vrf-import-com\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-import-com config community-member target:65100:9999\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export config name openconfig-vrf-export\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 conditions config install-protocol-eq DIRECTLY_CONNECTED\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions config policy-result ACCEPT_ROUTE\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions openconfig-bgp-policy:bgp-actions set-community config options ADD\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions openconfig-bgp-policy:bgp-actions set-community reference config community-set-ref openconfig-vrf-export-com\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import config name openconfig-vrf-import\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import statements statement term1 conditions openconfig-bgp-policy:bgp-conditions config community-set openconfig-vrf-import-com\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import statements statement term1 actions config policy-result ACCEPT_ROUTE\n&lt;/configuration-set&gt;\"><pre class=\"notranslate\"><code>$ python3 read_config.py -f 'routing-policy' -m openconfig set mx204-83\n&lt;configuration-set&gt;\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-export-com config community-set-name openconfig-vrf-export-com\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-export-com config community-member target:65100:9999\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-import-com config community-set-name openconfig-vrf-import-com\nset openconfig-routing-policy:routing-policy defined-sets openconfig-bgp-policy:bgp-defined-sets community-sets community-set openconfig-vrf-import-com config community-member target:65100:9999\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export config name openconfig-vrf-export\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 conditions config install-protocol-eq DIRECTLY_CONNECTED\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions config policy-result ACCEPT_ROUTE\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions openconfig-bgp-policy:bgp-actions set-community config options ADD\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements statement term1 actions openconfig-bgp-policy:bgp-actions set-community reference config community-set-ref openconfig-vrf-export-com\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import config name openconfig-vrf-import\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import statements statement term1 conditions openconfig-bgp-policy:bgp-conditions config community-set openconfig-vrf-import-com\nset openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-import statements statement term1 actions config policy-result ACCEPT_ROUTE\n&lt;/configuration-set&gt;\n</code></pre></div>\n<h4 tabindex=\"-1\" dir=\"auto\"><a id=\"user-content-update\" class=\"anchor\" aria-hidden=\"true\" tabindex=\"-1\" href=\"#update\"><svg class=\"octicon octicon-link\" viewBox=\"0 0 16 16\" version=\"1.1\" width=\"16\" height=\"16\" aria-hidden=\"true\"><path d=\"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z\"></path></svg></a>Update</h4>\n<p dir=\"auto\">The next action is the configuration modification. We will do the following:</p>\n<ul dir=\"auto\">\n<li>Create interface: ae83.4083</li>\n<li>Add inteface ae83.4083 to L3VPN openconfig-vrf</li>\n<li>Add a static route to L3VPN openconfig-vrf</li>\n<li>Add another term to export static routes from L3VPN openconfig-vrf</li>\n</ul>\n<p dir=\"auto\">To accomplish this, I will apply the XML configuration file <a href=\"https://github.com/agantonov/openconfig/blob/main/openconfig-update.xml\">openconfig-update.xml</a>:</p>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 load_config.py openconfig-update.xml xml mx204-83\n\n[edit openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements]\n       statement term1 { ... }\n+      statement term2 {\n+          conditions {\n+              config {\n+                  install-protocol-eq STATIC;\n+              }\n+          }\n+          actions {\n+              config {\n+                  policy-result ACCEPT_ROUTE;\n+              }\n+              openconfig-bgp-policy:bgp-actions {\n+                  set-community {\n+                      config {\n+                          options ADD;\n+                      }\n+                      reference {\n+                          config {\n+                              community-set-ref openconfig-vrf-export-com;\n+                          }\n+                      }\n+                  }\n+              }\n+          }\n+      }\n[edit openconfig-interfaces:interfaces]\n+   interface ae83 {\n+       config {\n+           name ae83;\n+           type ethernetCsmacd;\n+           enabled true;\n+       }\n+       subinterfaces {\n+           subinterface 4083 {\n+               openconfig-if-ip:ipv4 {\n+                   addresses {\n+                       address 83.83.83.83 {\n+                           config {\n+                               prefix-length 24;\n+                           }\n+                       }\n+                   }\n+               }\n+               openconfig-vlan:vlan {\n+                   match {\n+                       single-tagged {\n+                           config {\n+                               vlan-id 4083;\n+                           }\n+                       }\n+                   }\n+               }\n+           }\n+       }\n+   }\n[edit openconfig-network-instance:network-instances network-instance openconfig-vrf interfaces]\n+     interface ae83.4083 {\n+         config {\n+             id ae83.4083;\n+             interface ae83;\n+             subinterface 4083;\n+         }\n+     }\n[edit openconfig-network-instance:network-instances network-instance openconfig-vrf]\n+    protocols {\n+        protocol STATIC static-routes {\n+            static-routes {\n+                static 3.3.3.0/24 {\n+                    config {\n+                        prefix 3.3.3.0/24;\n+                    }\n+                    next-hops {\n+                        next-hop 83.83.83.1 {\n+                            config {\n+                                next-hop 83.83.83.1;\n+                            }\n+                        }\n+                    }\n+                }\n+            }\n+        }\n+    }\"><pre class=\"notranslate\"><code>$ python3 load_config.py openconfig-update.xml xml mx204-83\n\n[edit openconfig-routing-policy:routing-policy policy-definitions policy-definition openconfig-vrf-export statements]\n       statement term1 { ... }\n+      statement term2 {\n+          conditions {\n+              config {\n+                  install-protocol-eq STATIC;\n+              }\n+          }\n+          actions {\n+              config {\n+                  policy-result ACCEPT_ROUTE;\n+              }\n+              openconfig-bgp-policy:bgp-actions {\n+                  set-community {\n+                      config {\n+                          options ADD;\n+                      }\n+                      reference {\n+                          config {\n+                              community-set-ref openconfig-vrf-export-com;\n+                          }\n+                      }\n+                  }\n+              }\n+          }\n+      }\n[edit openconfig-interfaces:interfaces]\n+   interface ae83 {\n+       config {\n+           name ae83;\n+           type ethernetCsmacd;\n+           enabled true;\n+       }\n+       subinterfaces {\n+           subinterface 4083 {\n+               openconfig-if-ip:ipv4 {\n+                   addresses {\n+                       address 83.83.83.83 {\n+                           config {\n+                               prefix-length 24;\n+                           }\n+                       }\n+                   }\n+               }\n+               openconfig-vlan:vlan {\n+                   match {\n+                       single-tagged {\n+                           config {\n+                               vlan-id 4083;\n+                           }\n+                       }\n+                   }\n+               }\n+           }\n+       }\n+   }\n[edit openconfig-network-instance:network-instances network-instance openconfig-vrf interfaces]\n+     interface ae83.4083 {\n+         config {\n+             id ae83.4083;\n+             interface ae83;\n+             subinterface 4083;\n+         }\n+     }\n[edit openconfig-network-instance:network-instances network-instance openconfig-vrf]\n+    protocols {\n+        protocol STATIC static-routes {\n+            static-routes {\n+                static 3.3.3.0/24 {\n+                    config {\n+                        prefix 3.3.3.0/24;\n+                    }\n+                    next-hops {\n+                        next-hop 83.83.83.1 {\n+                            config {\n+                                next-hop 83.83.83.1;\n+                            }\n+                        }\n+                    }\n+                }\n+            }\n+        }\n+    }\n</code></pre></div>\n<h4 tabindex=\"-1\" dir=\"auto\"><a id=\"user-content-delete\" class=\"anchor\" aria-hidden=\"true\" tabindex=\"-1\" href=\"#delete\"><svg class=\"octicon octicon-link\" viewBox=\"0 0 16 16\" version=\"1.1\" width=\"16\" height=\"16\" aria-hidden=\"true\"><path d=\"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z\"></path></svg></a>Delete</h4>\n<p dir=\"auto\">The last CRUD function is Delete. We can remove the Openconfig configuration either with the XML <a href=\"https://github.com/agantonov/openconfig/blob/main/openconfig-delete.xml\">file</a> using the delete=\"delete\" attribute or using the ASCII <a href=\"https://github.com/agantonov/openconfig/blob/main/openconfig-delete.set\">text</a> and the \"delete:\" statement</p>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 load_config.py openconfig-delete.xml xml mx204-83\n\n[edit]\n-  openconfig-routing-policy:routing-policy {\n...\n(omitted for brevity)\n...\n-  }\n[edit openconfig-interfaces:interfaces interface lo0]\n-    subinterfaces {\n...\n(omitted for brevity)\n...\n-    }\n[edit]\n-  openconfig-network-instance:network-instances {\n...\n(omitted for brevity)\n...\n-  }\"><pre class=\"notranslate\"><code>$ python3 load_config.py openconfig-delete.xml xml mx204-83\n\n[edit]\n-  openconfig-routing-policy:routing-policy {\n...\n(omitted for brevity)\n...\n-  }\n[edit openconfig-interfaces:interfaces interface lo0]\n-    subinterfaces {\n...\n(omitted for brevity)\n...\n-    }\n[edit]\n-  openconfig-network-instance:network-instances {\n...\n(omitted for brevity)\n...\n-  }\n</code></pre></div>\n<p dir=\"auto\">ASCII text:</p>\n<div class=\"snippet-clipboard-content notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"$ python3 load_config.py openconfig-delete.set set mx204-83\n\n[edit]\n-  openconfig-routing-policy:routing-policy {\n...\n(omitted for brevity)\n...\n-  }\n-  openconfig-interfaces:interfaces {\n...\n(omitted for brevity)\n...\n-  }\n-  openconfig-network-instance:network-instances {\n...\n(omitted for brevity)\n...\n-  }\"><pre class=\"notranslate\"><code>$ python3 load_config.py openconfig-delete.set set mx204-83\n\n[edit]\n-  openconfig-routing-policy:routing-policy {\n...\n(omitted for brevity)\n...\n-  }\n-  openconfig-interfaces:interfaces {\n...\n(omitted for brevity)\n...\n-  }\n-  openconfig-network-instance:network-instances {\n...\n(omitted for brevity)\n...\n-  }\n</code></pre></div>\n<p dir=\"auto\">As a result, we succesfully demonstrated that Juniper devices can support CRUD operations with the Openconfig data model.</p>\n</article>","renderedFileInfo":null,"shortPath":null,"tabSize":8,"topBannersInfo":{"overridingGlobalFundingFile":false,"globalPreferredFundingPath":null,"repoOwner":"agantonov","repoName":"openconfig","showInvalidCitationWarning":false,"citationHelpUrl":"https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-on-github/about-citation-files","showDependabotConfigurationBanner":false,"actionsOnboardingTip":null},"truncated":false,"viewable":true,"workflowRedirectUrl":null,"symbols":{"timed_out":false,"not_analyzed":false,"symbols":[{"name":"OpenConfig CRUD with Juniper","kind":"section_3","ident_start":4,"ident_end":32,"extent_start":0,"extent_end":14879,"fully_qualified_name":"OpenConfig CRUD with Juniper","ident_utf16":{"start":{"line_number":0,"utf16_col":4},"end":{"line_number":0,"utf16_col":32}},"extent_utf16":{"start":{"line_number":0,"utf16_col":0},"end":{"line_number":379,"utf16_col":0}}},{"name":"Create","kind":"section_4","ident_start":2922,"ident_end":2928,"extent_start":2917,"extent_end":7446,"fully_qualified_name":"Create","ident_utf16":{"start":{"line_number":53,"utf16_col":5},"end":{"line_number":53,"utf16_col":11}},"extent_utf16":{"start":{"line_number":53,"utf16_col":0},"end":{"line_number":187,"utf16_col":0}}},{"name":"Read","kind":"section_4","ident_start":7451,"ident_end":7455,"extent_start":7446,"extent_end":10634,"fully_qualified_name":"Read","ident_utf16":{"start":{"line_number":187,"utf16_col":5},"end":{"line_number":187,"utf16_col":9}},"extent_utf16":{"start":{"line_number":187,"utf16_col":0},"end":{"line_number":236,"utf16_col":0}}},{"name":"Update","kind":"section_4","ident_start":10639,"ident_end":10645,"extent_start":10634,"extent_end":13713,"fully_qualified_name":"Update","ident_utf16":{"start":{"line_number":236,"utf16_col":5},"end":{"line_number":236,"utf16_col":11}},"extent_utf16":{"start":{"line_number":236,"utf16_col":0},"end":{"line_number":331,"utf16_col":0}}},{"name":"Delete","kind":"section_4","ident_start":13718,"ident_end":13724,"extent_start":13713,"extent_end":14879,"fully_qualified_name":"Delete","ident_utf16":{"start":{"line_number":331,"utf16_col":5},"end":{"line_number":331,"utf16_col":11}},"extent_utf16":{"start":{"line_number":331,"utf16_col":0},"end":{"line_number":379,"utf16_col":0}}}]}},"copilotInfo":null,"copilotAccessAllowed":false,"csrf_tokens":{"/agantonov/openconfig/branches":{"post":"2-1HmSGuoxfeeFe624za2H8i1oVpjO6FBkr8qNSUUXz4gBqLpm92KZWg3P6rNpX4oSlBfu9REly0CpOLrL2pjQ"},"/repos/preferences":{"post":"tIzvOjCGbJshHc-XtlOukbP6HAQb51nJNgO4fJ7v1hZ0JlmI4CSFIKKRHLnGbc21ujCpp4iAMK2OqcLBfXTi5w"}}},"title":"openconfig/README.md at main · agantonov/openconfig"}
>>>>>>> Stashed changes

# Template for a IPCM configuration file
ipcmconf_base = {
            "configFileVersion": "1.4.1",
            "localConfiguration": {
                "installationPath": "%(installpath)s/bin",
                "libraryPath": "%(installpath)s/lib",
                "logPath": "%(installpath)s/var/log",
                "consoleSocket": "%(installpath)s/var/run/ipcm-console.sock",
                "pluginsPaths": [
                        "%(installpath)s/lib/rinad/ipcp",
                        "/lib/modules/4.1.10-irati/extra"
                ]
                },

            "applicationToDIFMappings": [
                {
                    "encodedAppName": "rina.apps.echotime.server-1--",
                    "difName": "n.DIF"
                },
                {
                    "encodedAppName": "rina.apps.echotime.client-1--",
                    "difName": "n.DIF"
                },
                {
                    "encodedAppName": "rina.apps.echotime-2--",
                    "difName": "n.DIF"
                },
                {
                    "encodedAppName": "rina.apps.echotime.client-2--",
                    "difName": "n.DIF"
                }
            ],

            "ipcProcessesToCreate": [],
            "difConfigurations": [],
        }


# Template for a normal DIF configuration file
normal_dif_base =  {
    "difType" : "normal-ipc",
    "dataTransferConstants" : {
        "addressLength" : 2,
        "cepIdLength" : 2,
        "lengthLength" : 2,
        "portIdLength" : 2,
        "qosIdLength" : 2,
        "rateLength" : 4,
        "frameLength" : 4,
        "sequenceNumberLength" : 4,
        "ctrlSequenceNumberLength" : 4,
        "maxPduSize" : 10000,
        "maxPduLifetime" : 60000
    },

    "qosCubes" : [ {
            "name" : "unreliablewithflowcontrol",
            "id" : 1,
            "partialDelivery" : 'false',
            "orderedDelivery" : 'true',
            "efcpPolicies" : {
                "dtpPolicySet" : {
                    "name" : "default",
                    "version" : "0"
                },
                "initialATimer" : 300,
                "dtcpPresent" : 'true',
                "dtcpConfiguration" : {
                    "dtcpPolicySet" : {
                        "name" : "default",
                        "version" : "0"
                    },
                    "rtxControl" : 'false',
                    "flowControl" : 'true',
                    "flowControlConfig" : {
                        "rateBased" : 'false',
                        "windowBased" : 'true',
                        "windowBasedConfig" : {
                            "maxClosedWindowQueueLength" : 50,
                            "initialCredit" : 50
                        }
                    }
                }
            }
        }, {
            "name" : "reliablewithflowcontrol",
            "id" : 2,
            "partialDelivery" : 'false',
            "orderedDelivery" : 'true',
            "maxAllowableGap": 0,
            "efcpPolicies" : {
                "dtpPolicySet" : {
                    "name" : "default",
                    "version" : "0"
                },
                "initialATimer" : 300,
                "dtcpPresent" : 'true',
                "dtcpConfiguration" : {
                    "dtcpPolicySet" : {
                        "name" : "default",
                        "version" : "0"
                    },
                    "rtxControl" : 'true',
                    "rtxControlConfig" : {
                        "dataRxmsNmax" : 5,
                        "initialRtxTime" : 1000
                    },
                    "flowControl" : 'true',
                    "flowControlConfig" : {
                        "rateBased" : 'false',
                        "windowBased" : 'true',
                        "windowBasedConfig" : {
                            "maxClosedWindowQueueLength" : 50,
                            "initialCredit" : 50
                        }
                    }
                }
            }
        } ],

    "knownIPCProcessAddresses": [],

    "addressPrefixes" : [ {
            "addressPrefix" : 0,
            "organization" : "N.Bourbaki"
        }, {
            "addressPrefix" : 16,
            "organization" : "IRATI"
        } ],

    "rmtConfiguration" : {
        "pffConfiguration" : {
            "policySet" : {
                "name" : "default",
                "version" : "0"
            }
        },
        "policySet" : {
            "name" : "default",
            "version" : "1"
        }
    },

    "enrollmentTaskConfiguration" : {
        "policySet" : {
            "name" : "default",
            "version" : "1",
            "parameters" : [ {
                "name"  : "enrollTimeoutInMs",
                "value" : "10000"
            }, {
                "name"  : "watchdogPeriodInMs",
                "value" : "30000"
            }, {
                "name"  : "declaredDeadIntervalInMs",
                "value" : "120000"
            }, {
                "name"  : "neighborsEnrollerPeriodInMs",
                "value" : "30000"
            }, {
                "name"  : "maxEnrollmentRetries",
                "value" : "3"
            } ]
        }
     },

    "flowAllocatorConfiguration" : {
        "policySet" : {
            "name" : "default",
            "version" : "1"
        }
    },

    "namespaceManagerConfiguration" : {
        "policySet" : {
            "name" : "default",
            "version" : "1"
        }
    },

    "securityManagerConfiguration" : {
        "policySet" : {
            "name" : "default",
            "version" : "1"
        }
    },

    "resourceAllocatorConfiguration" : {
        "pduftgConfiguration" : {
            "policySet" : {
                "name" : "default",
                "version" : "0"
            }
        }
    },

    "routingConfiguration" : {
        "policySet" : {
            "name" : "link-state",
            "version" : "1",
            "parameters" : [ {
                    "name"  : "objectMaximumAge",
                    "value" : "10000"
                },{
                    "name"  : "waitUntilReadCDAP",
                    "value" : "5001"
                },{
                    "name"  : "waitUntilError",
                    "value" : "5001"
                },{
                    "name"  : "waitUntilPDUFTComputation",
                    "value" : "103"
                },{
                    "name"  : "waitUntilFSODBPropagation",
                    "value" : "101"
                },{
                    "name"  : "waitUntilAgeIncrement",
                    "value" : "997"
                },{
                    "name"  : "routingAlgorithm",
                    "value" : "Dijkstra"
                }]
        }
    }
}


{
    "companies":{
        "cyta":"images/cyta.png",
        "forthnet":"images/forthnet.gif",
        "hol":"images/hol.gif",
        "netone":"images/netone.gif",
        "ontelecoms":"images/ontelecoms.gif",
        "ote":"images/ote.gif",
        "tellas":"images/tellas.gif",
        "vivodi":"images/vivodi.gif",
        "cosmoline":"images/cosmoline.png"
    },
    "configurations":{
        "Forthnet 2play":{"company":"forthnet","assets":["forthnet-2play"]},
        "Hol double-play":{"company":"hol","assets":["hol-double-play"]},
        "Net One Value Pack":{"company":"netone","assets":["netone-value-pack"]},
        "Net One Value Pack + 60 κινητά":{"company":"netone","assets":["netone-value-pack","netone-60-kinhta"]},
        "On Double Play":{"company":"ontelecoms","assets":["on-double-play"]},
        "On Double Play 8 GR":{"company":"ontelecoms","assets":["on-double-play-8-gr"]},
        "On Double Play 24 Unlimited Plus":{"company":"ontelecoms","assets":["on-double-play-24-unlimited-plus"]},
        "On Double Play + 220 εθνικά":{"company":"ontelecoms","assets":["on-double-play","on-220-ethnika"]},
        "On Double Play + 60 κινητά":{"company":"ontelecoms","assets":["on-double-play","on-60-kinhta"]},
        "On Double Play 8 GR + 60 κινητά":{"company":"ontelecoms","assets":["on-double-play-8-gr","on-60-kinhta"]},
        "On Double Play + 220 εθνικά + 60 κινητά":{"company":"ontelecoms","assets":["on-double-play","on-220-ethnika","on-60-kinhta"]},
        "ΟΤΕ PSTN + ConnX Δίοδος 2Mbps":{"company":"ote","assets":["ote-pstn","connx-diodos-2mbps"]},
        "ΟΤΕ ISDN + ConnX Δίοδος 2Mbps":{"company":"ote","assets":["ote-isdn","connx-diodos-2mbps"]},
        "WIND Double Play S":{"company":"tellas","assets":["wind-double-play-s"]},
        "WIND Double Play M":{"company":"tellas","assets":["wind-double-play-m"]},
        "WIND Double Play L":{"company":"tellas","assets":["wind-double-play-l"]},
        "Vivodi Telefonet":{"company":"vivodi","assets":["vivodi-telefonet"]},
        "Vivodi Telefonet+":{"company":"vivodi","assets":["vivodi-telefonet+"]},
        "Cosmoline ανά κλήση + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-ana-klhsh","connx-diodos-2mbps"]},
        "Cosmoline βασικό + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-basiko","connx-diodos-2mbps"]},
        "Cosmoline basic 200 + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-basic-200","connx-diodos-2mbps"]},
        "Cosmoline σταθερά κινητά 100 + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-stathera-kinhta-100","connx-diodos-2mbps"]},
        "Cosmoline σταθερά κινητά 200 + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-stathera-kinhta-200","connx-diodos-2mbps"]},
        "Cosmoline σταθερά κινητά 300 + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-stathera-kinhta-300","connx-diodos-2mbps"]},
        "Cosmoline απεριόριστα σταθερά + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-aperiorista-stathera","connx-diodos-2mbps"]},
        "Cosmoline σταθερά 400 + ConnX Δίοδος 2Mbps":{"company":"cosmoline","assets":["cosmoline-stathera-400","connx-diodos-2mbps"]}
    },
    "assets":{
        "ote-pstn":{
            "monthly_charges":12.40,
            "free":{
              "local_and_long_distance":{"secs":0,"min_duration":0,"step":0},
              "mobile":{"secs":0,"min_duration":0,"step":0}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTF  ","hours":"        890123456789    ","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000433}]},
                        {"days":"MTWTF  ","hours":"01234567            0123","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000417}]},
                        {"days":"     S ","hours":"012345678901234567890123","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000417}]},
                        {"days":"      S","hours":"012345678901234567890123","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000400}]}
                    ]
                },
                "long_distance":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTF  ","hours":"        890123456789    ","tiered_fee":[{"len":25,"step":25,"charge":0.026}, {"len":-1,"step":1,"charge":0.001033}]},
                        {"days":"MTWTF  ","hours":"01234567            0123","tiered_fee":[{"len":28,"step":28,"charge":0.026}, {"len":-1,"step":1,"charge":0.000917}]},
                        {"days":"     S ","hours":"012345678901234567890123","tiered_fee":[{"len":28,"step":28,"charge":0.026}, {"len":-1,"step":1,"charge":0.000917}]},
                        {"days":"      S","hours":"012345678901234567890123","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000400}]}
                    ]
                },
                "mobile":{
                    "use_free":"mobile",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":1,"charge":0.001615}]}
                    ]
                }
            }
        },
        "ote-isdn":{
            "copy_of":"ote-pstn",
            "changes":{
                "monthly_charges":"+3.5"
            }
        },
        "ote-stathera-120":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+3",
                "free":{"local_and_long_distance":{"mins":120,"min_duration":0,"step":60}}
            }
        },
        "ote-stathera-240":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+5.84",
                "free":{"local_and_long_distance":{"mins":240,"min_duration":0,"step":60}}
            }
        },
        "ote-stathera-480":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+11.597",
                "free":{"local_and_long_distance":{"mins":480,"min_duration":0,"step":60}}
            }
        },
        "ote-kinhta-30":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+2.605",
                "free":{"mobile":{"mins":30,"min_duration":30,"step":1}}
            }
        },
        "ote-kinhta-60":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+4.874",
                "free":{"mobile":{"mins":60,"min_duration":30,"step":1}}
            }
        },
        "ote-kinhta-120":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+9.664",
                "free":{"mobile":{"mins":120,"min_duration":30,"step":1}}
            }
        },
        "ote-kinhta-240":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+18.487",
                "free":{"mobile":{"mins":240,"min_duration":30,"step":1}}
            }
        },
        "ote-kinhta-480":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+35.714",
                "free":{"mobile":{"mins":480,"min_duration":30,"step":1}}
            }
        },
        "ote-stathera-kinhta-180":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+3.852",
                "free":{
                    "local_and_long_distance":{"mins":160,"min_duration":0,"step":60},
                    "mobile":{"mins":20,"min_duration":0,"step":60}
                },
                "categories":{
                    "local":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.026}]}
                        ]
                    },
                    "long_distance":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.026}]}
                        ]
                    }
                }
            }
        },
        "ote-stathera-kinhta-300":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+7.03",
                "free":{
                    "local_and_long_distance":{"mins":250,"min_duration":0,"step":60},
                    "mobile":{"mins":50,"min_duration":0,"step":60}
                },
                "categories":{
                    "local":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.026}]}
                        ]
                    },
                    "long_distance":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.026}]}
                        ]
                    }
                }
            }
        },
        "ote-olh-mera-60-kinhta":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+12.4",
                "free":{
                    "local_and_long_distance":{"mins":99999999,"min_duration":0,"step":60},
                    "mobile":{"mins":60,"min_duration":0,"step":1}
                }
            }
        },
        "ote-brady-sk":{
            "addon_to":["ote-pstn","ote-isdn"],
            "changes":{
                "monthly_charges":"+6.555",
                "categories":{
                    "local":{
                        "datetime":[
                            {"days":"MTWTF  ","hours":"        890123456789    ","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000433}]},
                            {"days":"MTWTF  ","hours":"01234567            0123","tiered_fee":[{"len":-1,"step":60,"charge":0}]},
                            {"days":"     SS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0}]}
                        ]
                    },
                    "long_distance":{
                        "datetime":[
                            {"days":"MTWTF  ","hours":"        890123456789    ","tiered_fee":[{"len":120,"step":60,"charge":0.026},{"len":-1,"step":1,"charge":0.000433}]},
                            {"days":"MTWTF  ","hours":"01234567            0123","tiered_fee":[{"len":-1,"step":60,"charge":0}]},
                            {"days":"     SS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0}]}
                        ]
                    }
                }
            }
        },
        "connx-diodos-2mbps":{
            "addon_to":["ote-pstn","ote-isdn","cosmoline-ana-klhsh","cosmoline-basiko","cosmoline-basic-200","cosmoline-stathera-kinhta-100","cosmoline-stathera-kinhta-200","cosmoline-stathera-kinhta-300","cosmoline-aperiorista-stathera","cosmoline-stathera-400"],
            "changes":{
                "monthly_charges":"+10"
            }
        },
        "various-unlimited":{
            "free":{
                "local_and_long_distance":{"mins":99999999,"min_duration":0,"step":60},
                "mobile":{"mins":60,"min_duration":0,"step":60}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance"
                },
                "long_distance":{
                    "use_free":"local_and_long_distance"
                },
                "mobile":{
                    "use_free":"mobile"
                }
            }
        },
        "forthnet-2play":{
            "copy_of":"various-unlimited",
            "changes":{
                "monthly_charges":33.5285,
                "categories":{
                    "mobile":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.131870}]}
                        ]
                    }
                }
            }
        },
        "hol-double-play":{
            "copy_of":"various-unlimited",
            "changes":{
                "monthly_charges":33.4960,
                "categories":{
                    "mobile":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.138699}]}
                        ]
                    }
                }
            }
        },
        "netone-value-pack":{
            "copy_of":"various-unlimited",
            "changes":{
                "monthly_charges":31.8699,
                "free":{
                    "mobile":{"mins":0,"min_duration":0,"step":0}
                },
                "categories":{
                    "mobile":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":30,"step":30,"charge":0.057561},{"len":-1,"step":1,"charge":0.001919}]}
                        ]
                    }
                }
            }
        },
        "netone-60-kinhta":{
            "addon_to":"netone-value-pack",
            "changes":{
                "monthly_charges":"+5.2033",
                "free":{
                    "mobile":{"mins":60,"min_duration":0,"step":60}
                }
            }
        },
        "on-double-play":{
            "monthly_charges":16.4472,
            "free":{
              "local_and_long_distance":{"secs":0,"min_duration":0,"step":0},
              "mobile":{"secs":0,"min_duration":0,"step":0}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":60,"step":60,"charge":0.023496},{"len":-1,"step":1,"charge":0.000392}]}
                    ]
                },
                "long_distance":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":60,"step":60,"charge":0.023496},{"len":-1,"step":1,"charge":0.000392}]}
                    ]
                },
                "mobile":{
                    "use_free":"mobile",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":60,"step":60,"charge":0.137805},{"len":-1,"step":1,"charge":0.002297}]}
                    ]
                }
            }
        },
        "on-double-play-plus":{
            "copy_of":"on-double-play",
            "changes":{
                "monthly_charges":20.0813
            }
        },
        "on-double-play-8-gr":{
            "copy_of":"on-double-play",
            "changes":{
                "monthly_charges":21.7561,
                "free":{
                    "local_and_long_distance":{"mins":99999999,"min_duration":0,"step":60}
                }
            }
        },
        "on-double-play-24-gr":{
            "copy_of":"on-double-play-8-gr",
            "changes":{
                "monthly_charges":24.2927
            }
        },
        "on-double-play-24-unlimited":{
            "copy_of":"on-double-play-24-gr",
            "changes":{
                "monthly_charges":26.8130
            }
        },
        "on-double-play-24-unlimited-plus":{
            "copy_of":"on-double-play-24-unlimited",
            "changes":{
                "monthly_charges":33.5285,
                "free":{
                  "mobile":{"mins":60,"min_duration":0,"step":60}
                }
            }
        },
        "on-220-ethnika":{
            "addon_to":["on-double-play","on-double-play-plus"],
            "changes":{
                "monthly_charges":"+1.6829",
                "free":{
                    "local_and_long_distance":{"mins":220,"min_duration":0,"step":60}
                }
            }
        },
        "on-60-kinhta":{
            "addon_to":["on-double-play","on-double-play-plus","on-double-play-8-gr","on-double-play-24-gr","on-double-play-24-unlimited"],
            "changes":{
                "monthly_charges":"+5.8862",
                "free":{
                    "mobile":{"mins":60,"min_duration":0,"step":60}
                }
            }
        },
        "wind-double-play-s":{
            "monthly_charges":19.2439,
            "free":{
              "local_and_long_distance":{"secs":0,"min_duration":0,"step":0},
              "mobile":{"secs":0,"min_duration":0,"step":0}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.025041}]}
                    ]
                },
                "long_distance":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.044106}]}
                    ]
                },
                "mobile":{
                    "use_free":"mobile",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":60,"charge":0.139024}]}
                    ]
                }
            }
        },
        "wind-double-play-m":{
            "copy_of":"wind-double-play-s",
            "changes":{
                "monthly_charges":27.6423,
                "free":{
                    "local_and_long_distance":{"mins":99999999,"min_duration":0,"step":60}
                }
            }
        },
        "wind-double-play-l":{
            "copy_of":"wind-double-play-m",
            "changes":{
                "monthly_charges":33.5285,
                "free":{
                    "mobile":{"mins":60,"min_duration":0,"step":60}
                }
            }
        },
        "vivodi-telefonet":{
            "monthly_charges":15.00,
            "free":{
              "local_and_long_distance":{"mins":180,"min_duration":0,"step":60},
              "mobile":{"secs":0,"min_duration":0,"step":0}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":120,"step":60,"charge":0.023008},{"len":-1,"step":1,"charge":0.000383}]}
                    ]
                },
                "long_distance":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":1,"charge":0.000717}]}
                    ]
                },
                "mobile":{
                    "use_free":"mobile",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":60,"step":60,"charge":0.141138},{"len":-1,"step":1,"charge":0.002352}]}
                    ]
                }
            }
        },
        "vivodi-telefonet+":{
            "copy_of":"vivodi-telefonet",
            "changes":{
                "monthly_charges":27.6504,
                "free":{
                    "local_and_long_distance":{"mins":99999999,"min_duration":0,"step":60}
                }
            }
        },
        "cosmoline-ana-klhsh":{
            "monthly_charges":13.96,
            "free":{
              "local_and_long_distance":{"secs":0,"min_duration":0,"step":0},
              "mobile":{"secs":0,"min_duration":0,"step":0}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":99999999,"charge":0.1476}]}
                    ]
                },
                "long_distance":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":99999999,"charge":0.1476}]}
                    ]
                },
                "mobile":{
                    "use_free":"mobile",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":1,"charge":0.001615}]}
                    ]
                }
            }
        },
        "cosmoline-basiko":{
            "monthly_charges":11.6992,
            "free":{
              "local_and_long_distance":{"mins":60,"min_duration":0,"step":1},
              "mobile":{"secs":0,"min_duration":0,"step":0}
            },
            "categories":{
                "local":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":120,"step":60,"charge":0.024748},{"len":-1,"step":1,"charge":0.000412}]}
                    ]
                },
                "long_distance":{
                    "use_free":"local_and_long_distance",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":1,"charge":0.000412}]}
                    ]
                },
                "mobile":{
                    "use_free":"mobile",
                    "datetime":[
                        {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":1,"charge":0.001615}]}
                    ]
                }
            }
        },
        "cosmoline-basic-200":{
            "copy_of":"cosmoline-basiko",
            "changes":{
                "monthly_charges":12.3984,
                "free":{
                    "local_and_long_distance":{"mins":200,"min_duration":0,"step":1}
                },
                "categories":{
                    "local":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":120,"step":60,"charge":0.023902},{"len":-1,"step":1,"charge":0.000398}]}
                        ]
                    },
                    "long_distance":{
                        "datetime":[
                            {"days":"MTWTFSS","hours":"012345678901234567890123","tiered_fee":[{"len":-1,"step":1,"charge":0.000398}]}
                        ]
                    }
                }
            }
        },
        "cosmoline-stathera-kinhta-100":{
            "copy_of":"cosmoline-basiko",
            "changes":{
                "monthly_charges":13.7398,
                "free":{
                    "local_and_long_distance":{"mins":85,"min_duration":0,"step":1},
                    "mobile":{"mins":15,"min_duration":0,"step":1}
                }
            }
        },
        "cosmoline-stathera-kinhta-200":{
            "copy_of":"cosmoline-basiko",
            "changes":{
                "monthly_charges":16.7236,
                "free":{
                    "local_and_long_distance":{"mins":180,"min_duration":0,"step":1},
                    "mobile":{"mins":20,"min_duration":0,"step":1}
                }
            }
        },
        "cosmoline-stathera-kinhta-300":{
            "copy_of":"cosmoline-basiko",
            "changes":{
                "monthly_charges":25.1301,
                "free":{
                    "local_and_long_distance":{"mins":220,"min_duration":0,"step":1},
                    "mobile":{"mins":80,"min_duration":0,"step":1}
                }
            }
        },
        "cosmoline-aperiorista-stathera":{
            "copy_of":"cosmoline-basiko",
            "changes":{
                "monthly_charges":28.8618,
                "free":{
                    "local_and_long_distance":{"mins":99999999,"min_duration":0,"step":60}
                }
            }
        },
        "cosmoline-stathera-400":{
            "copy_of":"cosmoline-basiko",
            "changes":{
                "monthly_charges":25.1301,
                "free":{
                    "local_and_long_distance":{"mins":400,"min_duration":0,"step":1}
                }
            }
        }
    }
}
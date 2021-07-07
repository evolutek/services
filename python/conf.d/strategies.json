{
  "goals": [
    {
      "name": "get_buoys_1-2",
      "position": {
        "x": 800,
        "y": 534.25
      },
      "theta": "- pi / 6",
      "actions": [
        {
          "fct": "pumps_get",
          "handler": "robot",
          "args": {
            "ids": [3, 5]
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 1200,
            "y": 345.35
          }
        }
      ]
    },
    {
      "name": "get_buoys_3-4",
      "position": {
        "x": 635,
        "y": 255
      },
      "theta": "7*pi/8",
      "actions": [
        {
          "fct": "pumps_get",
          "handler": "robot",
          "args": {
            "ids": [1, 6]
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 430,
            "y": 350
          }
        }
      ]
    },
    {
      "name": "get_buoys_5-6",
      "position": {
        "x": 223,
        "y": 450
      },
      "theta": "pi/2",
      "actions": [
        {
          "fct": "pumps_get",
          "handler": "robot",
          "args": {
            "ids": [2]
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 223,
            "y": 590
          }
        },
        {
          "fct": "pumps_get",
          "handler": "robot",
          "args": {
            "ids": [4]
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 340,
            "y": 910
          }
        },
        {
          "fct": "front_arm_close",
          "handler": "robot"
        }
      ]
    },
    {
      "name": "get_buoys_7-8",
      "position": {
        "x": 900,
        "y": 280
      },
      "actions": [
        {
          "fct": "pumps_get",
          "handler": "robot",
          "args": {
            "ids": [1, 3]
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 845,
            "y": 1050
          }
        },
        {
          "fct": "pumps_get",
          "handler": "robot",
          "args": {
            "ids": [4, 5]
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 1150,
            "y": 1280
          }
        },
        {
          "fct": "pumps_drop",
          "handler": "robot",
          "args": {
            "ids": [3, 5]
          }
        },
        {
          "fct": "front_arm_close",
          "handler": "robot"
        }
      ]
    },
    {
      "name": "start_lighthouse",
      "position": {
        "x": 250,
        "y": 330
      },
      "theta": 0,
      "score": 15,
      "actions": [
        {
          "fct": "start_lighthouse",
          "handler": "robot",
          "score": 15
        }
      ]
    },
    {
      "name": "get_top_reef",
      "position": {
        "x": 250,
        "y": 887.5
      },
      "theta": 0,
      "actions": [
        {
          "fct": "recalibration",
          "handler": "robot",
          "args": {
            "y": false,
            "y_sensor": "right"
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 250,
            "y": 887.5
          }
        },
        {
          "fct": "goth",
          "args": {
            "theta": "0"
          }
        },
        {
          "fct": "get_reef",
          "handler": "robot"
        }
      ]
    },
    {
      "name": "get_bottom_reef",
      "position": {
        "x": 1637.5,
        "y": 250
      },
      "theta": "pi/2",
      "actions": [
        {
          "fct": "recalibration",
          "handler": "robot",
          "args": {
            "x": false,
            "x_sensor": "right"
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 1637.5,
            "y": 250
          }
        },
        {
          "fct": "goth",
          "args": {
            "theta": "pi/2"
          }
        },
        {
          "fct": "get_reef",
          "handler": "robot"
        }
      ]
    },
    {
      "name": "push_windsocks",
      "position": {
        "x": 1700,
        "y": 300
      },
      "score": 15,
      "actions": [
        {
          "fct": "goth",
          "handler": "robot",
          "args": {
            "theta": "3*pi/4"
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 1825,
            "y": 175
          }
        },
        {
          "fct": "goth",
          "handler": "robot",
          "args": {
            "theta": "pi/2"
          }
        },
        {
          "fct": "push_windsocks",
          "handler": "robot",
          "score": 15
        },
        {
          "fct": "goth",
          "args": {
            "theta": "pi / 3"
          }
        },
        {
          "fct": "goto",
          "args": {
            "x": 1800,
            "y": 400
          }
        }
      ]
    },
    {
      "name" : "drop_start_sorting",
      "position": {
        "x": 300,
        "y": 300
      },
      "theta": "pi / 2",
      "score": 30,
      "actions": [
        {
            "fct": "goto",
            "args": {
                "x": 300,
                "y": 150
            }
        },
        {
          "fct": "drop_start",
          "handler": "robot",
          "score": 30
        }
      ]
    },
    {
      "name": "drop_center_sorting",
      "position": {
        "x":  1400,
        "y":  700
      },
      "actions": [
        {
          "fct": "goto_avoid",
          "handler": "robot",
          "args": {
            "x": 1400,
            "y": 1705
          }
        },
        {
          "fct": "drop_center",
          "handler": "robot"
        }
      ]
    },
    {
      "name": "pmi_starting_sleep",
      "position": {
        "x": 620,
        "y": 255
      },
      "actions": [
        {
          "fct": "sleep",
          "args": {
            "time": 0.5
          }
        }
      ]
    },
    {
      "name": "goto_anchorage",
      "position": {
        "x": 800,
        "y": 700
      },
      "actions": [
        {
          "fct": "goto_anchorage",
          "handler": "robot"
        }
      ]
    }
  ],
  "strategies": [
    {
      "name": "normal_pal",
      "goals": [
        "get_buoys_7-8",
        "get_bottom_reef",
        "push_windsocks",
        "drop_center_sorting",
        "goto_anchorage"
      ],
      "available": ["pal"],
      "use_pathfinding": false
    },
    {
      "name": "normal_pmi",
      "goals": [
        "pmi_starting_sleep",
        "get_buoys_3-4",
        "start_lighthouse",
        "get_buoys_5-6",
        "get_top_reef",
        "get_buoys_1-2",
        "drop_start_sorting",
        "goto_anchorage"
      ],
      "available": ["pmi"],
      "use_pathfinding": false
    },
    {
      "name": "homologation_pmi",
      "goals": [
        "pmi_starting_sleep",
	"get_buoys_3-4",
	"start_lighthouse"
      ],
      "available": ["pmi"],
      "use_pathfinding": false
    },
    {

      "name": "homologation_pal",
      "goals": [
        "get_buoys_7-8",
        "push_windsocks"
      ],
      "available": ["pal"],
      "use_pathfinding": false
    }
  ],
  "starting_pos": {
    "pal": {
      "x": 900,
      "y": 270,
      "theta": "pi/2"
    },
    "pmi": {
      "x": 630,
      "y": 255,
      "theta": "pi"
    }
  }
}

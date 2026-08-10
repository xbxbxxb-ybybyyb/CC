
md_cert_tpl_prod = '''{
    "generate_date": "20250102",
    "fast_template_prd_sz": {
        "sdk-login-mode": 2,
        "sdk-remote-login": {
            "sdk-login-user": "temp_user_sz",
            "sdk-login-pwd": "temp_password_sz",
            "sdk-login-timeout": 2,
            "sdk-remote-login-aurl": "http://168.9.100.93:18088/icontrol/userConfig/getUserConfig",
            "sdk-remote-login-burl": "http://168.15.25.143:18088/icontrol/userConfig/getUserConfig"
        },
        "sdk-log-level": 0,
        "sdk-network-interface": "temp_interface_sz",
        "sdk-network-interface-mtu": 1500,
        "sdk-network-protocol": "udp",
        "sdk-network-configs": [
            {
                "sdk-bind-cpuid": 46,
                "sdk-network-filters": [
                    {
                        "sdk-dest-host-ip": "238.0.8.1",
                        "sdk-dest-port": 22001
                    }
                ]
            }
        ],
        "sdk-select-configs": {
            "sdk-cache-switch": 0,
            "sdk-data-type": 2
        }
    },
    "fast_template_prd_sh": {
        "sdk-login-mode": 2,
        "sdk-remote-login": {
            "sdk-login-user": "temp_user_sh",
            "sdk-login-pwd": "temp_password_sh",
            "sdk-login-timeout": 2,
            "sdk-remote-login-aurl": "http://168.9.100.93:18088/icontrol/userConfig/getUserConfig",
            "sdk-remote-login-burl": "http://168.15.25.143:18088/icontrol/userConfig/getUserConfig"
        },
        "sdk-log-level": 0,
        "sdk-network-interface": "temp_interface_sh",
        "sdk-network-interface-mtu": 1500,
        "sdk-network-protocol": "udp",
        "sdk-network-configs": [
            {
                "sdk-bind-cpuid": 46,
                "sdk-network-filters": [
                    {
                        "sdk-dest-host-ip": "233.57.1.103",
                        "sdk-dest-port": 38103
                    }
                ]
            }
        ],
        "sdk-select-configs": {
            "sdk-cache-switch": 0,
            "sdk-data-type": 1
        }
    },
    "udp_template_prd": {
        "udp_ip": "168.9.100.93",
        "udp_port": 18088,
        "udp_backup": [
            {
                "udp_ip": "168.9.65.25",
                "udp_port": 18088
            },
            {
                "udp_ip": "168.15.25.143",
                "udp_port": 18088
            },
            {
                "udp_ip": "168.15.25.144",
                "udp_port": 18088
            }
        ],
        "tcp_ip": "168.7.17.37",
        "tcp_port": 9662,
        "tcp_backup": [
            {
                "tcp_ip": "168.7.17.38",
                "tcp_port": 9662
            }
        ]
    },
    "udp_template_sim": {
        "udp_ip": "168.62.5.47",
        "udp_port": 18088,
        "udp_backup": [
            {
                "udp_ip": "168.62.5.48",
                "udp_port": 18088
            }
        ],
        "tcp_ip": "168.62.5.42",
        "tcp_port": 9662,
        "tcp_backup": [
            {
                "tcp_ip": "168.62.5.43",
                "tcp_port": 9662
            }
        ]
    },
    "account": {
        "503304": {
            "environment": "prd",
            "udp": {
                "user": "USERATSQUANTUDP13",
                "password": "a3._+wC79a57J",
                "interface_ip": "100.68.84.44"
            }
        },
        "503106": {
            "environment": "prd",
            "udp": {
                "user": "JQUSERATSQUANTUDP59",
                "password": "a7qh._c+79d97",
                "interface_ip": "100.68.59.38"
            }
        }
    }
}
'''

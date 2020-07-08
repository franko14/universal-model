VARIABLES = {
        'solar' : 
        {
            'fcst' : [
                'alb_rad',
                'alhfl_s',
                'asob_s',
                'asob_t',
                'aswdifd_s',
                'aswdir_s',
                ],
            'hist' : [
                'ALB_RAD',
                'ALHFL_S',
                'ASOB_S',
                'ASOB_T',
                'Surface_down_solar'
                ]
        },
        'wind' : 
        {
            'fcst' : [
                '57u',
                '57v',
                '58t',
                'pmsl',
                'relhum_150',
                ],
            'hist' : [
                'wind_150',
                't_100m',
                'pmsl',
                'relhum_150m'
            ]
        },
        'protiodchylka':
        {
            'fcst' : [
                't2m',
                ],
            'hist' : [
                't2m',
                ]
        },
        }
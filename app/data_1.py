from graph.base_define import Shape

data = {
    Shape.entity.value: {
        "suppliers": {
            "columns": ["sno", "sname", "status", "city"],
            "headnoun": "sname",
            "surrogate": "sno",
            "modifiers": ["status", "city"],
            "similar_of_table": [
                'suppliers', 'by', 'supplied'
            ],
            "similar_of_column": {
                "sno": [
                    'suppliers number', 'number'
                ],
                "sname": [
                    'suppliers', 'suppliers name', 'Clark', 'sname'
                ],
                "status": [
                    'status number', '10', '20', '30'
                ],
                "city": [
                    'in', 'city', 'London', 'city name'
                ]
            },
            "n": {
                "sno": [
                    'parts'
                ],
                "sname": [
                ],
                "status": [
                ],
                "city": [
                ]
            },
            "values": [
                ["S1", "Smith","20","London"],
                ["S2", "Jones","10","Paris"],
                ["S3", "Blake","30","Paris"],
                ["S4", "Clark","20","London"],
                ["S5", "Adames","30","Taipei"],
            ],
        },
        "parts": {
            "columns": ["pno", "pname", "color", "weight", "city"],
            "headnoun": "pname",
            "surrogate": "pno",
            "modifiers": ["color", "weight", "city"],
            "similar_of_table": [
                'parts', 'part'
            ],
            "similar_of_column": {
                "pno": [
                    'part number', 'number'
                ],
                "pname": [
                    'part name', 'Screw', 'Cam', 'Cog', 'Bolt', 'Nuts'
                ],
                "weight": [
                    'weight', '12', '14', '17', '19'
                ],
                "color": [
                    'color', 'green', 'blue'
                ],
                "city": [
                    'city', 'stored', 'in'
                ]
            },
            "n": {
                "pno": [
                ],
                "pname": [
                ],
                "weight": [
                ],
                "color": [
                ],
                "city": [
                ]
            },
            "values": [
                ["P1", "Nuts","Red","12","London"],
                ["P2", "Bolt","Green","17","Paris"],
                ["P3", "Screw","Blue","17","Rome"],
                ["P4", "Screw","Red","14","London"],
                ["P5", "Cam","Blue","12","Paris"],
                ["P6", "Cog","Red","19","London"],
            ],
        },
    },
    Shape.diamond.value: {
        "shipments": {
            "columns": ["sno", "pno", "qty"],
            "subject": {
                "shape": Shape.entity.value,
                "name": "suppliers",
                "key": "sno",
            },
            "object": {
                "shape": Shape.entity.value,
                "name": "parts",
                "key": "pno",
            },
            "modifiers": ["qty"],
            "similar_of_table": [
                'supply', 'provide', 'offer', 'supplied'
            ],
            "similar_of_column": {
                "sno": [
                    'S1', 'S2', 'S3', 'S4'
                ],
                "pno": [
                    'P1', 'P2', 'P3', 'P4', 'P5', 'P6'
                ],
                "qty": [
                    'quantity', '100', '200', '300', '400'
                ],
            },
            "n": {
                "sno": [
                ],
                "pno": [
                ],
                "qty": [
                ],
            },
            "values": [
                ["S1", "P1","300"],
                ["S1", "P2","200"],
                ["S1", "P3","400"],
                ["S1", "P4","200"],
                ["S1", "P5","100"],
                ["S1", "P6","100"],
                ["S2", "P1","300"],
                ["S2", "P2","400"],
                ["S3", "P2","200"],
                ["S4", "P2","200"],
                ["S4", "P4","300"],
                ["S4", "P5","400"],
            ],
        },
    },
}
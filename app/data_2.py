from graph.base_define import Shape

data = {
    Shape.entity.value: {
        "teacher": {
            "columns": ['tno', 'tname', 'dept'],
            "headnoun": "tname",
            "surrogate": 'tno',
            "modifiers": ["dept"],
            "similar_of_table": [
                
            ],
            "similar_of_column": {
                "tno": [

                ],
                "tname": [

                ],
                "dept": [

                ]
            },
            "values": [
                ['T1', 'Frank', 'IM'],
                ['T2', 'Annie', 'CS']
            ],
        },
        "student": {
            "columns":  ['sno', 'sname', 'major', 'year'],
            "headnoun": "sname",
            "surrogate": "sno",
            "modifiers": ['major', 'year'],
            "similar_of_table": [

            ],
            "similar_of_column": {
                "sno": [

                ],
                "sname": [

                ],
                "major": [

                ],
                "year": [

                ],
            },
            "values": [
                ['S1', 'Claire', 'CS', 2022],
                ['S2', 'Ryan', 'IM', 2022],
                ['S3', 'George', 'IM', 2022],
                ['S4', 'Nancy', 'IM', 2023],
                ['S5', 'Eric', 'CS', 2023],
            ],
        },
        "course": {
            "columns":  ['cno', 'cname', 'dept', 'time'],
            "headnoun": "cname",
            "surrogate": "cno",
            "modifiers": ['dept', 'time'],
            "similar_of_table": [

            ],
            "similar_of_column": {
                "cno": [

                ],
                "cname": [
                    
                ],
                "dept": [

                ],
                "time": [

                ],
            },
            "values": [
                ['C1', 'DBMS', 'IM', 'Mon567'],
                ['C2', 'DBMS', 'CS', 'Tue567'],
                ['C3', 'Advanced_DBMS', 'IM', 'Tue567'],
                ['C4', 'Computer_Programming', 'IM', 'Tue234'],
            ],
        }
    },
    Shape.diamond.value: {
        "take": {
            "columns": ["sno", "cno"],
            "subject": {
                "shape": Shape.entity.value,
                "name": "student",
                "key": "sno",
            },
            "object": {
                "shape": Shape.entity.value,
                "name": "course",
                "key": "cno",
            },
            "similar_of_table": [
                'take'
            ],
            "similar_of_column": {
                "sno": [

                ],
                "cno": [

                ],
            },
            "values": [
                ['S1', 'C2'],
                ['S2', 'C1'],
                ['S3', 'C1'],
                ['S3', 'C4'],
                ['S4', 'C1'],
                ['S4', 'C3'],
                ['S4', 'C4'],
                ['S5', 'C2'],
                ['S5', 'C4'],
            ],
        },
        "teach": {
            "columns": ["tno", "cno"],
            "subject": {
                "shape": Shape.entity.value,
                "name": "teacher",
                "key": "tno",
            },
            "object": {
                "shape": Shape.entity.value,
                "name": "course",
                "key": "cno",
            },
            "similar_of_table": [
                'taught'
            ],
            "similar_of_column": {
                "sno": [

                ],
                "cno": [

                ],
            },
            "values": [
                ['T1', 'C1'],
                ['T1', 'C3'],
                ['T1', 'C4'],
                ['T2', 'C2'],
                ['T2', 'C4'],
            ],
        },
    },
}
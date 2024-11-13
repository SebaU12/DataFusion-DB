from spimiInvert import SPIMIInvert

token_stream = [
    [
        ("Hola", "docID1", 80, 1.3),
        ("Mundo", "docID2", 50, 1.0),
        ("Python", "docID1", 30, 0.7),
        ("Eficiencia", "docID1", 40, 1.1)
    ],
    [
        ("Python", "docID3", 25, 0.6),
        ("Código", "docID4", 45, 0.9),
        ("Python", "docID5", 10, 0.4),
        ("Mundo", "docID6", 60, 0.9)
    ],
    [
        ("Algoritmo", "docID2", 60, 1.1),
        ("Hashing", "docID5", 20, 0.5),
        ("Eficiencia", "docID6", 75, 1.2),
        ("Datos", "docID1", 35, 0.8)
    ],
    [
        ("Memoria", "docID7", 40, 0.85),
        ("Algoritmo", "docID4", 10, 0.3),
        ("Estructura", "docID5", 55, 0.95),
        ("Índice", "docID8", 55, 1.05)
    ],
    [
        ("Estructura", "docID3", 65, 1.15),
        ("Bloque", "docID9", 22, 0.55),
        ("Documentos", "docID4", 38, 0.82),
        ("Busqueda", "docID2", 70, 1.25)
    ],
    [
        ("Estructura", "docID6", 60, 0.95),
        ("Índice", "docID3", 80, 1.2),
        ("Algoritmo", "docID1", 55, 1.0),
        ("Optimización", "docID10", 33, 0.75)
    ],
    [
        ("Algoritmo", "docID6", 18, 0.4),
        ("Sistema", "docID5", 48, 0.92),
        ("Palabra", "docID8", 28, 0.6),
        ("Archivo", "docID1", 52, 1.1)
    ],
    [
        ("Algoritmo", "docID3", 28, 0.5),
        ("Palabra", "docID4", 20, 0.5),
        ("Código", "docID2", 70, 1.0),
        ("Búsqueda", "docID12", 65, 1.05)
    ],
    [
        ("Manejo", "docID13", 40, 0.75),
        ("Fórmula", "docID14", 30, 0.6),
        ("Optimización", "docID15", 48, 0.9),
        ("Sistema", "docID16", 35, 0.8)
    ],
    [
        ("Índice", "docID17", 60, 1.05),
        ("Hashing", "docID18", 50, 0.85),
        ("Optimización", "docID19", 25, 0.55),
        ("Algoritmo", "docID2", 60, 1.1)
    ]
]



index = SPIMIInvert(token_stream)

index.construct_pre_index()
#print(index.readBlockToDict('/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/BLOCKS/BLOCK1.json'))
#index.mergeTwoBlocks('/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/BLOCKS/BLOCK1.json', '/Users/smdp/Documents/PERSONAL/DB2/DataFusion-DB/BLOCKS/BLOCK2.json')

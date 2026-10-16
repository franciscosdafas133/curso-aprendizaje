# Soluciones — simulacro (abrir solo al final)

## A1
Las distancias (euclídea, etc.) se dominan por features con mayor rango. Escalar (p. ej. StandardScaler) iguala contribuciones.

## A2
Sobreajuste: buen rendimiento en train y malo en datos no vistos. Train/test estima generalización. Accuracy solo en train no prueba generalización.

## A3
k máximo puede dar inercia ~0 (cada punto un cluster) sin significado. Se busca compromiso (codo, silhouette, conocimiento del dominio).

## B1 / B2
Ver notebooks de experimento `01_knn_escalado.ipynb` y `02_overfitting_train_test.ipynb`.

## C1
Modelos basados en distancia/regularización sensibles a escala se benefician; árboles suelen ser invariantes a monótonas en una feature. No es regla ciega.

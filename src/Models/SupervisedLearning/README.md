# Supervised Learning Models

Supervised Learning Models are those models trained using data which contains the desired output (usually labels) and make predictions about the labels of new unknown data.

## Gradient Boosting
This type of models make a strong model based on smaller and weaker models by optimizing a desired loss function.

### GradientBoostingClassifier
This is the basic gradient boosting method.

### XGB Classifier
Fast and efficient gradient boosting method that uses paralelization and memory optimization in order to improve the performance of the model.

### LGBM Classifier
This gradient boosting method uses leaf-wise growth for faster tree generation.

## Forests
Forest-based models are ensemble learning methods that use multiple decision trees to improve prediction accuracy and robustness. These models are popular for classification, regression, and anomaly detection.

### Random Forest
A supervised learning algorithm that builds multiple decision trees and combines their predictions to improve accuracy and reduce overfitting. It works by randomly selecting features and samples for each tree, making it robust against noise and overfitting.

### Isolation Forest
An unsupervised anomaly detection algorithm that isolates outliers by recursively partitioning the data. It is efficient for detecting anomalies in high-dimensional datasets by using the fact that anomalies are easier to isolate than normal instances.
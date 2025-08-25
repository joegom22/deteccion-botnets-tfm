from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class DataProcessor(BaseEstimator, TransformerMixin):
    def __init__(self, num_cols=None, cat_cols=None):
        """
        Initialize the DataProcessor with numerical and categorical columns.
        Args:
            num_cols (list): List of numerical column names.
            cat_cols (list): List of categorical column names.
        """
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.preprocessor = None
    
    def fit(self, X, y=None):
        """
        Fit the preprocessor to the data.

        Args:
            X (DataFrame): Input data.
            y (Series, optional): Target variable, not used in fitting.
        Returns:
            self: Fitted DataProcessor instance.
        """
        self.preprocessor = ColumnTransformer([
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
                ("scaler", StandardScaler())
            ]), self.num_cols),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ]), self.cat_cols)
        ])
        self.preprocessor.fit(X, y)
        return self
    
    def transform(self, X):
        """
        Transform the data using the fitted preprocessor.

        Args:
            X (DataFrame): Input data to be transformed.
            
        Returns:
            Transformed data as a numpy array.
        """
        return self.preprocessor.transform(X)
    
    def get_feature_names_out(self, input_features=None):
        """
        Get output feature names after transformation.

        Args:
            input_features (list, optional): List of input feature names.
        
        Returns:
            list: List of output feature names.
        """
        return self.preprocessor.get_feature_names_out(input_features)


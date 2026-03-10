from typing import Dict, List, Any


def generate_cleaning_code(profile: Dict[str, Any], df_name: str = "df") -> str:
    """Generate Python cleaning code based on data profile."""
    code_lines = [
        "# Data Cleaning Script",
        "import pandas as pd",
        "import numpy as np",
        "",
        f"# Load your dataset",
        f"{df_name} = pd.read_csv('your_dataset.csv')  # or pd.read_excel() for Excel files",
        "",
    ]
    
    # Remove duplicates
    if profile["duplicates"]["total_duplicate_rows"] > 0:
        code_lines.extend([
            "# Remove duplicate rows",
            f"{df_name}.drop_duplicates(inplace=True)",
            "",
        ])
    
    # Handle missing values
    missing_data = profile["missing_values"]["columns_with_missing"]
    if missing_data:
        code_lines.append("# Handle missing values")
        for col in missing_data:
            code_lines.extend([
                f"# Missing values in '{col}': {missing_data[col]['percentage']}%",
                f"{df_name}['{col}'].fillna({df_name}['{col}'].median(), inplace=True)  # Use median for numeric, mode for categorical",
            ])
        code_lines.append("")
    
    # Handle outliers
    outliers_data = profile["outliers"]["columns_with_outliers"]
    if outliers_data:
        code_lines.append("# Handle outliers using IQR method")
        for col, data in outliers_data.items():
            code_lines.extend([
                f"# Handling outliers in '{col}'",
                f"Q1 = {df_name}['{col}'].quantile(0.25)",
                f"Q3 = {df_name}['{col}'].quantile(0.75)",
                f"IQR = Q3 - Q1",
                f"lower_bound = Q1 - 1.5 * IQR",
                f"upper_bound = Q3 + 1.5 * IQR",
                f"{df_name}['{col}'] = {df_name}['{col}'].clip(lower=lower_bound, upper=upper_bound)",
            ])
        code_lines.append("")
    
    # Data type conversions
    code_lines.append("# Data type conversions")
    datatypes = profile["datatypes"]
    for col, data in datatypes.items():
        if "object" in data["datatype"] and 0 < data["unique_values"] < 20:
            code_lines.append(f"{df_name}['{col}'] = {df_name}['{col}'].astype('category')")
    code_lines.append("")
    
    # Final summary
    code_lines.extend([
        "# Data cleaning complete",
        f"print(f'Cleaned dataset shape: {{{df_name}.shape}}')",
        f"print(f'Missing values: {{{df_name}.isnull().sum().sum()}}')",
        "",
        "# Save cleaned dataset",
        f"{df_name}.to_csv('cleaned_dataset.csv', index=False)",
    ])
    
    return "\n".join(code_lines)


def generate_advanced_pipeline_code(profile: Dict[str, Any]) -> str:
    """Generate advanced sklearn pipeline code for preprocessing."""
    code = """# Advanced Data Cleaning Pipeline using scikit-learn
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

# Load dataset
df = pd.read_csv('your_dataset.csv')

# Separate numeric and categorical columns
numeric_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = df.select_dtypes(include=['object']).columns.tolist()

# Define preprocessing for numeric data
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),  # Fill missing with median
    ('scaler', StandardScaler())  # Scale to standard normal distribution
])

# Define preprocessing for categorical data
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),  # Fill missing with mode
    ('onehot', OneHotEncoder(handle_unknown='ignore'))  # One-hot encode
])

# Combine preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Apply preprocessing
df_processed = preprocessor.fit_transform(df)

# Convert back to DataFrame if needed
# df_processed = pd.DataFrame(df_processed)

print(f'Processed dataset shape: {df_processed.shape}')
print('Pipeline applied successfully!')

# Save processed data
# pd.DataFrame(df_processed).to_csv('processed_dataset.csv', index=False)
"""
    return code


def generate_custom_cleaning_code(profile: Dict[str, Any], specific_columns: List[str] = None) -> str:
    """Generate custom cleaning code for specific columns."""
    code_lines = [
        "# Custom Data Cleaning Script",
        "import pandas as pd",
        "import numpy as np",
        "",
        "df = pd.read_csv('your_dataset.csv')",
        "",
    ]
    
    if specific_columns:
        code_lines.append(f"# Cleaning {len(specific_columns)} specific column(s)")
        for col in specific_columns:
            if col in profile["missing_values"]["columns_with_missing"]:
                code_lines.append(f"# Fill missing values in '{col}'")
                code_lines.append(f"df['{col}'].fillna(df['{col}'].median(), inplace=True)")
            
            if col in profile["outliers"]["columns_with_outliers"]:
                code_lines.append(f"# Remove/cap outliers in '{col}'")
                code_lines.append(f"Q1 = df['{col}'].quantile(0.25)")
                code_lines.append(f"Q3 = df['{col}'].quantile(0.75)")
                code_lines.append(f"IQR = Q3 - Q1")
                code_lines.append(f"df = df[(df['{col}'] >= Q1 - 1.5*IQR) & (df['{col}'] <= Q3 + 1.5*IQR)]")
            
            code_lines.append("")
    
    code_lines.extend([
        "df.to_csv('cleaned_dataset.csv', index=False)",
        "print('Cleaning complete!')"
    ])
    
    return "\n".join(code_lines)

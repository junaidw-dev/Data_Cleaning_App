from typing import Dict, List, Any


def generate_recommendations(profile: Dict[str, Any], df_columns: List[str]) -> List[Dict[str, str]]:
    """Generate cleaning recommendations based on data profile."""
    recommendations = []
    
    # Missing values recommendations
    missing_data = profile["missing_values"]["columns_with_missing"]
    for col, data in missing_data.items():
        if data["percentage"] > 50:
            recommendations.append({
                "column": col,
                "issue": "Missing values",
                "severity": "High",
                "problem": f"{data['percentage']}% of values are missing",
                "recommendation": f"Consider removing column '{col}' or imputing with external data source"
            })
        elif data["percentage"] > 20:
            recommendations.append({
                "column": col,
                "issue": "Missing values",
                "severity": "Medium",
                "problem": f"{data['percentage']}% of values are missing",
                "recommendation": f"Fill missing values with median (for numeric) or mode (for categorical)"
            })
        else:
            recommendations.append({
                "column": col,
                "issue": "Missing values",
                "severity": "Low",
                "problem": f"{data['percentage']}% of values are missing",
                "recommendation": f"Fill missing values using forward fill or interpolation"
            })
    
    # Duplicate rows recommendations
    if profile["duplicates"]["total_duplicate_rows"] > 0:
        dup_percentage = profile["duplicates"]["duplicate_percentage"]
        if dup_percentage > 10:
            severity = "High"
        elif dup_percentage > 5:
            severity = "Medium"
        else:
            severity = "Low"
        
        recommendations.append({
            "column": "Dataset",
            "issue": "Duplicate rows",
            "severity": severity,
            "problem": f"{profile['duplicates']['total_duplicate_rows']} duplicate rows ({dup_percentage}%)",
            "recommendation": "Remove duplicate rows using df.drop_duplicates()"
        })
    
    # Outlier recommendations
    outliers_data = profile["outliers"]["columns_with_outliers"]
    for col, data in outliers_data.items():
        if data["percentage"] > 10:
            recommendations.append({
                "column": col,
                "issue": "Outliers",
                "severity": "Medium",
                "problem": f"{data['count']} outliers ({data['percentage']}%)",
                "recommendation": f"Review outliers or use capping (clip between {data['lower_bound']:.2f} and {data['upper_bound']:.2f})"
            })
        else:
            recommendations.append({
                "column": col,
                "issue": "Outliers",
                "severity": "Low",
                "problem": f"{data['count']} outliers ({data['percentage']}%)",
                "recommendation": f"Consider removing or capping outliers using IQR method"
            })
    
    # Data type recommendations
    datatypes = profile["datatypes"]
    for col, data in datatypes.items():
        if "object" in data["datatype"] and data["unique_values"] < 20:
            recommendations.append({
                "column": col,
                "issue": "Categorical data type",
                "severity": "Low",
                "problem": f"'{col}' has object dtype with {data['unique_values']} unique values",
                "recommendation": "Consider converting to categorical type for memory efficiency"
            })
    
    return recommendations


def categorize_recommendations(recommendations: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Categorize recommendations by severity."""
    categorized = {
        "High": [],
        "Medium": [],
        "Low": []
    }
    
    for rec in recommendations:
        severity = rec.get("severity", "Low")
        categorized[severity].append(rec)
    
    return categorized


import json

def fix_notebook():
    file_path = "notebooks/ads_hw2.ipynb"
    
    with open(file_path, "r") as f:
        nb = json.load(f)
    
    for cell in nb["cells"]:
        if cell.get("cell_type") == "code" and "source" in cell:
            source = cell["source"]
            if isinstance(source, list):
                source_str = "".join(source)
            else:
                source_str = source
            
            # Find the binary classification setup cell
            if "Robust check for target variable" in source_str:
                # Replace with simpler code that uses Churn directly
                new_source = [
                    "# Binary classification target: use Churn column directly\n",
                    "# Find the churn column (case-insensitive)\n",
                    "churn_col = next((c for c in df.columns if c.lower() == 'churn'), None)\n",
                    "if churn_col is None:\n",
                    "    raise ValueError(f'Churn column not found. Available: {df.columns.tolist()}')\n",
                    "\n",
                    "# Convert Yes/No to 1/0 for classification\n",
                    "y_bin = df[churn_col].apply(lambda x: 1 if str(x).lower() in ['yes', 'true', '1'] else 0)\n",
                    "\n",
                    "# Drop target and ID columns from features\n",
                    "cols_to_drop = [c for c in df.columns if c.lower() in ['customerid', 'customer_id', 'churn', 'totalcharges', 'total_charges', 'paymentmethod', 'payment_method']]\n",
                    "X_bin = df.drop(columns=cols_to_drop)\n",
                    "\n",
                    "preprocess_cls = make_preprocessor()\n",
                    "\n",
                    "X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(\n",
                    "    X_bin, y_bin, test_size=0.2, random_state=42, stratify=y_bin\n",
                    ")\n",
                    "\n",
                    "models_bin = [\n",
                    '    ("Logistic Regression", LogisticRegression(max_iter=200, class_weight="balanced")),\n',
                    '    ("Linear SVM", SVC(kernel="linear", probability=True, class_weight="balanced", C=1.0)),\n',
                    '    ("RBF SVM", SVC(kernel="rbf", probability=True, class_weight="balanced", C=2.0, gamma="scale")),\n',
                    "    (\"KNN (k=15)\", KNeighborsClassifier(n_neighbors=15)),\n",
                    '    ("Decision Tree (max_depth=6)", DecisionTreeClassifier(max_depth=6, random_state=42, class_weight="balanced")),\n',
                    '    ("Random Forest", RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight="balanced")),\n',
                    "]\n",
                    "\n",
                    "bin_results = []\n",
                    "conf_mats = {}\n",
                    "for name, model in models_bin:\n",
                    '    pipe = Pipeline(steps=[("prep", preprocess_cls), ("model", model)])\n',
                    "    result = evaluate_binary(pipe, X_train_b, y_train_b, X_test_b, y_test_b, name)\n",
                    '    bin_results.append({k: v for k, v in result.items() if k != "confusion"})\n',
                    '    conf_mats[name] = result["confusion"]\n',
                    "\n",
                    'bin_df = pd.DataFrame(bin_results).set_index("model").sort_values("f1", ascending=False)\n',
                    "bin_df\n",
                ]
                cell["source"] = new_source
                print("Fixed binary classification cell")
    
    # Also fix any other cells that reference churn_flag
    for cell in nb["cells"]:
        if cell.get("cell_type") == "code" and "source" in cell:
            source = cell["source"]
            if isinstance(source, list):
                new_source = []
                for line in source:
                    # Replace churn_flag references in drop statements
                    if "churn_flag" in line and "drop" in line:
                        line = line.replace('"churn_flag", ', '').replace(', "churn_flag"', '').replace('"churn_flag"', '')
                    new_source.append(line)
                cell["source"] = new_source
    
    with open(file_path, "w") as f:
        json.dump(nb, f, indent=1)
    
    print("Notebook updated successfully")

if __name__ == "__main__":
    fix_notebook()


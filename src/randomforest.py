from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, balanced_accuracy_score
import joblib
import pandas as pd
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
import seaborn as sns
import shap

#Load Data
train_data = pd.read_csv('data/train_data.csv')
test_data = pd.read_csv('data/test_data.csv')

X_train = train_data.drop(['KELULUSAN', 'ID'], axis=1)
y_train = train_data['KELULUSAN']
X_test = test_data.drop(['KELULUSAN', 'ID'], axis=1)
y_test = test_data['KELULUSAN']

#Hyperparameter Tuning
param_grid = {
    'n_estimators': [200, 500],
    'max_depth': [6, 8, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2'],
    'criterion': ['gini', 'entropy'],
}

rf_model = RandomForestClassifier(
    random_state=42, 
    n_jobs=-1,
    class_weight='balanced'
    )
    
cv = 5 if len(y_train.unique()) > 1 and len(y_train) >= 5 else 3

grid_search = GridSearchCV(
    estimator=rf_model,
    param_grid=param_grid,
    cv=cv,
    scoring='balanced_accuracy',
    verbose=2
)
grid_search.fit(X_train, y_train)

#Model Terbaik
best_rf = grid_search.best_estimator_
print("\n🔵 Best Parameters:", grid_search.best_params_)


#Evaluasi Model
#Cross-Validation
cv_scores = cross_val_score(best_rf, X_train, y_train, cv=5)
print(f"\n📊 CV Accuracy: {cv_scores.mean():.2%} (±{cv_scores.std():.2%})")

#Test Set Evaluation
y_pred = best_rf.predict(X_test)
print("\n🔍 Classification Report:")
kelulusan = joblib.load('models/kelulusan.joblib')
class_names = kelulusan.classes_
print(classification_report(y_test, y_pred, target_names=class_names))

print("Balanced Accuracy:", balanced_accuracy_score(y_test, y_pred))
print("Test Accuracy:", accuracy_score(y_test, y_pred))


#Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix')
plt.ylabel('Aktual')
plt.xlabel('Prediksi')
plt.savefig('static/assets/img/confusion_matrix.png')
plt.show()

#Feature Importance
feature_imp = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': best_rf.feature_importances_
}).sort_values('Importance', ascending=False)

print(feature_imp)

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_imp)
plt.title('Feature Importance')
plt.tight_layout()
plt.savefig('static/assets/img/feature_importance.png')
plt.show()


#SHAP
print("\n### Membuat SHAP Explainer ###")
shap_explainer = shap.Explainer(best_rf, feature_names=list(X_train.columns))
joblib.dump(shap_explainer, 'models/shap.joblib')
print("\n💾 SHAP explainer disimpan di: models/shap.joblib")


shap_exp = shap_explainer(X_train)


# index kelas utk visualisasi
try:
    target_label = next(c for c in class_names if c.lower() == 'lulus')
    lulus_class_index = list(class_names).index(target_label)
except StopIteration:
    lulus_class_index = 0

# SUMMARY PLOT
plt.figure()
shap.plots.bar(shap_exp[..., lulus_class_index], show=False)
plt.title('Rata-rata Dampak Fitur pada Prediksi (SHAP Summary)')
plt.tight_layout(); plt.savefig('static/assets/img/shap_summary_plot.png', dpi=150, bbox_inches='tight')
print("\n💾 SHAP summary plot disimpan di: static/assets/img/shap_summary_plot.png")
plt.close()


# BEESWARM PLOT
plt.figure()
shap.plots.beeswarm(shap_exp[..., lulus_class_index], show=False)
plt.title(f"Distribusi Dampak Fitur terhadap Prediksi '{class_names[lulus_class_index]}'")
plt.tight_layout(); plt.savefig('static/assets/img/shap_beeswarm_plot.png', dpi=150, bbox_inches='tight')
print(" SHAP beeswarm plot disimpan di: static/assets/img/shap_beeswarm_plot.png")
plt.close()



#save mdl
joblib.dump(best_rf, 'models/random_forest_model.joblib')
print("\n💾 Model dan SHAP disimpan di: 'models/'.")

#Metadata model
model_metadata = {
    'best_params': grid_search.best_params_,
    'cv_score': cv_scores.mean(),
    'test_accuracy': accuracy_score(y_test, y_pred),
    'feature_importance': feature_imp.to_dict()
}

joblib.dump(model_metadata, 'models/model_metadata.joblib')
print("💾 Metadata disimpan di: models/model_metadata.joblib")
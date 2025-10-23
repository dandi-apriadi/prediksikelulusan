import pandas as pd
import matplotlib.pyplot as plt

#Load data
df = pd.read_csv(r'data\dataset.csv', sep=',')

# Analisis
print("\n🔍 Deskripsi Data:")
print(df.describe())

# Plot
df['KELULUSAN'].value_counts().plot(
    kind='pie',
    autopct='%1.1f%%',
    colors=['#66b3ff', '#ff9999']
)
plt.title("Persentase Data")

#save plot
plt.savefig('static/assets/img/plot_data.png')
plt.show()
#1. Import library numpy dan pandas untuk menghitung data yang ada
import numpy as np
import pandas as pd

#2. Mengambil data insurance.csv
data = pd.read_csv("./insurance.csv")
data.head(5)

# menampilkan total baris dan kolom dari data
display(data.shape)

#3. Menghitung jumlah data yang bernilai null / kosong
data.isnull().sum()

# Mengisi nilai kosong dengan rata-rata dari kolom 'bmi'
data['bmi'].fillna(data['bmi'].mean(), inplace=True)

# Mengisi nilai kosong dengan rata-rata dari kolom 'charges'
data['charges'].fillna(data['charges'].mean(), inplace=True)

#Setelah data yang kosong diisi dengan rata-rata dari masing-masing kolom, tidak ada lagi data yang bernilai null

# cek kembali data yang bernilai null
data.isna().sum()

#4. Mengubah variabel kategorikal menjadi data numerik tanpa menggunakan pd.get_dummies. Tidak disarankan untuk menggunakan pd.get_dummies dalam mode produksi
data.describe()

import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from sklearn.preprocessing import OneHotEncoder, LabelEncoder

cat_feature = ['sex']
cat_more_features = ['smoker', 'region']
feature_name = []

def num_cat(feature, feature_name):
    label_enc = LabelEncoder()
    label_enc.fit(feature)
    label_feat = label_enc.transform(feature)
    #print(label_enc.classes_)

    ohe = OneHotEncoder()
    ohe.fit(label_feat.reshape(-1,1))
    encoded_data = ohe.transform(label_feat.reshape(-1,1)).toarray()
    feature_name = ohe.get_feature_names_out(input_features=[feature_name])
    #print(feature_name)
    return encoded_data, feature_name, label_enc.classes_

for i in cat_feature:
    enc_dataI = num_cat(data[i], i)
    tempI = enc_dataI[0]
    clas = enc_dataI[2]
    for ii in clas:
        feature_name.append(i+'_'+ii)

for j in cat_more_features:
    enc_dataII = num_cat(data[j], j)
    tempII = enc_dataII[0]
    clas = enc_dataII[2]
    for jj in clas:
        feature_name.append(j+'_'+jj)
    tempI = np.concatenate([tempI, tempII], axis=1)

print(feature_name)

#5. Kemudian menggabungkan kolom-kolom yang tersisa dari dataset ke dataframe yang baru.
cat_to_num = pd.DataFrame(tempI, columns=feature_name)
dataN = cat_to_num.join(data[['age','bmi','children','charges']])
plt.figure(figsize=(18,12))
sns.heatmap(dataN.corr(), center=0, linewidths=0.5, cmap='YlGnBu')

#6. Dari heatmap, cukup jelas bahwa perokok memiliki korelasi positif dengan charges/biaya.
dataN.head(5)

sns.pairplot(data, hue="smoker")

#7. Dari pairplot di atas, beberapa poin dapat disimpulkan: Perokok membayar lebih banyak biaya seiring bertambahnya usia. Untuk perokok, biaya meningkat bersama dengan bmi, sedangkan untuk non-perokok tidak terlalu banyak mengeluarkan biaya.
sns.pairplot(data, hue="sex")
sns.distplot(data.charges)

#Berdasarkan grafik diatas, terlihat bahwa mean lebih besar dari median, yang berarti biaya rata-rata lebih besar dari biaya median.

plt.hist(data.charges, bins=20)

## Cek prediksi menggunakan algoritma **Sklearn**: (numerical data)
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
y = dataN.charges
X = dataN.drop(['charges'], axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=True)
reg = LinearRegression()
reg.fit(X_train, y_train)
print(reg.coef_)
print(reg.intercept_)
y_train_pred = reg.predict(X_train)
y_test_pred = reg.predict(X_test)

train_accu = r2_score(y_train, y_train_pred)
test_accu = r2_score(y_test, y_test_pred)

print("Akurasi Linear Regression Train: ", train_accu)
print("Tes Akurasi: ", test_accu)

## Cek prediksi menggunakan algoritma **Random Forest Regressor**
reg_random = RandomForestRegressor(max_depth=10, random_state=1, n_estimators=200)
reg_random.fit(X_train, y_train)
y_train_randm = reg_random.predict(X_train)
y_test_randm = reg_random.predict(X_test)
train_accu_pred_randm = r2_score(y_train, y_train_randm)
test_accu_pred_randm = r2_score(y_test, y_test_randm)

print("Akurasi Train Prediksi", train_accu_pred_randm)
print("Akurasi Tes Prediksi: ", test_accu_pred_randm )

#**Note:** dengan menggunakan RFG dapat meningkatkan akurasi data hingga hampir 97%. Namun, kita perlu melihat lebih dalam lagi dengan menggunakan log transformation.

#Kemudian gunakan log transformation pada data charges yang di distribusikan condong ke kanan (right skewed)
y_ln = np.log(dataN.charges)
X_ln = dataN.drop(['charges'], axis=1)
X_train_ln, X_test_ln, y_train_ln, y_test_ln = train_test_split(X_ln, y_ln, test_size=0.3)
reg_ln = LinearRegression()
reg_ln.fit(X_train_ln, y_train_ln)
y_train_ln_pred = reg_ln.predict(X_train_ln)
y_test_ln_pred = reg_ln.predict(X_test_ln)
print("Akurasi log train: ", r2_score(y_train_ln, y_train_ln_pred))
print("Akurasi tes log: ", r2_score(y_test_ln, y_test_ln_pred))

## Random Forest with Log Transformation
rndm_ln = RandomForestRegressor(max_depth=10, random_state=1, n_estimators=200)
rndm_ln.fit(X_train_ln, y_train_ln)
y_trainrndm_pred = rndm_ln.predict(X_train_ln)
y_testrndm_pred = rndm_ln.predict(X_test_ln)
print("Train akurasi random forest: ", r2_score(y_train_ln, y_trainrndm_pred))
print("Tes akurasi random forest: ", r2_score(y_test_ln, y_testrndm_pred))

#Terlihat bahwa dengan menggunakan random forest with log transformation tingkat akurasi datanya masih kalah dengan menggunakan RandomForestRegressor yang hampir 97%, kemudian coba kita periksa dengan drawing learning curve
from sklearn.model_selection import learning_curve
def learning_curves(algo, X, y, train_sizes, cv):
    train_sizes, train_score, validation_score = learning_curve(estimator=algo, X=X, y=y, cv=cv, scoring='neg_mean_squared_error')
    train_score_mean = -train_score.mean(axis=1)
    validation_score_mean = -validation_score.mean(axis=1)

    plt.plot(train_sizes, train_score_mean, label="Training error")
    plt.plot(train_sizes, validation_score_mean, label="Validation Error")

    plt.ylabel("MSE", fontsize=10)
    plt.xlabel("Train sizes", fontsize=10)

    plt.title("Learning Curve")
    plt.legend(loc="best")

train_sizes=[1,200,400,600,800,1000]

learning_curves(rndm_ln, X_ln, y_ln,train_sizes,5)

learning_curves(reg_ln, X_ln, y_ln, train_sizes, 5)

#Kesimpulan dari perbandingan 2 algoritma:
#! 1. Algoritma RandomForestRegressor mampu meningkatkan akurasi data yang di uji hingga hampir 97%
#! 2. RandomForestRegressor pemenang dari seluruh algoritma yang kami tes
#! 3. Random Forest memiliki tingkat akurasi cukup tinggi karena dia mengambil rataan (average) dari sekian banyak prediksi. Oleh karena itu, teknik ini bisa meminimumkan bias (error) nya.


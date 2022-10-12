import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import rcParams
from sklearn.metrics import mean_squared_error 
from sklearn.metrics import mean_absolute_error

############################################################################
# Script what plots ground truth coordinates and calculated coordinates 
############################################################################

def mse(actual, predicted):
    return np.square(np.subtract(np.array(actual), np.array(predicted))).mean()

def dif(actual, predicted):
    return np.subtract(np.array(actual), np.array(predicted))


sns.set_style("whitegrid")
sns.set(font_scale = 2)
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.edgecolor'] = 'white'
plt.rcParams['axes.unicode_minus'] = False
filename = "calculated_coordinates_real_data_1.csv"



data = pd.read_csv(filename)
total_images = data.shape[0]
data = data.loc[data['Calculated_Latitude'] != -1]
data = data.loc[data['Meters_Error'] < 50]

located_images = data.shape[0]

dataset_list = []
for i in range(0,data.shape[0]):
    dataset_list.append("Dataset 1")

data['Dataset'] = dataset_list

pd_zeros = pd.DataFrame(np.zeros(data.shape[0]))
 
print("Total images ", total_images) 
print("Located images ", located_images)
print("Located images %", located_images *100 / total_images)

# Using DataFrame.mean() method to get column average
df2 = data["Meters_Error"].mean()
print(data['Meters_Error'])
print("Mean meter error:", df2)
print("RMS meter error:", mse(pd_zeros, data['Meters_Error']))
mse_sci_kit = mean_squared_error(pd_zeros, data['Meters_Error'], squared=False)
mae_sci_kit = mean_absolute_error(pd_zeros, data['Meters_Error'], )
print("RMS meter error Sci_kit: ", mse_sci_kit)
print("MAE meter error Sci_kit: ", mae_sci_kit)

print("Filename:", filename)
print("RMS Latitude:", mse(data['Latitude'], data['Calculated_Latitude']))

print("RMS Longitude:", mse(data['Longitude'], data['Calculated_Longitude']))


print(data)


fig=plt.figure(figsize=(15,8))
ax=plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.patch.set_facecolor('lightgray')
ax.patch.set_alpha(0.4)
sns.lineplot(data = data, x = data.index , y = "Meters_Error", marker="o", color='r')
ax.set_xlabel("Photograph Index")
ax.set_ylabel("Localization Error [m]")

plt.savefig("mean_error_dataset_1.png")
plt.savefig("mean_error_dataset_1.pdf")


plt.show()



print("RMS Latitude:", mse(data['Latitude'], data['Calculated_Latitude']))

print("RMS Longitude:", mse(data['Longitude'], data['Calculated_Longitude']))

error = dif(data['Latitude'], data['Calculated_Latitude'])
print(error)






filename = "calculated_coordinates_real_data_2.csv"



data_2 = pd.read_csv(filename)
total_images = data_2.shape[0]
data_2 = data_2.loc[data_2['Calculated_Latitude'] != -1]
data_2 = data_2.loc[data_2['Meters_Error'] < 50]

located_images = data_2.shape[0]

dataset_list = []
for i in range(0,data_2.shape[0]):
    dataset_list.append("Dataset 2")

data_2['Dataset'] = dataset_list

concatenated = pd.concat([data, data_2])

fig=plt.figure(figsize=(15,8))
ax=plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.patch.set_facecolor('lightgray')
ax.patch.set_alpha(0.4)
sns.boxplot(x = "Dataset",y="Meters_Error", data=concatenated)
#ax.set_xlabel("Photograph Index")
#ax.set_ylabel("Localization Error [m]")

plt.savefig("boxplot_error_dataset_1.png")
plt.savefig("boxplot_error_dataset_1.pdf")


plt.show()









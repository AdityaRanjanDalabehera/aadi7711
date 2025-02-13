# -*- coding: utf-8 -*-
"""human_activity_rec.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WkFTWmWbCZToPZ9VEJ7YEsAHDbXbIsvQ
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import roc_auc_score
from tqdm import tqdm
import os
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications.xception import Xception
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, TensorBoard, ModelCheckpoint
from sklearn.metrics import classification_report,confusion_matrix
import ipywidgets as widgets
import io
from PIL import Image
from IPython.display import display,clear_output
from warnings import filterwarnings
for dirname, _, filenames in os.walk('/content/drive/MyDrive/activity_rec'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

colors_dark = ["#1F1F1F", "#313131", '#636363', '#AEAEAE', '#DADADA']
colors_blue = ['#003396', '#1750AC', '#3373C4', '#73B9EE','#86CEFA']
colors_pink = ['#342415','#442e19','#54381d','#654321','#7f5f42']
sns.palplot(colors_dark)
sns.palplot(colors_pink)
sns.palplot(colors_blue)
labels = ['applauding','blowing_bubbles','brushing_teeth','cleaning _the_floor','climbing','cooking','cutting_trees','cutting_vegetables','drinking','feeding_horse','fishing','fixing_a_bike','fixing_a_car','gardening','holding_an_umbrella','jumping','looking_through_a_microscope','looking_through_a_telescope','phoning','playing_guitar','playing_violin','pouring_liquid','pushing_a_cart','reading','riding_a_bike','riding_a_horse','rowing_a_boat','running','shooting_an_arrow','smoking','taking_photos','texting_message','throwing_frisby','using_a_computer','walking_the_dog','washing_dishes','watching_TV','waving_hands','writing_on_a_board','writing_on_a_book']
X_train = []
y_train = []
image_size = 150
for i in labels:
    folderPath = os.path.join('/content/drive/MyDrive','activity_rec',i)
    for j in tqdm(os.listdir(folderPath)):
        img = cv2.imread(os.path.join(folderPath,j))
        img = cv2.resize(img,(image_size, image_size))
        X_train.append(img)
        y_train.append(i)
for i in labels:
    folderPath = os.path.join('/content/drive/MyDrive','activity_rec',i)
    for j in tqdm(os.listdir(folderPath)):
        img = cv2.imread(os.path.join(folderPath,j))
        img = cv2.resize(img,(image_size,image_size))
        X_train.append(img)
        y_train.append(i)

X_train = np.array(X_train)
y_train = np.array(y_train)
k=0
fig, ax = plt.subplots(1,40,figsize=(100,12))
# fig.text(s='Sample Image From Each Label',size=18,fontweight='bold',
#              fontname='monospace',color=colors_dark[1],y=0.6,x=0.4,alpha=0.8)
for i in labels:
    j=0
    while True :
        if y_train[j]==i:
            ax[k].imshow(X_train[j])
            ax[k].set_title(y_train[j])
            ax[k].axis('off')
            k+=1
            break
        j+=1
X_train, y_train = shuffle(X_train,y_train, random_state=101)
X_train.shape

X_train,X_test,y_train,y_test = train_test_split(X_train,y_train, test_size=0.2,random_state=101)
y_train_new = []
for i in y_train:
    y_train_new.append(labels.index(i))
y_train = y_train_new
y_train = tf.keras.utils.to_categorical(y_train)


y_test_new = []
for i in y_test:
    y_test_new.append(labels.index(i))
y_test = y_test_new
y_test = tf.keras.utils.to_categorical(y_test)

xception = Xception(weights='imagenet',include_top=False,input_shape=(image_size,image_size,3))

model = tf.keras.models.Sequential()
model.add(xception)
model.add(tf.keras.layers.GlobalAveragePooling2D())
model.add(tf.keras.layers.Dropout(rate=0.5))
model.add(tf.keras.layers.Dense(40, activation='softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',optimizer = 'Adam', metrics= ['accuracy'])

tensorboard = TensorBoard(log_dir = 'logs')
checkpoint = ModelCheckpoint("/content/drive/MyDrive/Human.h5",monitor="val_accuracy",save_best_only=True,mode="auto",verbose=1)
reduce_lr = ReduceLROnPlateau(monitor = 'val_accuracy', factor = 0.3, patience = 2, min_delta = 0.001,
                              mode='auto',verbose=1)

history = model.fit(X_train,y_train,validation_split=0.2, epochs =50, verbose=1, batch_size=64,
                   callbacks=[tensorboard,checkpoint,reduce_lr])



import tensorflow as tf
import keras
from keras.models import load_model

activity_model = load_model('/content/drive/MyDrive/Human.h5', compile=False)

converter = tf.lite.TFLiteConverter.from_keras_model(activity_model)
#converter.optimizations = [tf.lite.Optimize.DEFAULT] #Uses default optimization strategy to reduce the model size
tflite_model = converter.convert()
open("/content/drive/MyDrive/Human.tflite", "wb").write(tflite_model)

filterwarnings('ignore')
epochs = [i for i in range(50)]
fig, ax = plt.subplots(1,1,figsize=(8,5))
train_acc = history.history['accuracy']
train_loss = history.history['loss']
val_acc = history.history['val_accuracy']

val_loss = history.history['val_loss']

# fig.text(s='Efficient-NetV2B2 Accuracy ',size=16,fontweight='bold',
#               fontname='monospace',color=colors_dark[1],y=1,x=0.28,alpha=0.8)

sns.despine()
ax.plot(epochs, train_acc, marker='.',markerfacecolor='green',color='green',
           label = 'Training Accuracy')
ax.plot(epochs, val_acc, marker='.',markerfacecolor='red',color='red',
           label = 'Validation Accuracy')
ax.legend(frameon=False)
ax.set_xlabel('Epochs')
ax.set_ylabel('Accuracy')
ax.set_title('xception')
sns.set_theme()
plt.savefig("/content/drive/MyDrive/ALLOUTPUT/xception_for_har.eps",dpi=600)
fig.show()

filterwarnings('ignore')
epochs = [i for i in range(50)]
fig, ax = plt.subplots(1,1,figsize=(8,5))
train_acc = history.history['accuracy']
train_loss = history.history['loss']
val_acc = history.history['val_accuracy']
val_loss = history.history['val_loss']
# fig.text(s='Efficient-NetV2B2',size=8,fontweight='bold',
#               color=colors_dark[1],y=1,x=0.28,alpha=0.8)

sns.despine()
ax.plot(epochs, train_loss, marker='.',markerfacecolor='green',color='green',
           label ='Training Loss')
ax.plot(epochs, val_loss, marker='.',markerfacecolor='red',color='red',
           label = 'Validation Loss')
ax.legend(frameon=False)
ax.set_xlabel('Epochs')
ax.set_ylabel('Loss')
ax.set_title('xception')
plt.savefig("/content/drive/MyDrive/ALLOUTPUT/xception_los_for_har.eps",dpi=600)
fig.show()

pred = model.predict(X_test)
pred = np.argmax(pred,axis=1)
y_test= np.argmax(y_test,axis=1)

y_test=y_test.reshape(-1,1)

y_test.shape

print(classification_report(y_test,pred))

# Calculate sensitivity and specificity
TP = np.diag(cm)
FP = cm.sum(axis=0) - TP
FN = cm.sum(axis=1) - TP
TN = cm.sum() - (FP + FN + TP)

sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)

# Print sensitivity and specificity
for i, label in enumerate(labels):
    print(f"{label}: Sensitivity = {sensitivity[i]}, Specificity = {specificity[i]}")

# Generate confusion matrix table
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
plt.figure(figsize=(12, 10))
sns.heatmap(cm_df, annot=True, cmap='Blues', fmt='g')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate sensitivity and specificity
TP = np.diag(cm)
FP = cm.sum(axis=0) - TP
FN = cm.sum(axis=1) - TP
TN = cm.sum() - (FP + FN)

sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)

# Print sensitivity and specificity
for i, label in enumerate(labels):
    print(f"{label}: Sensitivity = {sensitivity[i]}, Specificity = {specificity[i]}")

# Calculate overall sensitivity and specificity
overall_sensitivity = np.mean(sensitivity)
overall_specificity = np.mean(specificity)

print(f"Overall Sensitivity: {overall_sensitivity}")
print(f"Overall Specificity: {overall_specificity}")

# Generate confusion matrix table
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
plt.figure(figsize=(12, 10))
sns.heatmap(cm_df, annot=True, cmap='Blues', fmt='g')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()



import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate sensitivity and specificity
TP = np.diag(cm)
FP = cm.sum(axis=0) - TP
FN = cm.sum(axis=1) - TP
TN = cm.sum() - (FP + FN + TP)

sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)

# Print sensitivity and specificity
for i, label in enumerate(labels):
    print(f"{label}: Sensitivity = {sensitivity[i]}, Specificity = {specificity[i]}")

# Generate confusion matrix table
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
plt.figure(figsize=(12, 10))
sns.heatmap(cm_df, annot=True, cmap='Blues', fmt='g')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

print(cm)

from sklearn.metrics import confusion_matrix
from mlxtend.plotting import plot_confusion_matrix

cm = confusion_matrix(y_test,pred)
plot_confusion_matrix(conf_mat = cm,figsize=(8,7),
                     show_normed = True)

# Calculate confusion matrix
cm = confusion_matrix(y_test_labels, pred_labels)

# Calculate sensitivity and specificity
TP = np.diag(cm)
FP = cm.sum(axis=0) - TP
FN = cm.sum(axis=1) - TP
TN = cm.sum() - (FP + FN + TP)

sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)

# Print sensitivity and specificity
for i, label in enumerate(labels):
    print(f"{label}: Sensitivity = {sensitivity[i]}, Specificity = {specificity[i]}")

# Generate confusion matrix table
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
plt.figure(figsize=(12, 10))
sns.heatmap(cm_df, annot=True, cmap='Blues', fmt='g')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

fig,ax=plt.subplots(1,1,figsize=(20,20))

sns.heatmap(cm/np.sum(cm),ax=ax,xticklabels=labels,yticklabels=labels,annot=True, fmt='.2%',
           cmap='gnuplot',alpha=1,linewidths=0.5,linecolor=colors_dark[1])
#fig.text(s='Confusion Matrix',size=18,fontweight='bold',
             #fontname='monospace',color=colors_dark[1],y=0.92,x=0.28,alpha=0.8)
ax.set_xlabel('PREDICTED VALUES',fontweight='bold')
ax.set_ylabel('ACTUAL VALUES',fontweight='bold')
# plt.savefig("efficientnetv2b2cnfsn.eps",dpi=1200)
plt.show()

#group_names = ['True Neg','False Pos','False Neg','True Pos','True Pos','True Pos','True Pos','True Pos','True Pos']
fig,ax=plt.subplots(1,1,figsize=(10,10))
group_counts = ["{0:0.0f}".format(value) for value in
                cm.flatten()]

group_percentages = ["{0:.2%}".format(value) for value in
                     cm.flatten()/np.sum(cm)]

labels = [f"{v1}\n{v2}\n" for v1, v2 in
          zip(group_counts,group_percentages)]

labels = np.asarray(labels).reshape(40,40)

ax = sns.heatmap(cm, annot=labels, fmt='', cmap='cubehelix',alpha=1,linewidths=0.5,linecolor=colors_dark[1])

ax.set_title('xception\n');
ax.set_xlabel('\nPredicted ')
ax.set_ylabel('Actual ');

## Ticket labels - List must be in alphabetical order
ax.xaxis.set_ticklabels(['applauding','blowing_bubbles','brushing_teeth','cleaning _the_floor','climbing','cooking','cutting_trees','cutting_vegetables','drinking','feeding_horse','fishing','fixing_a_bike','fixing_a_car','gardening','holding_an_umbrella','jumping','looking_through_a_microscope','looking_through_a_telescope','phoning','playing_guitar','playing_violin','pouring_liquid','pushing_a_cart','reading','riding_a_bike','riding_a_horse','rowing_a_boat','running','shooting_an_arrow','smoking','taking_photos','texting_message','throwing_frisby','using_a_computer','walking_the_dog','washing_dishes','watching_TV','waving_hands','writing_on_a_board','writing_on_a_book'])
ax.yaxis.set_ticklabels(['applauding','blowing_bubbles','brushing_teeth','cleaning _the_floor','climbing','cooking','cutting_trees','cutting_vegetables','drinking','feeding_horse','fishing','fixing_a_bike','fixing_a_car','gardening','holding_an_umbrella','jumping','looking_through_a_microscope','looking_through_a_telescope','phoning','playing_guitar','playing_violin','pouring_liquid','pushing_a_cart','reading','riding_a_bike','riding_a_horse','rowing_a_boat','running','shooting_an_arrow','smoking','taking_photos','texting_message','throwing_frisby','using_a_computer','walking_the_dog','washing_dishes','watching_TV','waving_hands','writing_on_a_board','writing_on_a_book'])

## Display the visualization of the Confusion Matrix.
# plt.savefig("/content/gdrive/MyDrive/ALLOUTPUT/ae2.eps",transparent=True,dpi=1200)
plt.show()

roc_auc_score(y_test, pred, multi_class='ovo',average='weighted')

from sklearn.metrics import roc_curve, roc_auc_score
roc_auc_score(y_test,pred, multi_class='ovr')

macro_roc_auc_ovo = roc_auc_score(y_test, pred, multi_class="ovo", average="macro")
weighted_roc_auc_ovo = roc_auc_score(
    y_test, pred, multi_class="ovo", average="weighted"
)
macro_roc_auc_ovr = roc_auc_score(y_test, pred, multi_class="ovr", average="macro")
weighted_roc_auc_ovr = roc_auc_score(
    y_test, pred, multi_class="ovr", average="weighted"
)
print(
    "One-vs-One ROC AUC scores:\n{:.6f} (macro),\n{:.6f} "
    "(weighted by prevalence)".format(macro_roc_auc_ovo, weighted_roc_auc_ovo)
)
print(
    "One-vs-Rest ROC AUC scores:\n{:.6f} (macro),\n{:.6f} "
    "(weighted by prevalence)".format(macro_roc_auc_ovr, weighted_roc_auc_ovr)
)

y_test= label_binarize(y_test, classes=[0, 1, 2, 3, 4, 5, 6, 7, 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39])
n_classes = y_test.shape[1]

y_test.shape

fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(40):
    fpr[i], tpr[i], _ = roc_curve(y_test[:, i], pred[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Compute micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), pred.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
# First aggregate all false positive rates
all_fpr = np.unique(np.concatenate([fpr[i] for i in range(40)]))

# Then interpolate all ROC curves at this points
mean_tpr = np.zeros_like(all_fpr)
for i in range(7):
    mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])

# Finally average it and compute AUC
mean_tpr /= 40

fpr["macro"] = all_fpr
tpr["macro"] = mean_tpr
roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

# Plot all ROC curves

plt.figure(figsize=(8,5))

plt.plot(
    fpr["micro"],
    tpr["micro"],
    label="micro-average ROC curve (area = {0:0.2f})".format(roc_auc["micro"]),
    color="gray",

    linewidth=2

)

plt.plot(
    fpr["macro"],
    tpr["macro"],
    label="macro-average ROC (area = {0:0.2f})".format(roc_auc["macro"]),
    color="yellow",

    linewidth=0.8

)

from itertools import cycle

color_cycle = cycle(["blue", "black", "gray", "green", "navy", "turquoise", "darkorange", "cornflowerblue", "teal",
                    "purple", "red", "darkgreen", "silver", "lime", "indigo", "gold", "slategray", "olive",
                    "darkcyan", "maroon", "cyan", "darkviolet", "peru", "orchid", "steelblue", "chocolate",
                    "mediumseagreen", "plum", "dodgerblue", "sienna", "mediumorchid", "cadetblue", "orangered",
                    "mediumblue", "darkslategray", "mediumturquoise", "darkred", "rosybrown", "mediumvioletred",
                    "deepskyblue", "saddlebrown"])

colors = [next(color_cycle) for _ in range(40)]

print(colors)


for i, color in zip(range(42), colors):
    plt.plot(
        fpr[i],
        tpr[i],
        color=color,
        linewidth=1

        # label="ROC of class {0} (area = {1:0.2f})".format(i, roc_auc[i]),
    )
plt.plot(figsize=(20, 20))
plt.plot([0, 1], [0, 1.0], "k--")

plt.xlim([0.0 , 1.0])
plt.ylim([0.0 , 1.1])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("xception ")
plt.legend(loc="lower right")
plt.grid('dark')
# sns.set_style('darkgrid')
#plt.style.use("dark_background")
plt.savefig("/content/drive/MyDrive/ALLOUTPUT/xceptionmultiroc_for_har.eps",dpi=1200)
plt.show()

from sklearn.metrics import roc_curve, roc_auc_score
roc_auc = dict()
fig,ax=plt.subplots(1,1,figsize=(8,5))
from sklearn.metrics import roc_curve
pred = model.predict(X_test)
fpr, tpr, thresholds = roc_curve(y_test.ravel(), pred.ravel())
plt.plot([0,1],[0,1],'k--')
plt.plot(fpr,tpr, label='xception')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('xception')
plt.savefig("/content/drive/MyDrive/ALLOUTPUT/xception_for_harroc.eps",dpi=600)
plt.show()

from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import PrecisionRecallDisplay

# For each class
precision = dict()
recall = dict()
average_precision = dict()
for i in range(40):
    precision[i], recall[i], _ = precision_recall_curve(y_test[:, i], pred[:, i])
    average_precision[i] = average_precision_score(y_test[:, i], pred[:, i])

# A "micro-average": quantifying score on all classes jointly
precision["micro"], recall["micro"], _ = precision_recall_curve(
    y_test.ravel(), pred.ravel()
)
average_precision["micro"] = average_precision_score(y_test, pred, average="micro")

display = PrecisionRecallDisplay(
    recall=recall["micro"],
    precision=precision["micro"],
    average_precision=average_precision["micro"],
)
display.plot()
_ = display.ax_.set_title("xception")
plt.savefig("/content/drive/MyDrive/ALLOUTPUT/pr_har.eps",dpi=600)

import matplotlib.pyplot as plt
from itertools import cycle



color_cycle = cycle(["blue", "black", "gray", "green", "navy", "turquoise", "darkorange", "cornflowerblue", "teal",
                    "purple", "red", "darkgreen", "silver", "lime", "indigo", "gold", "slategray", "olive",
                    "darkcyan", "maroon", "cyan", "darkviolet", "peru", "orchid", "steelblue", "chocolate",
                    "mediumseagreen", "plum", "dodgerblue", "sienna", "mediumorchid", "cadetblue", "orangered",
                    "mediumblue", "darkslategray", "mediumturquoise", "darkred", "rosybrown", "mediumvioletred",
                    "deepskyblue", "saddlebrown"])


_, ax = plt.subplots(figsize=(8, 5))

f_scores = np.linspace(0.2, 0.8, num=4)
lines, labels = [], []
for f_score in f_scores:
    x = np.linspace(0.01, 1)
    y = f_score * x / (2 * x - f_score)
    (l,) = plt.plot(x[y >= 0], y[y >= 0], color="green", alpha=0.2)
    plt.annotate("f1={0:0.1f}".format(f_score), xy=(0.9, y[45] + 0.02))

display = PrecisionRecallDisplay(
    recall=recall["micro"],
    precision=precision["micro"],
    # average_precision=average_precision["micro"],
)
display.plot(ax=ax, color="gold")

for i, color in zip(range(40), colors):
    display = PrecisionRecallDisplay(
        recall=recall[i],
        precision=precision[i]
        # average_precision=average_precision[i],
    )
    display.plot(ax=ax, color=color)

# add the legend for the iso-f1 curves
handles, labels = display.ax_.get_legend_handles_labels()
handles.extend([l])
labels.extend(["iso-f1 curves"])
# set the legend and the axes
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.legend(handles=handles, labels=labels, loc="best")
ax.set_title("xception")
plt.savefig("/content/drive/MyDrive/ALLOUTPUT/multipr_for_har.eps",dpi=600)
plt.show()

from sklearn.metrics import log_loss
log_loss(y_test, pred)

pred=np.argmax(pred, axis=1)
y_test=np.argmax(y_test, axis=1)

from sklearn.metrics import cohen_kappa_score
cohen_kappa_score(y_test, pred,labels=None, weights=None, sample_weight=None)

from sklearn.metrics import matthews_corrcoef
matthews_corrcoef(y_test, pred, )

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Load the .h5 model
model_h5 = load_model('/content/drive/MyDrive/Human.h5')

# Load the .tflite model
interpreter = tf.lite.Interpreter(model_path="/content/drive/MyDrive/Human.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Define image size and labels
image_size = 150
activity_labels = ['applauding', 'blowing_bubbles', 'brushing_teeth', 'cleaning_the_floor', 'climbing', 'cooking', 'cutting_trees', 'cutting_vegetables', 'drinking', 'feeding_horse', 'fishing', 'fixing_a_bike', 'fixing_a_car', 'gardening', 'holding_an_umbrella', 'jumping', 'looking_through_a_microscope', 'looking_through_a_telescope', 'phoning', 'playing_guitar', 'playing_violin', 'pouring_liquid', 'pushing_a_cart', 'reading', 'riding_a_bike', 'riding_a_horse', 'rowing_a_boat', 'running', 'shooting_an_arrow', 'smoking', 'taking_photos', 'texting_message', 'throwing_frisby', 'using_a_computer', 'walking_the_dog', 'washing_dishes', 'watching_TV', 'waving_hands', 'writing_on_a_board', 'writing_on_a_book']

# Preprocess frame for the models
def preprocess_frame(frame):
    frame = cv2.resize(frame, (image_size, image_size))
    frame = frame / 255.0  # Normalize to [0, 1]
    return np.expand_dims(frame, axis=0)

# Webcam capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess frame
    preprocessed_frame = preprocess_frame(frame)

    # Predict using the .h5 model
    predictions_h5 = model_h5.predict(preprocessed_frame)
    predicted_label_h5 = activity_labels[np.argmax(predictions_h5)]

    # Predict using the .tflite model
    interpreter.set_tensor(input_details[0]['index'], preprocessed_frame)
    interpreter.invoke()
    predictions_tflite = interpreter.get_tensor(output_details[0]['index'])
    predicted_label_tflite = activity_labels[np.argmax(predictions_tflite)]

    # Display results
    cv2.putText(frame, f'Activity H5: {predicted_label_h5}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, f'Activity TFLite: {predicted_label_tflite}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    cv2.imshow('Webcam', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


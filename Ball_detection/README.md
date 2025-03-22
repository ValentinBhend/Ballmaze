The Ball detection in being done with the YOLO11n algorithm using the user friendly Ultralytics implementation in Python. 

The current pytorch (.pt) model and exported OpenVINO model are already trained. The OpenVINO model is the folder of the other Pi scripts in this project. <br>
To train it differently or with another dataset, the whole trianing and exporting procedure is in YOLO_train_export.ipynb which can also be ran on Google Colab. 

There are currently ~2000 labeled images with a ball and another ~3000 empty images. <br>
The labeled dataset can be found at: [kaggle.com/datasets/valentinbhend/ballmaze-labeled-images](https://www.kaggle.com/datasets/valentinbhend/ballmaze-labeled-images) <br>
The labels are axis-aligned bounding boxes of the metal ball and were made using Label Studio.

from helpers import StrokeParse
from mlModule.FastPredict import FastPredict
from mlModule.Predictor23 import Predictor23
from mlModule.Predict23LSTM import Predictor23LSTM


# prediction index to Class Mapping

class_names23 = ['avatar','back','camera','cancel','checkbox','cloud','drop-down','envelope','forward','house','image','left-arrow','menu','play','plus','search','settings','share','sliders','container','squiggle','star','switch']



    

def getFasterPredictResultForFullUI(redundata, PREDICTOR, FASTPREDICT ):
    data = StrokeParse.removeDuplicates(redundata)
    features1 = PREDICTOR.parse_features(str(data))
    predict_results = FASTPREDICT.predict(features1)
    print(predict_results)
    for idx, prediction in enumerate(predict_results):
          index = prediction["classes"]  # Get the predicted class (index)
          probability = prediction["probabilities"][index]
          result = class_names23[index]
          result = result + " with probability "+ str(probability)

    return result,index

# Get Top 3 prediction on the data
def getFasterTop3Predict(data, PREDICTOR, FASTPREDICT ):
    # data = StrokeParse.removeDuplicates(redundata)
    features1 = PREDICTOR.parse_features(str(data))
    predict_results = FASTPREDICT.predict(features1)
    for idx, prediction in enumerate(predict_results):
          arr = prediction['probabilities']
          indexes = (-arr).argsort()[:3]
          result = {}
          key = 0
          for idx in indexes:
              result[str(key)] = [class_names23[idx],str(idx),"{0:.1f}".format(arr[idx] *100)]
              key = key + 1

    return result


def getFasterPredictResult(redundata, PREDICTOR, FASTPREDICT ):
    if(len(redundata)==0):
        return "Start Drawing"
    data = StrokeParse.removeDuplicates(redundata)
    features1 = PREDICTOR.parse_features(str(data))
    predict_results = FASTPREDICT.predict(features1)
    for idx, prediction in enumerate(predict_results):
          index = prediction["classes"]  # Get the predicted class (index)
          probability = prediction["probabilities"][index]
          probability = "{0:.2f}".format(probability*100)
          className = class_names23[index]
          result = "Predicted  <strong>" + className + "</strong> with probability :" + str(probability) 

    return result,index


if __name__ == "__main__":
    output_directory = r"C:\Users\sxm6202xx\Desktop\Project\Uploads\AWSWebApp\My23Records5\tb"
    export_dir = r"C:\Users\sxm6202xx\Desktop\Project\Uploads\AWSWebApp\My23Records"
    compressStroke = [[[37, 37, 37, 35, 35, 32, 32, 29, 29, 27, 27, 25, 25, 24, 24, 23, 23, 21, 21, 20, 20, 20, 20, 19, 19, 19, 19, 18, 18, 17, 17, 17, 17, 17, 17, 17, 17, 18, 18, 20, 20, 23, 23, 26, 26, 29, 29, 31, 31, 33, 33, 34, 34, 36, 36, 38, 38, 38, 38, 39], [11, 12, 12, 13, 13, 14, 14, 16, 16, 17, 17, 17, 17, 18, 18, 19, 19, 20, 20, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 28, 28, 32, 32, 34, 34, 37, 37, 40, 40, 42, 42, 44, 44, 46, 46, 47, 47, 48, 48, 49, 49, 49]]]

    PREDICTOR = Predictor23LSTM(export_dir,output_directory)
    FASTPREDICT = FastPredict(PREDICTOR.classifier,PREDICTOR.example_input_fn)

    # compressStroke,rect = StrokeParse.compressDataForFullUI(canvas_strokes)

    result, resultID = getFasterPredictResultForFullUI(compressStroke, PREDICTOR, FASTPREDICT )

    print(result, resultID)
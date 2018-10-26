网店工商信息图片文字提取
@Hypo
2018-06-18

# 1 Prerequisites
* 1.Ubuntu 18.x
* 2.Python 3.x
* 3.I3 4130 with 4GB RAM or above

# 2 Easy Installation
* 1.Copy this file to '\home'
* 2.Install xlwt
* 3.Install Tesseract
* 4.Copy Tesseract pre_train model to '/usr/share/tesseract-ocr/4.00/tessdata'
```shell
git clone https://github.com/HypoX64/TBILR
sudo apt install python3-pip
sudo pip3 install xlwt
sudo apt install tesseract-ocr
sudo cp TBILR/model/{chi_sim_best.traineddata,chi_sim_fast.traineddata} /usr/share/tesseract-ocr/4.00/tessdata/
```

# 3 Run
* 1.Copy images for testing to '天猫工商信息执照'
* 2.Run 'ocr.py':
```shell
cd TBILR
python3 ocr.py
```
# 4 Result
* 1.The result will be save as 'result.xls' & 'result_no_image_name.xls'
* 2.Cost about 25s on I7-4170mq @2.5Ghz

# 5 Detail
* 1.the number of OCR workers depend CPU ,recommend workers = (CPU Cores)/2-1,
    you can change OCR workers by "--workers".
	example:
	python3 ocr.py --workers 4
* 2.you can put testing images in file called '天猫工商信息执照' anywhere in your computer,
	but you have to change directory for seaching by "--search_dir".
	default:
	python3 ocr.py --search_dir ./
* 3.change Tesseract pre_train model to improve accuracy. recommend : chi_sim_fast
	default:
	python3 ocr.py --model chi_sim_fast
* 4.if there is no number in the images name,please run using "--sort str"

# 6 Acknowledgments
* Code based on Tesseract OCR 4.0 : https://github.com/tesseract-ocr/tesseract

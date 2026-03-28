# Multimodal-XAD
This is the official implementation of Multimodal-XAD.

## Setting：
* Clone this repo and prepare the environment.
```
git clone https://github.com/lab-sun/Multimodal-XAD.git
cd Multimodal-XAD
conda env create -f environment.yaml --name Multimodal_XAD
conda activate Multimodal_XAD
```

## Dataset
To download the nu-A2D dataset, please refers to: https://drive.google.com/drive/folders/15zQhXqRjs-KmZyCuxsfGbHiaLdpQbHst?usp=drive_link

Download all the files and then extract them into the folder of `project_root/data/trainval/`

## Usage
* Clone this repo and prepare the environment.
* Download the dataset, create the foler `data/trainval/` in the project root, and release the dataset into the `/trainval/`.
* To pretrain/train the network, use the pre_train.py/train.py.
* To obatin the prediction results: 1) download the weight and put into the folder of `weight`; 2) use the predict.py.
* The link for the weight is: https://drive.google.com/file/d/1CFvBUTZ_EL0c3NT6JJrEJPyLaLMjCAur/view?usp=drive_link

## Citation
If you found this code or dataset are useful in your research, please consider citing
```
@ARTICLE{feng2024multimodalxad,
  author={Yuchao Feng and Zhen Feng and Wei Hua and Yuxiang Sun},
  journal={IEEE Transactions on Intelligent Transportation Systems}, 
  title={Multimodal-XAD: Explainable Autonomous Driving Based on Multimodal Environment Descriptions}, 
  year={2024},
  volume={25},
  number={12},
  pages={19469-19481},
  doi={10.1109/TITS.2024.3467175}}
```

If you have any questions, pleas feel free to contact us!

Contact: yx.sun@cityu.edu.hk; yuchao.feng@connect.polyu.hk

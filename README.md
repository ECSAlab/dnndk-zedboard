# dnndk-zedboard
This repo is part of the work presented at the [6th South-East Europe Design Automation, Computer Engineering, Computer Networks and Social Media Conference (SEEDA-CECNSM 2021), Preveza, Greece, September 24th-26th 2021](https://seeda2021.uowm.gr/) and published in [IEEE Xplore](https://ieeexplore.ieee.org/document/9566259).
 
# Paper: "Workflow on CNN utilization and inference in FPGA for embedded applications"

# Citation
If you use this work in academic research, please, cite it using the following BibTeX:
```
@INPROCEEDINGS{9566259,
  author={Flamis, Georgios and Kalapothas, Stavros and Kitsos, Paris},
  booktitle={2021 6th South-East Europe Design Automation, Computer Engineering, Computer Networks and Social Media Conference (SEEDA-CECNSM)},
  title={Workflow on CNN utilization and inference in FPGA for embedded applications: 6th South-East Europe Design Automation, Computer Engineering, Computer Networks and Social Media Conference (SEEDA-CECNSM 2021)},
  year={2021},
  volume={},
  number={},
  pages={1-6},
  doi={10.1109/SEEDA-CECNSM53056.2021.9566259}
}
```

![](https://img.shields.io/github/last-commit/ECSAlab/dnndk-zedboard?style=plastic)

Table of Contents
=================

  * [Installation](#Installation)
  	* [ZedBoard SD card configuration for DNNDK](#zedboard-sd-card-configuration-for-dnndk)
	* [Host configuration for DNNDK setup and inference kernel generation](#host-configuration-for-dnndk-setup-and-inference-kernel-generation)
	* [Application build and run inference on the ZedBoard](#application-build-and-run-inference-on-the-zedboard)
  * [Citation](#citation)

# Installation
In the following steps we describe the process to setup the development enviroment.

## ZedBoard SD card configuration for DNNDK

Follow the steps below to setup the FPGA board:

1. Our work is based on ZedBoard which is a complete development kit for designers interested in exploring designs using the Xilinx Zynq®-7000 SoC (read more specs: http://zedboard.org/product/zedboard ).

<img src="https://i.imgur.com/TPmQRCm.jpg" widht="450" height="450">

2. Verify the ZedBoard boot (JP7-JP11) and MIO0 (JP6) jumpers are set to SD card mode (as described in the Hardware Users Guide https://www.zedboard.org/documentation/1521). Jumpers should be in the following position. 

![](https://i.imgur.com/VTboA8m.jpg)

3. Download the Xilinx DNNDK image file compatible for ZedBoard
https://www.xilinx.com/member/forms/download/design-license-xef.html?filename=xilinx-zedboard-dnndk3.1-image-20190812.zip.
4. Extract the image from the zip file and burn it on an SD card (8GB or higher is needed) using etcher https://www.balena.io/etcher/.
5. Connect the serial console.
6. Connect power and switch on the board.

## Host configuration for DNNDK setup and inference kernel generation

A typical computer with a x86 CPU has been used, loaded with Ubuntu 18.04 LTS. The Deep Neural Network Development Kit (DNNDK) package version 3.1 has been downloaded from the official Xilinx website (prior registration required) https://www.xilinx.com/member/forms/download/xef.html?filename=xilinx_dnndk_v3.1_190809.tar.gz. Chapter 1 of the DNNDK User Guide (UG1327 - v1.6) includes all the details required to setup the environment.

The exact version of the tools that was used for the GPU setup is shown in the table below.



| Ubuntu  18.04 LTS | GPU      | CUDA 10.0, cuDNN 7.4.1 | 2.7 | tensorflow_gpu-1.12.0-cp27-cp27mu-linux_x86_64.whl |
|-------------------|----------|------------------------|-----|----------------------------------------------------|
|                   |          |                        | 3.6 | tensorflow_gpu-1.12.0-cp36-cp36m-linux_x86_64.whl  |
|                   | CPU Only | None                   | 2.7 | tensorflow_gpu-1.12.0-cp27-cp27mu-linux_x86_64.whl |
|                   |          |                        | 3.6 | tensorflow_gpu-1.12.0-cp36-cp36m-linux_x86_64.whl  |


The CPU configuration is also possible but latency of five times longer can be met when compared with the GTX1050TI (4GB) GPU card that has been used. 

The packages can be found in folder "pkgs" under dnndk root folder. It is suggested to use Anaconda to create the environment where the selected package will be installed. Further information can be found in DNNDK User Guide (UG1327 - v1.6).
After downloading and unpacking the DNNDK package, execute the `sudo ./install.sh` command under the host_x86 folder to install the DECENT,DNNC, DDump and DLet tools on the host.

The conda environment used in this exercise is saved as yml file (decent_ecsa_lab.yml) and the environment can be created with the command  `conda env create -f decent_ecsa_lab.yml`.

The freeze model has been generated from the floating point model implementation in tensorflow and for convenience it is provided inside folder "freeze". It is suggested to visit the paper for details how to generate it from tensorflow or the tensorflow documentation.

It is also required to generate the calibration and the test images. The "generate_images.py" will do this work.

The accuracy of the freeze model can be validated with the following command:

```shell=
$ python eval_graph.py \ 
--graph ./freeze/frozen_graph.pb \
--input_node images_in \
--output_node dense_1/BiasAdd
```

The expected result is
 Top 1 accuracy with validation set: 0.9902
 Top 5 accuracy with validation set: 0.9999

The DECENT tool of DNNDK should be used next to generate the quantized model. The following command will enable this process:

```shell=
$ decent_q quantize \
--input_frozen_graph ./freeze/frozen_graph.pb \
--input_nodes images_in \
--output_nodes dense_1/BiasAdd \
--input_shapes ?,28,28,1 \
--input_fn graph_input_fn.calib_input \
--output_dir _quant
```

The process may take some time to finish. Once quantization is completed, summary will be displayed, like the one below:

```console=
INFO: Checking Float Graph...
INFO: Float Graph Check Done.
INFO: Calibrating for 100 iterations...
100% (100 of 100) |############| Elapsed Time: 0:00:13 Time:  0:00:13
INFO: Calibration Done.
INFO: Generating Deploy Model...
INFO: Deploy Model Generated.
*********** Quantization Summary **************      
INFO: Output:       
  quantize_eval_model:      quantize_eval_model.pb
  deploy_model:                    deploy_model.pb
```  

At this point, it is suggested to validate the accuracy of the quantized model  using the command:

```shell=
$ python eval_graph.py \
--graph ./_quant/quantize_eval_model.pb \
--input_node images_in \
--output_node dense_1/BiasAdd
```

And the expected results should be
 Top 1 accuracy with validation set: 0.9904
 Top 5 accuracy with validation set: 0.9999

The DNNC tool from DNNDK is used to deploy the inference kernel for the ZedBoard. The following command is used:

```shell=
dnnc-dpu1.4.0 \
--parser=tensorflow \
--frozen_pb=_quant/deploy_model.pb \
--dcf=zedboard.dcf \
--cpu_arch=arm32 \
--output_dir=_deploy \
--net_name=mnist \
--save_kernel \
--mode=normal
```

For simplicity, the Zedboard.dcf file is provided. Alternatively, it can be generated with the DLet tool from DNNDK, using the hardware hand-off (.hwh) file from the vivado project.

The generated inference kernel will be stored in "_deploy" folder in .elf file.

## Application build and run inference on the ZedBoard

Transfer to Zedboard the contents of the folder "mnist_zedboard_inference" via FTP.

Step 1: Install the application via "install.sh"\
Step 2: Build the model using the Makefile in samples/mnist\
Step 3: Run the generated executable to collect the result as mentioned in the paper

###### tags: `fpga` `dnndk` `zedboard`

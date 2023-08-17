# Classify_DDoS
## Prerequist
* Download the unsw-nb15 dataset(csv)
* install requirment in `requirments.txt`
    ```
    python3 -m pip install -r requirments.txt
    ```
* Installed the P4 studio SDE 9.9.0
## Machine Learning Usage
* In ML directory
    ```
    usage: main.py [-h] [-a {randomforest,decisiontree,ridge,pass}] [-p DATASET_PATH] [-t TREE_NUMBER]
                   [-d [DEPTHS [DEPTHS ...]]] [-n TRAINING_TIMES] [-s STRATIFY] [-m {B,M,None}] [-f {all,DM,EC}]
                   [-S {ML,Entry}]

    optional arguments:
      -h, --help            show this help message and exit
      -a {randomforest,decisiontree,ridge,pass}, --algorithm {randomforest,decisiontree,ridge,pass}
                            choose a algorithm to train
      -p DATASET_PATH, --dataset-path DATASET_PATH
      -t TREE_NUMBER, --tree-number TREE_NUMBER
                            how many trees will the randomforest use
      -d [DEPTHS [DEPTHS ...]], --depths [DEPTHS [DEPTHS ...]]
                            the depth of trees
      -n TRAINING_TIMES, --training-times TRAINING_TIMES
                            how many times each algorithm classify
      -s STRATIFY, --stratify STRATIFY
                            split train/test more balance
      -m {B,M,None}, --binary-or-multi {B,M,None}
                            y is binary or multiple
      -f {all,DM,EC}, --features-use {all,DM,EC}
                            Feature scheme to use
      -S {ML,Entry}, --get-score {ML,Entry}
                            Print the ML score or entry count
    ```
* Example
    > Assume `UNSW-NB15_1.csv` is in `~/`
    ```
    python3 main.py -p ~/ -d 5 10 15 20 25 30 -n 5 -f DM -S ML
    python3 main.py -n 1 -f EC -S Entry
    ```
    
## P4 Usage
* Put the script in p4src/planter/build directory and run it
    ```
    mkdir p4src/planter/build
    cp generate_makefile.sh p4src/planter/build/
    cd p4src/planter/build
    sh generate_makefile.sh planter planter.p4
    ```
* compile and install
    ```
    make & make install
    ```
* run on PC
* First Terminal
    ```
    cd $SDE
    ./run_tofino_model.sh --arch tofino -p planter
    ```
* Second Terminal
    ```
    cd $SDE
    ./run_switchd.sh --arch tofino -p planter
    ```
* Third Terminal
    ```
    cd controller
    sh run_controller.sh planter.py
    cd $SDE
    ./run_p4_tests.sh --arch tofino -p planter -t /path/to/this/project/test/
    ```

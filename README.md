# FRC Nifty Assignment

## Description
After completing this [nifty assignment](http://nifty.stanford.edu/) inspired by [Idziorek et al.'s Detecting fraudulent use of cloud resources](https://dl.acm.org/doi/10.1145/2046660.2046676), undergraduate students will achieve the following learning objectives:

1. Identify common threats to cloud infrastructure, including flash crowds, Distributed Denial of Service (DDoS) attacks, and Fraudulent Resource Consumption (FRC) attacks.
2. Analyze network logs to detect patterns indicative of security threats.
3. Visualize website traffic data to gain insights into potential security incidents.
4. Develop algorithms to detect and differentiate between different types of security threats in cloud environments.
5. Understand the financial implications of security threats on cloud environments.

In a publicly available [Canvas assignment](https://canvas.instructure.com/enroll/67KLBL), students will follow the story of Alex, a cloud engineer working on a e-commerice platform at Swift Mart, as he tackles 4 cloud security challenges.

## Repository Contents
The GitHub Repository contains all necessary files to synthetically generate baseline, flash crowd, DDoS attack, and FRC attack data using [NASA server web logs from Jully 1995](https://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html). The generated data, sample code, output, and visualizations are also provided for each of the 4 challanges in the assignment. The data generation and sample code for the challenges is written in Python, altough the challenges can be performed in any software or programming language.


An overview of the main files will be provided below:
* NASA_access_log_Jul95.gz: This compressed file contains the original NASA server logs. This data will be used as a starting point to create datasets for each challenge.
* generate_data.py: This Python file takes the original NASA server logs as an input and creates 4 CSV files that are saved into baseline, flash crowd, DDoS attack, and FRC folders. 
* Challenge folders: There are 4 folders for each of the challenges in the project. Each folder contains a CSV file created by generate_data.py, a Python file to process the data to answer the questions in each challenge, and 1 or more images that visualize the synthetically generated data.
* requirements.txt: This contains a listof Python libraries required to run the project. See the "Installation and Usage" for more details.
* frc-nifty-assignment-export.imscc: The Cavnas assignment is also exported and included in the repository.

For the assignment, only the synthetically  generated web logs are provided to the students.

## Installation and Usage
- Use of virtual environment to make sure consistent. Done in Python, but this project can be adapted for any software or programming lanauge. Instructions will be for Python
- Data generation and sample code is provided using Python, although the sample code can be done in any software or programming lanauge that can visualize data and process large amounts of data. Instructions are provided below to set up the Python environment to regenerate data, modify the provided data sets, and run the sample code for each challenege.

### Prerequisites
Python 3.9.0+

pip

git

### Setup
1. Clone the GitHub Repository
* Open a terminal window and navigate to a directory where the project will be created.
* Run the following command to clone the repository:
```bash
git clone https://github.com/cobyrem/cloud-security-nifty-assignment.git
```
* A folder titled cloud-security-nifty-assignment should now be created in the current directory and contains all of the files from the repository.

2. Create a Virtual Envrionment
* A virtual environment will be created to self-contain any dependencies for the project.
* In the terminal window, navigate inside the cloud-security-nifty-assignment folder.
* Run the following command to create the virtual environment:
```bash
python3 -m venv virtual-env
```
* A virtual environment called "virtual-env" should now be created.

3. Activate the Virtual Environment
* The virtual envrionment has been created, but is not being used. 
* Run the following command to activate the virtual environment:
```bash
source virtual-env/bin/activate
```
* The virtual envrionment is now being used. "(virtual-env)" should now be visible before the terminal prompt.

4. Install Dependencies
* Run the following command to install the required dependencies in the virtual environment:
```bash
pip install -r requirements.txt
```
* The project's depedencies will now be installed.

5. Deactivate the Virtual Environment
* After using the project, run the following command to deactivate the virtual environment:
```bash
deactivate
```

### Usage
Once the virtual environment has been activated, the Python code can be run to generate data, visualize the network traffic, and answers questions in the assignment. The input terminal commands, terminal output, and file output will be provided below. The commands below are exectued from the base cloud-security-nifty-assignment folder.

1. Generate Data
Terminal Input:
```bash
python3 generate_data.py
```

No Terminal Output

File Output:
* baseline/baseline.csv
* flash_crowd/flash_crowd.csv
* ddos/ddos.csv
* frc/frc.csv

2. Baseline Challenge
Terminal Input:
```bash
python3 baseline/baseline_challenge.py
```

Terminal Output:
```
The maximum requests per second in baseline traffic is 9  
```

File Output:
* baseline/baseline.png

3. Flash Crowd Challenge
Terminal Input:
```bash
python3 flash_crowd_challenge.py
```

Terminal Output:
```
The maximum requests per second in the flash crowd is 67
Flash crowd at or above 50 requests/second detected at 2023-07-03 10:14:14
```

File Output:
* flash_crowd/flash_crowd.png

4. DDoS Attack Challenge
Terminal Input:
```bash
python3 ddos/ddos_challenge.py
```

Terminal Output:
```
The maximum requests per second in the flash crowd is 65                                                                                                                                               
Running flash crowd detection algorithm but with DDoS data.                   
Flash crowd at or above 50 requests/second detected at 2023-07-10 06:44:40                                                                                                 
DDoS attack was detected as a flash crowd                                                                                                                                                              
DDoS attack at or above 10 requests/client detected at 2023-07-10 06:41:00
Flash crowd or DDoS attack not detected at 10 requests/client. Use the original script to detect flash crowds
```

File Output:
* ddos/ddos.png
* ddos/flash_crowd_client.png
* ddos/ddos_client.png

5. FRC Attack Challenege
Terminal Input:
```bash
python3 frc/frc_challenge.py
```

Terminal Output:
```
The maximum requests per second in the flash crowd is 28
Baseline Scenario Cost: $17.50
FRC Attack Scenario 1 Cost: $157.46
FRC Attack Scenario 2 Cost: $157.46
```

File Output:
* frc/frc.png

### Sign up for the assignment

Students can sign up for the FRC Nifty Assignment using the following link:
https://canvas.instructure.com/enroll/67KLBL

The template for the assignment on Canvas Commons by searching for "FRC Nifty Assignment"

\# Lab 1 - Git/DVC and Data Preparation



\## Question 1



\*\*Observe the files created by "uv init". What do you think they contain?\*\*



After running "uv init", it created the basic structure of the Python project.



\- "src/" is where the Python source code of the project will be written.

\- ".python-version" specifies the Python version used by the project.

\- "pyproject.toml" contains information about the project and its dependencies.

\- "README.md" is used to document and explain the project.



\## Question 2



\*\*What are the created files? What do you think they are used for? And which ones should be pushed to Git?\*\*



After running "dvc init", DVC created a ".dvc" folder and a ".dvcignore" file.



\- ".dvc/config" contains the DVC project configuration.

\- ".dvc/.gitignore" tells Git which local DVC files should not be tracked.

\- ".dvc/tmp/" contains temporary files used by DVC.

\- ".dvcignore" tells DVC which files or folders it should ignore.



The ".dvc/config", ".dvc/.gitignore", and ".dvcignore" files should be pushed to Git. Temporary files such as ".dvc/tmp/" should stay local.






\## Question 3



\*\*Where are the credentials stored? And what are the options other than "--global"? Should the credentials be pushed to GitHub?\*\*



Because "--global" was used, the credentials are stored in the global DVC configuration on the local computer.



Other options are "--local", which stores the configuration only for the current project, "--system", which stores it at the system level, or using no option to store normal project configuration in ".dvc/config".



Credentials should not be pushed to GitHub because they contain sensitive information such as the username and access token.







\## Question 4



\*\*Take a look at the ".gitignore" file. Explain what happened.\*\*



After running "dvc add data", DVC added "/data" to the ".gitignore" file. This prevents Git from tracking the actual dataset because the data is managed by DVC instead.









\## Question 5



\*\*Do you see a ".dvc" file? What does it contain?\*\*



Yes, a "data.dvc" file was created. It does not contain the dataset itself. It contains information that DVC uses to track the data, such as the hash of the data, its size, the number of files, and the path to the tracked folder.



At the first "dvc add", it tracked 16643 files. Later, after reducing the dataset for the lab and creating the processed datasets, the current version tracks 99 files.







\## Question 6



On GitHub, the actual dataset is not stored in the repository. Instead, GitHub contains the "data.dvc" pointer file that describes the tracked data.



The "data" folder itself is ignored by Git using ".gitignore".



On DagsHub, the data can be viewed through the DVC integration. I can see the "food11\_raw" folder with the "training", "evaluation", and "validation" folders and their images.



The project code is stored on GitHub, while the actual dataset is managed by DVC and stored through DagsHub.







\## Question 7



After cloning the GitHub repository in a new folder, the "data" folder was not there because Git only cloned the DVC pointer file.



To download the actual dataset, I used:



"dvc pull"



After that, the "data" folder was restored with the "training", "evaluation", and "validation" folders.













\## Question 8



No. After checking out the older Git commit and running "dvc checkout", the new "food11\_processed" and "food11\_processed\_mini" folders were no longer there. Only the older "food11\_raw" data remained.



After returning to "main" and running "dvc checkout" again, the processed folders appeared again.






















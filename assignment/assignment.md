Minerva Logo

Carl Vincent

CK
Edit Profile
The Hub
Logout

Help Topics
Report a Bug
Live Tech Support
System Check
Suggest a Feature
CS156 - Pipeline - First Draft
You have three classes today and nothing due.
Home
Assignments
Class Assessments
Outcome Index
Courses
CP193.025 - Watson, TH@1:00PM UTC
CS156 - Watson, MW@11:00PM UTC
CS162 - Subasic, MW@3:00PM UTC
CS162 - Subasic, TTH@3:00PM UTC
GL97 - Lindo, T@2:00AM UTC
IL181.006 - Watson, M@1:00PM UTC
Past Courses
Grading
Absences
All Events
CS156 > Watson, MW@11:00PM UTC > Pipeline - First Draft
Assignment due Sunday, October 19, 2025 by 7:00am
Late submissions will not be accepted after Wednesday, October 22, 2025 at 7:00am
General ML Assignment Instructions: All three assignments involve the same core task: create a machine learning pipeline that analyzes data from your own digital archive. I want you to use the ML models and techniques we learn in class to look for interesting patterns in photos, social media, videos, text, location data, or other any other data you've created, collected, or accessed in your life so far. This data should be personal, but not private—things you feel comfortable sharing with peers and colleagues in a professional settings, such as holiday photos, old assignments, or music files. It's sometimes ok to augment your data with other sources, but pre-processing is part of the assignment.

​

​

Assignments are due immediately after each break. (Fall: Fall Break, Friendsgiving, Finals. Spring: Spring Break, Quinquatria, and Finals). However, some of the components of each pipeline are often due as PCW in the week before the break. Each assignment involves building an end-to-end machine learning pipeline that explores and presents an interesting insight about your own personal data. This should be formatted as a single jupyter notebook with markdown cells **explaining each step. **

​

**The final deliverable is a jupyter notebook exported as a PDF. Other formats will not be evaluated. Do not upload a zip. Do not upload multiple documents. Do not upload a raw .ipynb. Upload a polished final report in PDF format.**

​

The notebook should include the following elements:

Students will need to select a sample of the digital data they have accumulated in their life so far. This might include images, sound files, text, geospatial, or numerical data.
The first section of the notebook should explain the data: what is included, how it was obtained, and all important details about how it was sampled from the student's own digital archive.
The second section of the notebook should contain well-commented code for converting this data to python readable format (and scikit-learn) and loading this data into an appropriate data structure (np.array, pandas dataframe, glob etc.).
The third section of the notebook should include a markdown section explaining any necessary cleaning, pre-processing, and feature engineering the data requires, and a include a code block completing these steps. You should also perform some basic exploratory data analysis at this point reporting and visualizing the samples and computing appropriate descriptive statistics.
The fourth section should include a markdown section discussing the analysis (classification, regression, or clustering) that will be conducted on the data, along with well commented code block performs any necessary data splits (such as creating training and test sets)
The fifth section should discuss model** selection** in a markdown section and include model initialization and construction in a well-commented code block. This section should include a clear discussion of the model's mathematical underpinnings. This should include typeset equations and/or algorithms as pseudocode.
The sixth section_ _should train the model, including code and explanations for necessary cross validation or hyperparameter tuning.
The seventh section should contain code to generate predictions for out of sample data, and compute appropriate performance** metrics.**
The eighth section_ _should visualize the results and discuss your conclusions.
The ninth section should be an executive summary of the prior eight sections, clearly explaining your steps, diagramming your pipeline, visualizing any key results, and explaining any key insights or shortcomings of your approach. You may wish to include a discussion of how the model might be improved.
The tenth section should contain references for documents, guides, or code repos you accessed for the project.
This is a rough visualization of the elements your notebook should contain:



Please be sure to run all code and save all output (you may wish to suppress especially verbose outputs from training steps if they take up multiple pages with something like logging.config(logging.info(critical)). Be sure to read your work before you submit, edit your writing, and think through how to present your work most clearly with diagrams, #dataviz, and section headers.

​

Export the full notebook with all output as a pdf and upload it. If you wish to include supplementary code or data, please include these as a link to a public GitHub.

​

Assignment 1:

In this first assignment, you'll build a simple pipeline based on data from your personal archive. While this is open ended, for the first assignment I recommend choosing something simple. You'l have chances to be more creative in the second and third assignments. Here are a few examples:

​

Images--Build a logistic regression to classify photos taken in SF vs. Seoul.
Text--Build a naïve Bayes classifier to classify assignments from different classes.
Audio--Use a neural network to classify music genres.
Example Assignment

​

Tips:

​

Data ingestion is the most difficult part of the first assignment, you'll probably have to search for guides on how to ingest the particular data type that you choose and much of your time will be spent flexing that data into a format readable by the model. This is worth doing, as you'll need to do something similar for future projects and you'll be able to re-use some of your code and all of your expertise.
​

It is important to approach this assignment as a work of personal creative expression. There are no "right" and "wrong" answers, only compelling or confusing ones. You're being evaluated in part on whether you can select something interesting and worth exploring from the ambiguous repository of your own data.
​

​


Assignment Information
Length:
1500
Weight:
8%
Learning Outcomes Added
cs156-MLCode: Produce working, readable, and performant Python implementations of a variety of machine learning systems using appropriate libraries and software tools.

cs156-MLExplaination: Clearly articulate machine learning systems, algorithms, and techniques using appropriate oral and written descriptions, mathematical notation, and visualizations.

cs156-MLFlexibility: Reason flexibly, apply information in new contexts, produce novel work, and articulate meta-knowledge about machine learning.

cs156-MLMath: Evaluate problems and derive solutions in linear algebra, multivariate calculus, and Bayesian statistics.

Submit

Your submission has not yet been submitted or finalized.
Submit
© Copyright 2025 Minerva Project, Inc. All rights reserved. Privacy Policy Terms
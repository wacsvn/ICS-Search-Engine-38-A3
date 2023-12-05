# IR23F-38-A3-M1
Group Members
-------------------------
Adam Ho, adamh7, 93172696

Bryan Barcelo, barceloo, 20059593

Jett Spitzer, jlspitze, 44184334

Varun Ruddaraju , vruddara, 95283007


ABOUT
-------------------------
Minimum analytics: The number of indexed documents; The number of unique words; The total size (in KB) of your index on disk.
...

HOW TO USE
-------------------------
There are four python files for our code. The first step is to add the corpus zip file into the folder.
Next, in the main method, on line 20 where it says jsonReader = JSONZipReader("developer.zip"), replace "developer.zip" with
the name of you zip file. Make sure to import all packages used in each file. Another note is there is a variable in Main.py called reindex in the main method.
That variable is default set to True which will reindex the program and allow you to search. For any reasons after running the program one time, you choose to 
search again after ending the program, you can set reindex to False and run the program again without having to reindex all the files. 
Finally, you can run the indexer by running the 
Main.py file. At this point, the program will start to index the zip file. Once a local GUI Window pops that means the indexing is over with
and now you can search queries. There is a bar where you can enter you query. After you are done typing your query out, you can press the search bar on the right to display the query results.
The results will be displayed in the results box ranked in order from best(top) to worst(bottom). You can keep typing as many queries as you want while on your the window. Finally, you can minimize 
the GUI and the python console should display both the query search time as well as the count of the result-set of that query. 

# Digital folder
This project represents a simple digital folder created with PyQt5. With this application, you can create multiple digital folders and save them to a local database. 
The digital folder can be created with different registers under which you can save files. The actual file is not stored in the database, just the path to it. The application allows you to view the contents of the files in the GUI. So far `.pdf`-, `.doc`-, `.docx`-, `.xls`-, `.xlsx`- files are supported.

When creating a new folder or make changes to an existign the folder, you have to save the changes so that they are updated in the database.

The visualisation of the register cards can be changed. Therefor you can change the existing `html` files in the `register layout` folder or add new `html` files to the folder.

In order to run the application, copy the repository to a new folder and run the `main.py` file.

## Exe-file
You can also create your own exe-file. To do this, you need to install the `pyinstaller` package and the used packages stated in `requirements.txt`. Then run the following command in the terminal from your local folder:
```bash 
py -m PyInstaller main_onefile.spec
```

In the `spec` file you need to correct the path to the `config.ini` file.
The exe-file will be created in the `dist` folder.

In the `spec` file, you can, for example, change the icon of the application and the name of the exe-file.

## Note
The application only works on Windows, as the `QAxWidget` does not work on other operating systems. 

The application is still under development. Feedback and suggestions are welcome.

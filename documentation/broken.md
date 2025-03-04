# Fragments of Tutorials That Do Not Work

## Setup Tutorial: Flask and Gunicorn Section

## Docker With Flask Tutorial: Auto-Updates

### Updating The Application

* Sometimes changes will need to be made to the application
  * For example, installing new requirements, updating the Docker container, or HTMl and logic changes
* Python *autoreloading* watches the entire file system for changes and refreshes the application when it detects a
change
* Autoreloading is discouraged in production because it can become resource intensive very quickly
* `touch-reload` can be used to watch for changes to a particular file and reload when the file is updated or replaced
* To implement, start by opening the `uwsgi.ini` file:

```shell
sudo nano uwsgi.ini
```

* At the end of the file, add the following line:

`/var/www/yaggydev/uwsgi.ini`:

```ini
...
touch-reload = /app/uwsgi.ini
```

* This specifies a file that will be modified to trigger an entire application reload
* To demonstrate, make a small change to the application
* Open the `app/views.py` file:

```shell
sudo nano app/views.py
```

* Replace the string returned by the `home` function from `return "hello world!"` to the following:

```python
from flask import render_template
from app import app

@app.route('/')
def home():
    return "<b>There has been a change</b>"

@app.route('/template')
def template():
    return render_template('home.html')
```

* When opening the application homepage at `http://ip-address:56733`, the change will not yet be visible
* This is because the condition for a reload is a change to the `uwsgi.ini` file
* To reload the application, use `touch` to activate the condition:

```shell
sudo touch uwsgi.ini
```

* Now reload the application homepage in the browser again
* The application should have incorporated the changes